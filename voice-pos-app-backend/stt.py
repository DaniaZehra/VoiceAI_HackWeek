from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import db.models as models
from db.database import SessionLocal, engine
from datetime import date
from decimal import Decimal
import uuid
import os
import re
from typing import Optional, Union
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
def test_db(db: Session = Depends(get_db)):
    try:
        return {"message": "Database connected"}
    except Exception as e:
        return {"message": "Database connection not available", "error": str(e)}

API_URL = "https://api.upliftai.org/v1/transcribe/speech-to-text"
API_KEY = "sk_api_e96abf4d0ddb84d1f142b22fb37cccee645cda84c7c4a5d9b509671d5ee67273"

DATABASE_URL = "postgresql://postgres:tILHebFZFIqqlZcxmsFMgcxMcsRkTZfj@yamanote.proxy.rlwy.net:46383/railway?sslmode=require"


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
# Inventory Helpers (psycopg)
# -------------------
def _connect_db():
    try:
        conn = psycopg.connect(
            host="yamanote.proxy.rlwy.net",
            port="46383",
            dbname="railway",
            user="postgres",
            password="tILHebFZFIqqlZcxmsFMgcxMcsRkTZfj",
            sslmode="require"
        )
        print("psycopg connected (inside function)")
        return conn
    except Exception as e:
        print("psycopg failed inside function:", e)
        return None

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

def _update_inventory(product_name: str, delta: int):
    conn = _connect_db()
    if conn is None:
        return False, "ڈیٹا بیس کنکشن دستیاب نہیں۔", None
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE inventory
                    SET stock_level = stock_level + %s, updated_at = NOW()
                    WHERE lower(product_name) = lower(%s)
                    RETURNING stock_level;
                    """,
                    (delta, product_name),
                )
                row = cur.fetchone()
                if not row:
                    return False, "پروڈکٹ نہیں ملی۔", None
                return True, "OK", row[0]
    except Exception as e:
        return False, f"خرابی: {e}", None
    finally:
        conn.close()

def _fetch_inventory(product_name: str | None = None):
    conn = _connect_db()
    if conn is None:
        return False, "ڈیٹا بیس کنکشن دستیاب نہیں۔", None
    try:
        with conn:
            with conn.cursor() as cur:
                if product_name:
                    cur.execute(
                        "SELECT id, product_name, stock_level, updated_at FROM inventory WHERE lower(product_name)=lower(%s)",
                        (product_name,)
                    )
                    row = cur.fetchone()
                    if not row:
                        return True, "پروڈکٹ نہیں ملی۔", None
                    return True, "OK", {
                        "id": str(row[0]),
                        "product_name": row[1],
                        "stock_level": row[2],
                        "updated_at": row[3].isoformat() if row[3] else None,
                    }
                else:
                    cur.execute(
                        "SELECT id, product_name, stock_level, updated_at FROM inventory ORDER BY product_name"
                    )
                    rows = cur.fetchall()
                    return True, "OK", [
                        {
                            "id": str(r[0]),
                            "product_name": r[1],
                            "stock_level": r[2],
                            "updated_at": r[3].isoformat() if r[3] else None,
                        }
                        for r in rows
                    ]
    except Exception as e:
        return False, f"خرابی: {e}", None
    finally:
        conn.close()

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
        ok, msg, level = _update_inventory(product, -qty)
        new_stock_level = level
        message = f"{product} کا اسٹاک {qty} کم کر دیا گیا۔ نیا اسٹاک: {level}" if ok else msg
    elif product and _should_increase(text):
        ok, msg, level = _update_inventory(product, qty)
        new_stock_level = level
        message = f"{product} کا اسٹاک {qty} بڑھا دیا گیا۔ نیا اسٹاک: {level}" if ok else msg
    elif _is_stock_query(text):
        ok, msg, inv = _fetch_inventory(product)
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
async def get_inventory_all():
    ok, msg, items = _fetch_inventory(None)
    if not ok:
        raise HTTPException(status_code=500, detail=msg)
    return {"items": items}

@app.get("/inventory/{product}")
async def get_inventory_product(product: str):
    mapped = URDU_PRODUCT_MAP.get(product, product)
    ok, msg, item = _fetch_inventory(mapped)
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