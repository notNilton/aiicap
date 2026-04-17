"""
AIICAP Image Generator Service

FastAPI service for AI-powered image generation using DALL-E.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager
from datetime import datetime
import os

from .image_generation import ImageGenerator


# Store for tracking generation status
generation_status = {}
generation_counter = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    from packages.shared.database import init_db
    init_db()
    print("[OK] Image Generator Service started")
    yield
    print("[OK] Image Generator Service stopped")


app = FastAPI(
    title="AIICAP Image Generator",
    description="AI Image Generation Service using DALL-E",
    version="1.0.0",
    lifespan=lifespan
)


class GenerationRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    style: Optional[str] = None


class GenerationResponse(BaseModel):
    id: int
    status: str
    prompt: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "aiicap-image-generator"}


@app.post("/generate", response_model=GenerationResponse)
async def generate_image(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Request a new image generation"""
    global generation_counter
    
    generation_counter += 1
    gen_id = generation_counter
    
    # Initialize status
    generation_status[gen_id] = {
        "id": gen_id,
        "status": "pending",
        "prompt": request.prompt,
        "image_url": None,
        "error": None,
        "created_at": datetime.now().isoformat()
    }
    
    # Start background generation
    background_tasks.add_task(
        process_generation,
        gen_id,
        request.prompt,
        request.size,
        request.quality,
        request.style
    )
    
    return GenerationResponse(
        id=gen_id,
        status="pending",
        prompt=request.prompt
    )


async def process_generation(
    gen_id: int,
    prompt: str,
    size: str,
    quality: str,
    style: Optional[str]
):
    """Process image generation in background"""
    try:
        generation_status[gen_id]["status"] = "processing"
        
        generator = ImageGenerator(auto_save_db=True)
        
        # Check if API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        
        # Force the requested pixel art prompt
        forced_prompt = (
            "A highly detailed 16-bit pixel art of a vibrant medieval fantasy landscape."
        )
        
        print(f"Ignoring user prompt: '{prompt}'")
        print(f"Using forced prompt: '{forced_prompt}'")
        
        if not api_key:
             generation_status[gen_id]["status"] = "failed"
             generation_status[gen_id]["error"] = "OPENAI_API_KEY not set"
             return

        # Real generation
        image = generator.generate(
            prompt=forced_prompt,
            size=size,
            quality=quality
        )
        
        db_id = generator.get_last_db_id()
        generation_status[gen_id]["status"] = "completed"
        generation_status[gen_id]["image_url"] = f"/uploads/generated_{db_id}.png"
        generation_status[gen_id]["db_id"] = db_id
        generation_status[gen_id]["prompt"] = forced_prompt # Update status with actual used prompt
            
    except Exception as e:
        generation_status[gen_id]["status"] = "failed"
        generation_status[gen_id]["error"] = str(e)


@app.get("/status/{generation_id}")
async def get_status(generation_id: int):
    """Get generation status"""
    if generation_id not in generation_status:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return generation_status[generation_id]


@app.get("/history")
async def get_history(limit: int = 20):
    """Get recent generations"""
    recent = sorted(
        generation_status.values(),
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )[:limit]
    return {"generations": recent, "count": len(recent)}
