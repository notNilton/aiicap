"""
Image Corrector class for comprehensive image correction with PostgreSQL storage

Includes:
- Block-based color correction
- Pixelation
- Dithering
- Palette reduction
- Automatic database saving of corrected images
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional, Dict, Any
import time
import json

from .strategies import Strategies
from .effects import apply_pixelation, apply_dithering, apply_median_palette
from .color_utils import (
    get_majority_color,
    get_average_of_colors,
    get_harmonic_mean_of_colors,
    get_geometric_mean_of_colors,
    get_midrange_of_colors,
    get_quadratic_mean_of_colors,
    get_cubic_mean_of_colors
)
from ..database import get_session
from ..database.repository import ImageRepository


class ImageCorrector:
    """
    Comprehensive image correction tool with database integration.
    
    Provides methods for:
    - Block-based color correction with multiple strategies
    - Pixelation effects
    - Floyd-Steinberg dithering
    - Median palette reduction
    - Automatic PostgreSQL storage of corrected images
    """
    
    def __init__(self, image: Optional[Image.Image] = None, source_db_id: Optional[int] = None, auto_save_db: bool = True):
        """
        Initialize the image corrector.
        
        Args:
            image: Optional PIL Image to process
            source_db_id: Optional database ID of the source generated image
            auto_save_db: If True, automatically save corrected images to database
        """
        self.original_image = image.convert("RGB") if image else None
        self.current_image = self.original_image.copy() if self.original_image else None
        self.source_db_id = source_db_id
        self.auto_save_db = auto_save_db
        self.last_correction_db_id: Optional[int] = None
    
    def load_image(self, image_path: str) -> None:
        """
        Load an image from file path.
        
        Args:
            image_path: Path to the image file
        """
        self.original_image = Image.open(image_path).convert("RGB")
        self.current_image = self.original_image.copy()
    
    def load_from_database(self, image_id: int, is_generated: bool = True) -> None:
        """
        Load an image from the database.
        
        Args:
            image_id: Database ID of the image
            is_generated: If True, load from generated_images table, else from corrected_images
        """
        with get_session() as session:
            if is_generated:
                db_image = ImageRepository.get_generated_image(session, image_id)
                if not db_image:
                    raise ValueError(f"Generated image with ID {image_id} not found")
                self.original_image = ImageRepository.load_image_from_db(db_image)
                self.source_db_id = image_id
            else:
                db_image = ImageRepository.get_corrected_image(session, image_id)
                if not db_image:
                    raise ValueError(f"Corrected image with ID {image_id} not found")
                self.original_image = ImageRepository.load_corrected_image_from_db(db_image)
                self.source_db_id = db_image.source_image_id
            
            self.current_image = self.original_image.copy()
    
    def set_image(self, image: Image.Image, source_db_id: Optional[int] = None) -> None:
        """
        Set the image to process.
        
        Args:
            image: PIL Image object
            source_db_id: Optional database ID of the source image
        """
        self.original_image = image.convert("RGB")
        self.current_image = self.original_image.copy()
        if source_db_id:
            self.source_db_id = source_db_id
    
    def pixelate(self, pixel_size: int = 256) -> Image.Image:
        """
        Apply pixelation effect to the current image.
        
        Automatically saves to database if auto_save_db is True.
        
        Args:
            pixel_size: Size of pixel blocks
            
        Returns:
            Pixelated PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        start_time = time.time()
        self.current_image = apply_pixelation(self.current_image, pixel_size)
        processing_time = time.time() - start_time
        
        # Save to database
        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type='pixelation',
                parameters={'pixel_size': pixel_size},
                processing_time=processing_time
            )
        
        return self.current_image
    
    def dither(self, levels: int = 10) -> Image.Image:
        """
        Apply Floyd-Steinberg dithering to the current image.
        
        Automatically saves to database if auto_save_db is True.
        
        Args:
            levels: Number of color levels
            
        Returns:
            Dithered PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        start_time = time.time()
        self.current_image = apply_dithering(self.current_image, levels)
        processing_time = time.time() - start_time
        
        # Save to database
        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type='dithering',
                parameters={'levels': levels},
                processing_time=processing_time
            )
        
        return self.current_image
    
    def reduce_palette(self, num_colors: int = 32) -> Image.Image:
        """
        Apply median palette reduction to the current image.
        
        Automatically saves to database if auto_save_db is True.
        
        Args:
            num_colors: Number of colors in the reduced palette
            
        Returns:
            Palette-reduced PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        start_time = time.time()
        self.current_image = apply_median_palette(self.current_image, num_colors)
        processing_time = time.time() - start_time
        
        # Save to database
        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type='palette_reduction',
                parameters={'num_colors': num_colors},
                processing_time=processing_time
            )
        
        return self.current_image
    
    def correct_colors(
        self,
        block_width: int = 4,
        block_height: int = 4,
        strategy: Strategies = Strategies.AVERAGE,
        tolerance: int = 1,
        shrink_output: bool = False
    ) -> Image.Image:
        """
        Apply block-based color correction.
        
        Automatically saves to database if auto_save_db is True.
        
        Args:
            block_width: Width of processing blocks
            block_height: Height of processing blocks
            strategy: Color processing strategy to use
            tolerance: Color matching tolerance for MAJORITY strategy
            shrink_output: If True, output one pixel per block
        
        Returns:
            Corrected PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        start_time = time.time()
        
        # Convert to numpy array
        if self.current_image.mode != 'RGBA':
            img_data = np.array(self.current_image.convert("RGBA"))
        else:
            img_data = np.array(self.current_image)
        
        # Process the image
        processed, height, width = self._fix_image(
            img_data,
            self.current_image.height,
            self.current_image.width,
            block_width,
            block_height,
            strategy,
            tolerance,
            shrink_output
        )
        
        # Convert back to PIL Image
        if processed.dtype != np.uint8:
            processed = processed.astype(np.uint8)
        
        if processed.ndim == 3 and processed.shape[2] == 4:
            self.current_image = Image.fromarray(processed, 'RGBA')
        elif processed.ndim == 3 and processed.shape[2] == 3:
            self.current_image = Image.fromarray(processed, 'RGB')
        else:
            self.current_image = Image.fromarray(processed)
        
        processing_time = time.time() - start_time
        
        # Save to database
        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type='color_correction',
                parameters={
                    'block_width': block_width,
                    'block_height': block_height,
                    'strategy': strategy.name,
                    'tolerance': tolerance,
                    'shrink_output': shrink_output
                },
                processing_time=processing_time
            )
        
        return self.current_image
    
    def _save_to_database(
        self,
        correction_type: str,
        parameters: Dict[str, Any],
        processing_time: float
    ) -> None:
        """
        Save corrected image to database.
        
        Args:
            correction_type: Type of correction applied
            parameters: Parameters used
            processing_time: Time taken to process
        """
        try:
            with get_session() as session:
                # Get original prompt if available
                original_prompt = None
                if self.source_db_id:
                    source = ImageRepository.get_generated_image(session, self.source_db_id)
                    if source:
                        original_prompt = source.prompt
                
                db_image = ImageRepository.save_corrected_image(
                    session=session,
                    image=self.current_image,
                    source_image_id=self.source_db_id,
                    correction_type=correction_type,
                    parameters=parameters,
                    original_prompt=original_prompt,
                    processing_time=processing_time
                )
                self.last_correction_db_id = db_image.id
                print(f"✓ Corrected image saved to database with ID: {db_image.id}")
        except Exception as e:
            print(f"⚠ Warning: Could not save to database: {e}")
    
    def _fix_image(
        self,
        image_data: np.ndarray,
        height: int,
        width: int,
        out_pix_width: int,
        out_pix_height: int,
        strategy: Strategies,
        tolerance: int = 1,
        shrink_output: bool = False
    ) -> Tuple[np.ndarray, int, int]:
        """Process an image using block-based color strategies."""
        # Adjust dimensions to be divisible by block size
        adjusted_width = (width // out_pix_width) * out_pix_width
        adjusted_height = (height // out_pix_height) * out_pix_height
        
        # Split into blocks
        blocks = []
        for y in range(0, adjusted_height, out_pix_height):
            for x in range(0, adjusted_width, out_pix_width):
                block = image_data[y:y+out_pix_height, x:x+out_pix_width]
                blocks.append(block.reshape(-1, block.shape[-1]))
        
        # Process each block
        processed_blocks = []
        for block in blocks:
            processed_block = self._process_block(block, strategy, tolerance)
            processed_blocks.append(processed_block)
        
        if shrink_output:
            # Create reduced size image (one pixel per block)
            out_height = adjusted_height // out_pix_height
            out_width = adjusted_width // out_pix_width
            out_data = np.array([block[0] for block in processed_blocks])
            out_data = out_data.reshape(out_height, out_width, -1)
        else:
            # Reconstruct full size image
            out_height = adjusted_height
            out_width = adjusted_width
            out_data = np.zeros((adjusted_height * adjusted_width, image_data.shape[2]))
            
            block_idx = 0
            for y in range(0, adjusted_height, out_pix_height):
                for x in range(0, adjusted_width, out_pix_width):
                    block = processed_blocks[block_idx]
                    idx = 0
                    for by in range(out_pix_height):
                        for bx in range(out_pix_width):
                            pos = (y + by) * adjusted_width + (x + bx)
                            out_data[pos] = block[idx]
                            idx += 1
                    block_idx += 1
            
            out_data = out_data.reshape(adjusted_height, adjusted_width, -1)
        
        out_data = np.clip(out_data, 0, 255).astype(np.uint8)
        return out_data, out_height, out_width
    
    def _process_block(
        self,
        block: np.ndarray,
        strategy: Strategies,
        tolerance: int
    ) -> np.ndarray:
        """Process a single block using the specified strategy."""
        if strategy == Strategies.MAJORITY:
            color, _ = get_majority_color(block, tolerance)
            return np.tile(color, (len(block), 1))
        elif strategy == Strategies.AVERAGE:
            color = get_average_of_colors(block)
            return np.tile(color, (len(block), 1))
        elif strategy == Strategies.HARMONIC:
            color = get_harmonic_mean_of_colors(block)
            return np.tile(color, (len(block), 1))
        elif strategy == Strategies.GEOMETRIC:
            color = get_geometric_mean_of_colors(block)
            return np.tile(color, (len(block), 1))
        elif strategy == Strategies.MIDRANGE:
            color = get_midrange_of_colors(block)
            return np.tile(color, (len(block), 1))
        elif strategy == Strategies.QUADRATIC:
            color = get_quadratic_mean_of_colors(block)
            return np.tile(color, (len(block), 1))
        elif strategy == Strategies.CUBIC:
            color = get_cubic_mean_of_colors(block)
            return np.tile(color, (len(block), 1))
        else:  # Algorithm strategies
            color, occurrences = get_majority_color(block, tolerance)
            coverage = occurrences / len(block)
            if coverage >= strategy.value:
                return np.tile(color, (len(block), 1))
            else:
                avg_color = get_average_of_colors(block)
                return np.tile(avg_color, (len(block), 1))
    
    def reset(self) -> None:
        """Reset the current image to the original."""
        if self.original_image is None:
            raise ValueError("No image loaded")
        
        self.current_image = self.original_image.copy()
    
    def get_current_image(self) -> Image.Image:
        """Get the current processed image."""
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        return self.current_image
    
    def get_original_image(self) -> Image.Image:
        """Get the original unprocessed image."""
        if self.original_image is None:
            raise ValueError("No image loaded")
        
        return self.original_image
    
    def get_last_correction_db_id(self) -> Optional[int]:
        """Get the database ID of the last saved correction."""
        return self.last_correction_db_id
    
    def get_all_corrections(self) -> list:
        """
        Get all corrections for the current source image.
        
        Returns:
            List of correction metadata dictionaries
        """
        if not self.source_db_id:
            return []
        
        with get_session() as session:
            corrections = ImageRepository.get_corrected_images_by_source(
                session, self.source_db_id
            )
            return [corr.to_dict() for corr in corrections]
