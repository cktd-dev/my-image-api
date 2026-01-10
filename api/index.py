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

# NAYA UPDATED URL (As per Hugging Face latest update)
API_URL = "https://router.huggingface.co/hf-inference/models/cjwbw/real-esrgan"
HF_TOKEN = os.getenv("HF_TOKEN")

@app.get("/")
def home():
    return {"message": "API is online with new Hugging Face Router!"}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    if not HF_TOKEN:
        return {"error": "HF_TOKEN missing in Environment Variables"}

    image_bytes = await file.read()
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Nayi request naye URL par
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    
    if response.status_code == 200:
        return Response(content=response.content, media_type="image/png")
    elif response.status_code == 503:
        return {"error": "Model is waking up. Please retry in 20 seconds."}
    else:
        return {
            "error": "Processing failed", 
            "status": response.status_code,
            "details": response.text[:200] # Takki lamba HTML error na dikhe
        }
