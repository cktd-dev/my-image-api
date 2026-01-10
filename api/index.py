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

# 100% Active Model for Image Restoration (Tencent-ARC)
MODEL_ID = "TencentARC/GFPGAN"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"status": "Online", "model": MODEL_ID, "info": "Use /enhance to upscale"}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN missing in Vercel settings"}

    image_bytes = await file.read()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Retry mechanism agar model load ho raha ho
    max_retries = 3
    for i in range(max_retries):
        response = requests.post(API_URL, headers=headers, data=image_bytes)
        
        if response.status_code == 200:
            return Response(content=response.content, media_type="image/png")
        elif response.status_code == 503:
            # Model warm up ho raha hai, thoda wait karein
            time.sleep(10)
            continue
        else:
            return {
                "error": "HF API Issue",
                "status": response.status_code,
                "msg": response.json() if response.headers.get('content-type') == 'application/json' else "Model Error"
            }
            
    return {"error": "Model took too long to load. Try again now."}
