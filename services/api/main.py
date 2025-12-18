from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import sys
import io
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# sys.path hack removed as modules are now local


from modules.database import init_db
from modules.storage import get_storage

app = FastAPI(title="AIICAP API Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Ensure DB is initialized
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing DB: {e}")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), prompt: str = Form("Uploaded image")):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        storage = get_storage()
        image_id = storage.save_generated_image(
            image=image,
            prompt=prompt,
            model="uploaded",
            size=f"{image.width}x{image.height}",
            quality="standard"
        )
        
        # Close the file
        await file.close()
        
        return {"status": "success", "image_id": image_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images/{image_id}")
async def get_image_status(image_id: int):
    try:
        storage = get_storage()
        image = storage.load_image(image_id, is_generated=True)
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Check for corrections
        from modules.database import get_session
        from modules.database.models import CorrectedImage
        
        with get_session() as session:
            corrections = session.query(CorrectedImage).filter(
                CorrectedImage.source_image_id == image_id
            ).all()
            
            return {
                "id": image_id,
                "status": "processed" if corrections else "pending",
                "corrections": [c.correction_type for c in corrections]
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
