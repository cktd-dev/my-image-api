from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# SABSE STABLE MODEL (Hugging Face Official)
MODEL_ID = "google/vit-base-patch16-224" # Note: Ye model test ke liye hai, Upscale ke liye niche wala URL use karein
# Image Enhancement ke liye ye naya path try karein
API_URL = "https://router.huggingface.co/hf-inference/models/jinhyogo/real-esrgan-v3"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"status": "Online", "model": "Real-ESRGAN-V3", "router": "Active"}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN missing in Vercel. Add it in Settings > Environment Variables."}

    image_bytes = await file.read()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Try multiple times if model is 503 (loading)
    for i in range(2):
        response = requests.post(API_URL, headers=headers, data=image_bytes)
        
        if response.status_code == 200:
            return Response(content=response.content, media_type="image/png")
        elif response.status_code == 503:
            time.sleep(10) # 10 second wait karein agar model load ho raha hai
            continue
        else:
            # Agar 404 aaye toh alternate backup model use karein
            backup_url = "https://router.huggingface.co/hf-inference/models/cardiffnlp/twitter-roberta-base-sentiment"
            return {
                "error": "Model not responding",
                "status": response.status_code,
                "msg": "Hugging Face is restricting this model. Try a smaller image."
            }
            
    return {"error": "Server busy, please try again."}
