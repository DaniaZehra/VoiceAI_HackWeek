# Voice Command POS System

This is a **FastAPI-based prototype** for a **Point of Sale (POS)** system that allows merchants to manage **sales**, **billing**, and **inventory** using simple **Urdu voice commands**.  
It uses **UpliftAI’s Speech-to-Text (STT)** API to transcribe spoken commands into text, understand the intent, and perform real actions like updating inventory or recording transactions in a PostgreSQL database.

## Features

### Voice Command Support (Urdu)
- “اسٹاک کم کریں ایپل پانچ” → Reduce **Apple** stock by 5  
- “اسٹاک بڑھائیں دودھ دس” → Increase **Milk** stock by 10  
- “ایپل کا اسٹاک کیا ہے؟” → Check **Apple** stock level  
- “تمام اسٹاک دکھاؤ” → Show full inventory  
- “بل بناؤ کیش دو سو” → Create a **cash bill** of amount 200  
- “آج کی خریداری” / “سیلز رپورٹ دکھاؤ” → Generate **daily sales report**

### Billing & Transactions
- Create new transactions (bills) using voice commands  
- Store transaction details like **description**, **amount**, and **payment method**  
- Automatically record **created_at** timestamps  
- Generate a **daily sales report** including:
  - Total sales  
  - Payment method breakdown  
  - List of transactions

### Inventory Management
- Real-time updates stored in **PostgreSQL**  
- Increase or decrease product stock by voice command  
- Retrieve all items or a single product’s stock  
- View updated stock levels immediately

### API Endpoints
| Endpoint | Description |
|----------|--------------|
| `POST /voice-command` | Process Urdu voice command, trigger billing/inventory actions |
| `GET /inventory` | Fetch all inventory items |
| `GET /inventory/{product}` | Fetch a single product’s stock |
| `GET /test-db` | Test database connection |

---

## How It Works
1. User speaks a command in **Urdu**
2. **UpliftAI STT API** transcribes it to text
3. FastAPI parses the command → identifies **intent** (billing / stock / report)
4. Executes database operations in **PostgreSQL**
5. Returns a structured response (message + updated data)

---

## Tech Stack
- **Backend:** FastAPI (Python)  
- **Database:** PostgreSQL (via `psycopg` + SQLAlchemy)  
- **Speech-to-Text:** [UpliftAI API](https://upliftai.org)  
- **Language:** Urdu (`ur`)  
- **Domain:** `phone-commerce`  
- **Frontend:** React (for UI testing and integration)

---

## Run Locally
1. Clone the repository  
2. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server  
   ```bash
   uvicorn stt:app --reload
   ```
4. Test endpoints in Postman or your frontend app

---

## Example Response
```json
{
  "transcription": "اسٹاک کم کریں ایپل پانچ",
  "message": "Apple کا اسٹاک 5 کم کر دیا گیا۔ نیا اسٹاک: 45",
  "product": "Apple",
  "quantity": 5,
  "new_stock_level": 45
}
```
