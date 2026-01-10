from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# LATEST 2026 ROUTER ENDPOINT
# Hum Scuyler/Real-ESRGAN use kar rahe hain jo kafi stable hai
MODEL_ID = "scuyler/real-esrgan-v3"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"status": "Online", "model": MODEL_ID}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN missing in Vercel settings"}

    image_bytes = await file.read()
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    
    try:
        response = requests.post(API_URL, headers=headers, data=image_bytes, timeout=30)
        
        if response.status_code == 200:
            return Response(content=response.content, media_type="image/png")
        elif response.status_code == 503:
            return {"error": "Model loading... please retry in 20 seconds."}
        else:
            return {
                "error": "HF API Issue",
                "status": response.status_code,
                "msg": response.text[:100]
            }
    except Exception as e:
        return {"error": str(e)}
