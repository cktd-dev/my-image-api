from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
import cloudinary.uploader
import os

app = FastAPI()

# --- 1. MANDATORY CORS CONFIGURATION ---
# This fixes the "Failed to connect" and "Failed to fetch" errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your React app to talk to this API
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST requests
    allow_headers=["*"],  # Allows Content-Type and other headers
)

# Cloudinary Config
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

@app.get("/")
def home():
    return {"status": "Online", "engine": "Cloudinary AI"}

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    # Basic validation for file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # 2. Image upload and AI enhancement
        # We use file.file.read() to ensure the stream is correctly passed
        upload_result = cloudinary.uploader.upload(
            file.file,
            transformation=[
                {"effect": "improve:outdoor"}, # Auto color/light fix
                {"effect": "upscale"},         # AI Pixel Enhancement
                {"quality": "auto"}            # Best quality optimization
            ]
        )
        
        # 3. Return the JSON response your React code expects
        return {
            "status": "success",
            "enhanced_url": upload_result["secure_url"],
            "original_width": upload_result.get("width"),
            "original_height": upload_result.get("height")
        }

    except Exception as e:
        # Return a 500 error instead of a generic success message with an error status
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")
