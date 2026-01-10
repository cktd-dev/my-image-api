from fastapi import FastAPI, UploadFile, File
import cloudinary
import cloudinary.uploader
import os

app = FastAPI()

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
    try:
        # 1. Image upload karna aur AI enhancement apply karna
        # 'e_improve' aur 'e_upscale' pixels add karte hain aur blurryness hatate hain
        upload_result = cloudinary.uploader.upload(
            file.file,
            transformation=[
                {"effect": "improve:outdoor"}, # Auto color/light fix
                {"effect": "upscale"},         # AI Pixel Enhancement
                {"quality": "auto"}            # Best quality optimization
            ]
        )
        
        # 2. Enhanced Image ka URL return karna
        return {
            "status": "success",
            "enhanced_url": upload_result["secure_url"],
            "original_width": upload_result["width"],
            "original_height": upload_result["height"]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
