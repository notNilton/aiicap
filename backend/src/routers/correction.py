"""
Correction Router - Image correction endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import io

router = APIRouter()


class CorrectionRequest(BaseModel):
    image_id: int
    correction_type: str  # pixelation, dithering, palette_reduction, color_correction
    parameters: Optional[dict] = None


class CorrectionResponse(BaseModel):
    id: int
    source_id: int
    correction_type: str
    message: str


@router.post("/", response_model=CorrectionResponse)
async def correct_image(request: CorrectionRequest):
    """Apply a correction to an existing image"""
    from packages.shared.storage import get_storage
    from ..image_correction import ImageCorrector, Strategies
    
    storage = get_storage()
    
    # Load source image
    source_image = storage.load_image(request.image_id, is_generated=True)
    if not source_image:
        raise HTTPException(status_code=404, detail="Source image not found")
    
    # Apply correction
    corrector = ImageCorrector(auto_save_db=False)
    corrector.set_image(source_image)
    
    params = request.parameters or {}
    
    try:
        if request.correction_type == "pixelation":
            pixel_size = params.get("pixel_size", 128)
            corrector.pixelate(pixel_size=pixel_size)
        
        elif request.correction_type == "dithering":
            levels = params.get("levels", 10)
            corrector.dither(levels=levels)
        
        elif request.correction_type == "palette_reduction":
            num_colors = params.get("num_colors", 16)
            corrector.reduce_palette(num_colors=num_colors)
        
        elif request.correction_type == "color_correction":
            strategy_name = params.get("strategy", "AVERAGE")
            strategy = Strategies[strategy_name]
            corrector.correct_colors(
                block_width=params.get("block_width", 4),
                block_height=params.get("block_height", 4),
                strategy=strategy
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown correction type: {request.correction_type}"
            )
        
        # Get corrected image
        corrected_image = corrector.get_current_image()
        
        # Save corrected image
        corrected_id = storage.save_corrected_image(
            image=corrected_image,
            source_id=request.image_id,
            correction_type=request.correction_type,
            parameters=params
        )
        
        return CorrectionResponse(
            id=corrected_id,
            source_id=request.image_id,
            correction_type=request.correction_type,
            message="Correction applied successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def correct_uploaded_image(
    file: UploadFile = File(...),
    correction_type: str = Form(...),
    parameters: Optional[str] = Form(None)
):
    """Upload and correct an image in one request"""
    from ..image_correction import ImageCorrector, Strategies
    import json
    
    # Read uploaded image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # Parse parameters
    params = json.loads(parameters) if parameters else {}
    
    # Apply correction
    corrector = ImageCorrector(auto_save_db=False)
    corrector.set_image(image)
    
    try:
        if correction_type == "pixelation":
            corrector.pixelate(pixel_size=params.get("pixel_size", 128))
        elif correction_type == "dithering":
            corrector.dither(levels=params.get("levels", 10))
        elif correction_type == "palette_reduction":
            corrector.reduce_palette(num_colors=params.get("num_colors", 16))
        elif correction_type == "color_correction":
            strategy = Strategies[params.get("strategy", "AVERAGE")]
            corrector.correct_colors(
                block_width=params.get("block_width", 4),
                block_height=params.get("block_height", 4),
                strategy=strategy
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown correction type")
        
        # Get result
        corrected_image = corrector.get_current_image()
        
        # Convert to bytes for response
        buffer = io.BytesIO()
        corrected_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            buffer,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=corrected_{file.filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_correction_types():
    """List available correction types and their parameters"""
    return {
        "types": [
            {
                "name": "pixelation",
                "description": "Apply pixelation effect",
                "parameters": {"pixel_size": {"type": "int", "default": 128, "range": [2, 512]}}
            },
            {
                "name": "dithering",
                "description": "Apply dithering effect",
                "parameters": {"levels": {"type": "int", "default": 10, "range": [2, 256]}}
            },
            {
                "name": "palette_reduction",
                "description": "Reduce color palette",
                "parameters": {"num_colors": {"type": "int", "default": 16, "range": [2, 256]}}
            },
            {
                "name": "color_correction",
                "description": "Apply color correction by blocks",
                "parameters": {
                    "block_width": {"type": "int", "default": 4},
                    "block_height": {"type": "int", "default": 4},
                    "strategy": {"type": "enum", "values": ["AVERAGE", "MEDIAN", "MODE"], "default": "AVERAGE"}
                }
            }
        ]
    }
