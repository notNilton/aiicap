"""
Image Corrector class for comprehensive image correction

Includes:
- Block-based color correction
- Pixelation
- Dithering
- Palette reduction
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional
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


class ImageCorrector:
    """
    Comprehensive image correction tool.
    
    Provides methods for:
    - Block-based color correction with multiple strategies
    - Pixelation effects
    - Floyd-Steinberg dithering
    - Median palette reduction
    """
    
    def __init__(self, image: Optional[Image.Image] = None):
        """
        Initialize the image corrector.
        
        Args:
            image: Optional PIL Image to process
        """
        self.original_image = image.convert("RGB") if image else None
        self.current_image = self.original_image.copy() if self.original_image else None
    
    def load_image(self, image_path: str) -> None:
        """
        Load an image from file path.
        
        Args:
            image_path: Path to the image file
        """
        self.original_image = Image.open(image_path).convert("RGB")
        self.current_image = self.original_image.copy()
    
    def set_image(self, image: Image.Image) -> None:
        """
        Set the image to process.
        
        Args:
            image: PIL Image object
        """
        self.original_image = image.convert("RGB")
        self.current_image = self.original_image.copy()
    
    def pixelate(self, pixel_size: int = 256) -> Image.Image:
        """
        Apply pixelation effect to the current image.
        
        Args:
            pixel_size: Size of pixel blocks
            
        Returns:
            Pixelated PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        self.current_image = apply_pixelation(self.current_image, pixel_size)
        return self.current_image
    
    def dither(self, levels: int = 10) -> Image.Image:
        """
        Apply Floyd-Steinberg dithering to the current image.
        
        Args:
            levels: Number of color levels
            
        Returns:
            Dithered PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        self.current_image = apply_dithering(self.current_image, levels)
        return self.current_image
    
    def reduce_palette(self, num_colors: int = 32) -> Image.Image:
        """
        Apply median palette reduction to the current image.
        
        Args:
            num_colors: Number of colors in the reduced palette
            
        Returns:
            Palette-reduced PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        self.current_image = apply_median_palette(self.current_image, num_colors)
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
        
        return self.current_image
    
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
        """
        Process an image using block-based color strategies.
        
        Args:
            image_data: Input image as numpy array (height, width, channels)
            height: Original image height
            width: Original image width
            out_pix_width: Output pixel block width
            out_pix_height: Output pixel block height
            strategy: Color processing strategy
            tolerance: Color matching tolerance
            shrink_output: Whether to shrink output to block size
        
        Returns:
            Tuple of (processed_image, new_height, new_width)
        """
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
        """
        Process a single block using the specified strategy.
        
        Args:
            block: Block of pixels to process
            strategy: Processing strategy
            tolerance: Color matching tolerance
        
        Returns:
            Processed block
        """
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
        """
        Get the current processed image.
        
        Returns:
            Current PIL Image
        """
        if self.current_image is None:
            raise ValueError("No image loaded")
        
        return self.current_image
    
    def get_original_image(self) -> Image.Image:
        """
        Get the original unprocessed image.
        
        Returns:
            Original PIL Image
        """
        if self.original_image is None:
            raise ValueError("No image loaded")
        
        return self.original_image
