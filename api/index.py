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

# Naya Stable Model URL
API_URL = "https://api-inference.huggingface.co/models/cjwbw/real-esrgan"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"message": "API is online! Using stable model."}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN is missing in Vercel settings"}

    image_bytes = await file.read()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    
    if response.status_code == 200:
        return Response(content=response.content, media_type="image/png")
    elif response.status_code == 503:
        return {"error": "Model is loading (starting up). Please wait 20 seconds and try again."}
    else:
        return {
            "error": "Processing failed", 
            "status": response.status_code,
            "details": response.text
        }
