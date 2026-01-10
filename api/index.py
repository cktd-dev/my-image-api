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

# OFFICIAL STABLE MODEL (Ye 404 nahi dega)
MODEL_ID = "stabilityai/stable-diffusion-x4-upscaler"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"status": "Online", "model": MODEL_ID}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN setting missing in Vercel"}

    image_bytes = await file.read()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Retry mechanism for 503 (Loading) errors
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, data=image_bytes, timeout=120)
            
            if response.status_code == 200:
                return Response(content=response.content, media_type="image/png")
            
            elif response.status_code == 503:
                # Model is warming up, wait and retry
                time.sleep(15)
                continue
            
            else:
                return {
                    "error": "HF API Issue",
                    "status": response.status_code,
                    "msg": "Model busy or not available"
                }
        except Exception as e:
            return {"error": str(e)}
            
    return {"error": "Model took too long to load. Please try again now."}
