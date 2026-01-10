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

# 2026 Stable Model for Image Upscaling
# Ye model Hugging Face par active rehta hai
MODEL_ID = "stabilityai/stable-diffusion-x4-upscaler"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL_ID}"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"status": "Online", "active_model": MODEL_ID}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN missing in Vercel settings"}

    image_bytes = await file.read()
    
    # Headers for Image Binary Data
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
    }
    
    try:
        # Request to Hugging Face
        response = requests.post(API_URL, headers=headers, data=image_bytes, timeout=60)
        
        if response.status_code == 200:
            return Response(content=response.content, media_type="image/png")
        elif response.status_code == 503:
            return {"error": "Model is starting up. Retry in 30 seconds."}
        else:
            # Error Details dikhayega taaki hum samajh sakein kya hua
            return {
                "error": "HF API Issue",
                "status": response.status_code,
                "msg": response.text[:200]
            }
    except Exception as e:
        return {"error": str(e)}
