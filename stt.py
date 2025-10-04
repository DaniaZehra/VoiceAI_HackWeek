from fastapi import FastAPI, File, UploadFile
import requests

app = FastAPI()

API_URL = "https://api.upliftai.org/v1/transcribe/speech-to-text"
API_KEY = "sk_api_e96abf4d0ddb84d1f142b22fb37cccee645cda84c7c4a5d9b509671d5ee67273"

@app.post("/voice-command")
async def voice_command(file: UploadFile = File(...)):
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
    
    # Simulate actions
    if "سیلز" in text:
        message = "یہ آج کی سیلز رپورٹ ہے (dummy data)"
    elif "پروڈکٹ" in text:
        message = "پروڈکٹ لسٹ دکھا رہا ہوں (dummy data)"
    elif "بل" in text:
        message = "بلنگ اسکرین کھول رہا ہوں (dummy data)"
    else:
        message = f"کمانڈ سمجھ نہیں آئی: {text}"
    
    return {"transcription": text, "message": message}

@app.get("/")
async def root():
    return {"message": "Welcome to the VoiceAI API POS system"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)