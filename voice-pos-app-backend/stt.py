from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import db.models as models
from db.database import SessionLocal, engine, DATABASE_URL
from datetime import date
from decimal import Decimal
import uuid
import os
import re
from typing import Optional, Union
from sqlalchemy import func as sa_func
try:
    import psycopg
except Exception:
    psycopg = None

# -------------------
# Database Setup
# -------------------
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# -------------------
# FastAPI Setup
# -------------------
app = FastAPI()
from sqlalchemy import text

@app.get("/test-db")
def test_db():
    try:
        import psycopg
        conn = psycopg.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        now = cur.fetchone()[0]
        return {"message": "Connected successfully", "time": str(now)}
    except Exception as e:
        return {"message": "Connection failed", "error": str(e)}

@app.get("/healthz")
def healthz():
    try:
        import psycopg
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                one = cur.fetchone()[0]
        return {"ok": True, "db": True, "select1": one}
    except Exception as e:
        return {"ok": False, "db": False, "error": str(e)}

API_URL = "https://api.upliftai.org/v1/transcribe/speech-to-text"
API_KEY = "sk_api_e96abf4d0ddb84d1f142b22fb37cccee645cda84c7c4a5d9b509671d5ee67273"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# Helpers
# -------------------
def safe_value(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value

def to_float(value):
    if isinstance(value, uuid.UUID):
        return str(value)
    elif isinstance(value, Decimal):
        return float(value)
    else:
        return value

# -------------------
# Urdu Helpers
# -------------------
URDU_PRODUCT_MAP = {
    "ایپل": "Apple",
    "سیب": "Apple",
    "banana": "Banana",
    "کیلا": "Banana",
    "دودھ": "Milk",
    "ملک": "Milk",
    "اورنج": "Orange",
    "سنگترہ": "Orange",
    "مالٹا": "Orange",
    "بریڈ": "Bread",
    "روٹی": "Bread",
    "انڈے": "Eggs",
    "انڈا": "Eggs",
    "مکھن": "Butter",
    "پنیر": "Cheese",
    "چیز": "Cheese",
    "چینی": "Sugar",
    "شکر": "Sugar",
    "چائے": "Tea",
}

URDU_NUM_MAP = {
    "صفر": 0, "ایک": 1, "دو": 2, "تین": 3, "چار": 4, "پانچ": 5,
    "چھ": 6, "سات": 7, "آٹھ": 8, "نو": 9, "دس": 10, "گیارہ": 11,
    "بارہ": 12, "تیرہ": 13, "چودہ": 14, "پندرہ": 15, "سولہ": 16,
    "سترہ": 17, "اٹھارہ": 18, "انیس": 19, "بیس": 20, "تیس": 30,
    "چالیس": 40, "پچاس": 50, "ساٹھ": 60, "ستر": 70, "اسی": 80,
    "نوے": 90, "سو": 100
}

def parse_urdu_number(text: str) -> float:
    numbers = re.findall(r'\d+', text)
    if numbers:
        return float(numbers[0])
    units = URDU_NUM_MAP
    multipliers = {"ہزار": 1000, "لاکھ": 100000}
    words = text.split()
    total = 0
    current = 0
    for w in words:
        if w in units:
            current += units[w]
        elif w in multipliers:
            if current == 0:
                current = 1
            current *= multipliers[w]
            total += current
            current = 0
    return float(total + current)

# -------------------
# Sales Report
# -------------------
def generate_daily_sales_report(db: Session):
    today = date.today()
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.created_at >= today)
        .all()
    )
    total_sales = sum(to_float(tx.total_amount) for tx in transactions)
    payment_breakdown = {}
    for tx in transactions:
        method = tx.payment_method or "unknown"
        payment_breakdown[method] = payment_breakdown.get(method, 0) + to_float(tx.total_amount)
    report = {
        "date": str(today),
        "total_transactions": len(transactions),
        "total_sales": total_sales,
        "payment_breakdown": payment_breakdown,
        "transactions": [
            {
                "id": safe_value(tx.id),
                "description": tx.description,
                "amount": safe_value(tx.total_amount),
                "payment_method": tx.payment_method,
                "created_at": safe_value(tx.created_at),
            }
            for tx in transactions
        ],
    }
    return report

# -------------------
# Inventory Helpers (SQLAlchemy)
# -------------------
import os

def _parse_quantity(text: str) -> int:
    m = re.search(r"(\d{1,4})", text)
    if m:
        try:
            return int(m.group(1))
        except:
            pass
    total = 0
    for token in text.split():
        token = token.strip()
        if token in URDU_NUM_MAP:
            total += URDU_NUM_MAP[token]
    return total if total > 0 else 1

def _parse_product(text: str) -> str | None:
    for ur, en in URDU_PRODUCT_MAP.items():
        if ur in text:
            return en
    for name in URDU_PRODUCT_MAP.values():
        if name.lower() in text:
            return name
    return None

def _should_decrease(text: str) -> bool:
    patterns = ["اسٹاک کم", "کم کریں", "کم کرو", "کم کر", "گھٹا", "minus", "مائنس"]
    return any(p in text for p in patterns)

def _should_increase(text: str) -> bool:
    patterns = ["بڑھا", "اضافہ", "+", "پلس", "increase"]
    return any(p in text for p in patterns)

def _is_stock_query(text: str) -> bool:
    patterns = ["اسٹاک کیا", "اسٹاک لیول", "کتنا اسٹاک", "تمام اسٹاک", "inventory", "دکھاؤ", "بتاؤ"]
    return any(p in text for p in patterns)

def _update_inventory(db: Session, product_name: str, delta: int):
    item = (
        db.query(models.Inventory)
        .filter(sa_func.lower(models.Inventory.product_name) == sa_func.lower(product_name))
        .one_or_none()
    )
    if not item:
        return False, "پروڈکٹ نہیں ملی۔", None
    item.stock_level = (item.stock_level or 0) + int(delta)
    db.add(item)
    db.commit()
    db.refresh(item)
    return True, "OK", item.stock_level

def _fetch_inventory(db: Session, product_name: str | None = None):
    if product_name:
        item = (
            db.query(models.Inventory)
            .filter(sa_func.lower(models.Inventory.product_name) == sa_func.lower(product_name))
            .one_or_none()
        )
        if not item:
            return True, "پروڈکٹ نہیں ملی۔", None
        return True, "OK", {
            "id": str(item.id),
            "product_name": item.product_name,
            "stock_level": item.stock_level,
            "updated_at": safe_value(item.updated_at),
        }
    items = (
        db.query(models.Inventory)
        .order_by(models.Inventory.product_name)
        .all()
    )
    return True, "OK", [
        {
            "id": str(i.id),
            "product_name": i.product_name,
            "stock_level": i.stock_level,
            "updated_at": safe_value(i.updated_at),
        }
        for i in items
    ]

# -------------------
# Voice Command API
# -------------------
@app.post("/voice-command")
async def voice_command(file: UploadFile = File(...), db: Session = Depends(get_db)):
    files = {"file": (file.filename, file.file, file.content_type)}
    data = {"model": "scribe", "language": "ur", "domain": "phone-commerce"}
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post(API_URL, headers=headers, files=files, data=data)
    result = response.json()
    text = result.get("transcript", "").lower()

    message = None
    new_stock_level = None
    inv = None
    product = _parse_product(text)
    qty = _parse_quantity(text)

    # Inventory Commands
    if product and _should_decrease(text):
        ok, msg, level = _update_inventory(db, product, -qty)
        new_stock_level = level
        message = f"{product} کا اسٹاک {qty} کم کر دیا گیا۔ نیا اسٹاک: {level}" if ok else msg
    elif product and _should_increase(text):
        ok, msg, level = _update_inventory(db, product, qty)
        new_stock_level = level
        message = f"{product} کا اسٹاک {qty} بڑھا دیا گیا۔ نیا اسٹاک: {level}" if ok else msg
    elif _is_stock_query(text):
        ok, msg, inv = _fetch_inventory(db, product)
        message = "اسٹاک کی معلومات" if ok else msg


    # Billing & Sales Commands
    elif "خریداری" in text or "سیلز" in text:
        message = generate_daily_sales_report(db)
    elif "پروڈکٹ" in text:
        message = "پروڈکٹ لسٹ دکھا رہا ہوں (dummy data)"
    elif "بل" in text:
        description = "Voice-generated bill"
        total_amount = parse_urdu_number(text) or 100.0
        if "کیَش" in text or "نقد" in text or "cash" in text:
            payment_method = "cash"
        elif "کارڈ" in text or "card" in text or "کریڈٹ" in text:
            payment_method = "card"
        else:
            payment_method = "unknown"

        new_tx = models.Transaction(
            description=description,
            total_amount=total_amount,
            payment_method=payment_method
        )
        db.add(new_tx)
        db.commit()
        db.refresh(new_tx)
        message = f"بل بنایا گیا: {new_tx.description}، رقم {new_tx.total_amount}، ادائیگی: {new_tx.payment_method}"
    else:
        message = f"کمانڈ سمجھ نہیں آئی: {text}"

    return {
        "transcription": text,
        "message": message,
        "product": product,
        "quantity": qty,
        "new_stock_level": new_stock_level
    }

# -------------------
# Inventory Endpoints
# -------------------
@app.get("/inventory")
async def get_inventory_all(db: Session = Depends(get_db)):
    ok, msg, items = _fetch_inventory(db, None)
    if not ok:
        raise HTTPException(status_code=500, detail=msg)
    return {"items": items}

@app.get("/inventory/{product}")
async def get_inventory_product(product: str, db: Session = Depends(get_db)):
    mapped = URDU_PRODUCT_MAP.get(product, product)
    ok, msg, item = _fetch_inventory(db, mapped)
    if not ok:
        raise HTTPException(status_code=500, detail=msg)
    if item is None:
        raise HTTPException(status_code=404, detail="پروڈکٹ نہیں ملی۔")
    return item

@app.get("/")
async def root():
    return {"message": "Welcome to the VoiceAI API POS system"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)