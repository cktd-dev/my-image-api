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

# Hugging Face Model URL
API_URL = "https://api-inference.huggingface.co/models/akhaliq/Real-ESRGAN"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"message": "API is working! Use /enhance to upscale images."}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "Missing HF_TOKEN variable"}

    image_bytes = await file.read()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Hugging Face API Request
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    
    if response.status_code == 200:
        return Response(content=response.content, media_type="image/png")
    else:
        return {"error": "Processing failed", "status": response.status_code}
