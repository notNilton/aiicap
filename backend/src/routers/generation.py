"""
Generation Router - Image generation endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import httpx
import os

router = APIRouter()

# Image generator service URL
IMAGE_GENERATOR_URL = os.getenv("IMAGE_GENERATOR_URL", "http://localhost:8001")


class GenerationRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    style: Optional[str] = None


class GenerationResponse(BaseModel):
    id: int
    status: str
    prompt: str
    message: str


class GenerationStatus(BaseModel):
    id: int
    status: str  # pending, processing, completed, failed
    prompt: str
    image_url: Optional[str] = None
    error: Optional[str] = None


@router.post("/", response_model=GenerationResponse)
async def generate_image(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Request a new image generation"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{IMAGE_GENERATOR_URL}/generate",
                json=request.model_dump(),
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return GenerationResponse(
                id=data.get("id", 0),
                status="pending",
                prompt=request.prompt,
                message="Image generation started"
            )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Image generator service is not available"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{generation_id}", response_model=GenerationStatus)
async def get_generation_status(generation_id: int):
    """Get the status of an image generation request"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{IMAGE_GENERATOR_URL}/status/{generation_id}",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Image generator service is not available"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_generation_history(limit: int = 20):
    """Get recent generation history"""
    from packages.shared.storage import get_storage
    
    storage = get_storage()
    images = storage.list_generated_images(limit=limit)
    
    return {"generations": images, "count": len(images)}
