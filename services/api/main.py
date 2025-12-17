from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import io
from PIL import Image
from datetime import datetime

# sys.path hack removed as modules are now local


from modules.database import init_db
from modules.storage import get_storage

app = FastAPI(title="AIICAP API Service")

@app.on_event("startup")
def startup_event():
    # Ensure DB is initialized
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing DB: {e}")

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), prompt: str = "Uploaded image"):
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
        
        return {"status": "success", "image_id": image_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
