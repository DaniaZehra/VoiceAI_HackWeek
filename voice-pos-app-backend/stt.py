from fastapi import FastAPI, File, UploadFile, Depends
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import db.models as models
from db.database import SessionLocal, engine
from datetime import date
from fastapi.responses import JSONResponse
from decimal import Decimal
import uuid
import json

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

API_URL = "https://api.upliftai.org/v1/transcribe/speech-to-text"
API_KEY = "sk_api_e96abf4d0ddb84d1f142b22fb37cccee645cda84c7c4a5d9b509671d5ee67273"

def safe_value(value):
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, "isoformat"):  # datetime/date
            return value.isoformat()
        return value

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_daily_sales_report(db: Session):
    today = date.today()

    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.created_at >= today)
        .all()
    )

    def to_float(value):
        if isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value) 
        else: 
            return value

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



@app.post("/voice-command") 
async def voice_command(file: UploadFile = File(...), db: Session = Depends(get_db)):
    files = {"file": (file.filename, file.file, file.content_type)}
    data = {
        "model": "scribe",
        "language": "ur",
        "domain": "phone-commerce"
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    response = requests.post(API_URL, headers=headers, files=files, data=data)
    result = response.json()
    text = result.get("transcript", "").lower()

    def parse_urdu_number(text: str) -> float:
        units = {
            "صفر": 0, "ایک": 1, "دو": 2, "تین": 3, "چار": 4, "پانچ": 5,
            "چھ": 6, "سات": 7, "آٹھ": 8, "نو": 9, "دس": 10,
            "گیارہ": 11, "بارہ": 12, "تیرا": 13, "چودہ": 14, "پندرہ": 15, "سولہ": 16, "سترہ": 17, "اٹھارہ": 18, "انیس": 19,
            "بیس": 20, "تیس": 30, "چالیس": 40, "پچاس": 50, "ساٹھ": 60, "ستر": 70, "اسی": 80, "نوے": 90,
        }
        multipliers = {"سو": 100, "ہزار": 1000, "لاکھ": 100000}

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
    
    # Simulate actions
    if "خریداری" in text:
        message = generate_daily_sales_report(db)
    elif "پروڈکٹ" in text:
        message = "پروڈکٹ لسٹ دکھا رہا ہوں (dummy data)"
    elif "بل" in text:
        description = "Voice-generated bill"

        total_amount = None
        payment_method = None

        total_amount = parse_urdu_number(text)
        if total_amount == 0:
            total_amount = 100.0

        if "کیَش" in text or "نقد" in text or "cash" in text:
            payment_method = "cash"
        elif "کارڈ" in text or "card" in text or "کریڈٹ" in text:
            payment_method = "card"
        else:
            payment_method = "unknown"

        if total_amount is None:
            total_amount = 0.0  
        
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

    return {"transcription": text, "message": message}
    




@app.get("/")
async def root():
    return {"message": "Welcome to the VoiceAI API POS system"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)