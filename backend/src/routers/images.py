"""
Images Router - CRUD operations for images
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class ImageResponse(BaseModel):
    id: int
    prompt: Optional[str] = None
    model: Optional[str] = None
    size: Optional[str] = None
    created_at: str
    is_corrected: bool = False


class ImageListResponse(BaseModel):
    images: list[ImageResponse]
    total: int
    page: int
    per_page: int


@router.get("/", response_model=ImageListResponse)
async def list_images(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    type: str = Query("all", regex="^(all|generated|corrected)$")
):
    """List all images with pagination"""
    from packages.shared.storage import get_storage
    
    storage = get_storage()
    
    # Get images based on type filter
    if type == "generated":
        images = storage.list_generated_images(limit=per_page, offset=(page - 1) * per_page)
    elif type == "corrected":
        images = storage.list_corrected_images(limit=per_page, offset=(page - 1) * per_page)
    else:
        images = storage.list_all_images(limit=per_page, offset=(page - 1) * per_page)
    
    return ImageListResponse(
        images=[ImageResponse(**img) for img in images],
        total=len(images),
        page=page,
        per_page=per_page
    )


@router.get("/{image_id}")
async def get_image(image_id: int):
    """Get a specific image by ID"""
    from packages.shared.storage import get_storage
    
    storage = get_storage()
    image_data = storage.get_image_metadata(image_id)
    
    if not image_data:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return image_data


@router.delete("/{image_id}")
async def delete_image(image_id: int):
    """Delete an image by ID"""
    from packages.shared.storage import get_storage
    
    storage = get_storage()
    success = storage.delete_image(image_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"message": "Image deleted successfully", "id": image_id}
