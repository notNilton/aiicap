"""
Image Corrector – deterministic restoration pipeline for Pixel Art integrity.

Implements the three-stage architecture from the article:
    P(I) = f_α( f_k( f_g(I) ) )

- f_g : geometric grid reconstruction (Nearest-Neighbour)
- f_k : chromatic quantization (K-Means)
- f_α : opacity binarization (threshold τ)

Also preserves legacy block-based colour-correction methods for backward
compatibility.
"""

import json
import time
from typing import Any, Dict, Optional, Tuple

import numpy as np
from PIL import Image

from database import get_session
from database.repository import ImageRepository

from .pipeline import restore as restore_pipeline
from .metrics import compute_metrics

from .color_utils import (
    get_average_of_colors,
    get_cubic_mean_of_colors,
    get_geometric_mean_of_colors,
    get_harmonic_mean_of_colors,
    get_majority_color,
    get_midrange_of_colors,
    get_quadratic_mean_of_colors,
)
from .effects import apply_dithering, apply_median_palette, apply_pixelation
from .strategies import Strategies


class ImageCorrector:
    """
    Comprehensive image correction tool with database integration.

    Primary API (article pipeline):
        - restore(target_size, palette_size, alpha_threshold)

    Legacy API (kept for backward compatibility):
        - correct_colors(...)
        - pixelate(...)
        - dither(...)
        - reduce_palette(...)
    """

    def __init__(
        self,
        image: Optional[Image.Image] = None,
        source_db_id: Optional[int] = None,
        auto_save_db: bool = True,
    ):
        self.original_image: Optional[Image.Image] = image.copy() if image else None
        self.current_image: Optional[Image.Image] = (
            self.original_image.copy() if self.original_image else None
        )
        self.source_db_id = source_db_id
        self.auto_save_db = auto_save_db
        self.last_correction_db_id: Optional[int] = None
        self.last_metrics: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------ #
    # Loading / setting
    # ------------------------------------------------------------------ #

    def load_image(self, image_path: str) -> None:
        """Load an image from file, preserving its original mode (RGB/RGBA)."""
        self.original_image = Image.open(image_path)
        self.current_image = self.original_image.copy()

    def load_from_database(self, image_id: int, is_generated: bool = True) -> None:
        """Load an image from the database."""
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
        """Set the image to process."""
        self.original_image = image.copy()
        self.current_image = self.original_image.copy()
        if source_db_id:
            self.source_db_id = source_db_id

    # ------------------------------------------------------------------ #
    # Article pipeline – primary API
    # ------------------------------------------------------------------ #

    def restore(
        self,
        target_size: Tuple[int, int] = (64, 64),
        palette_size: int = 16,
        alpha_threshold: int = 128,
        return_original_size: bool = False,
    ) -> Image.Image:
        """
        Run the full restoration pipeline P(I) = f_α( f_k( f_g(I) ) ).

        Args:
            target_size: Desired sprite resolution, e.g. (64, 64) or (32, 32).
            palette_size: Number of colours K for K-Means quantization.
            alpha_threshold: Alpha binarisation threshold τ (default 128).
            return_original_size: If True, upscales the result back to the
                original image dimensions using NN for side-by-side preview.

        Returns:
            Restored PIL Image.
        """
        if self.current_image is None:
            raise ValueError("No image loaded")

        start_time = time.time()

        original_size = self.original_image.size if (return_original_size and self.original_image) else None

        self.current_image = restore_pipeline(
            self.current_image,
            target_size=target_size,
            palette_size=palette_size,
            alpha_threshold=alpha_threshold,
            original_size=original_size,
        )

        processing_time = time.time() - start_time

        if self.original_image:
            self.last_metrics = compute_metrics(
                self.original_image, self.current_image, palette_size
            )
            print(f"Metrics: {json.dumps(self.last_metrics, indent=2)}")

        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type="restoration_pipeline",
                parameters={
                    "target_size": target_size,
                    "palette_size": palette_size,
                    "alpha_threshold": alpha_threshold,
                },
                processing_time=processing_time,
                metadata=self.last_metrics,
            )

        return self.current_image

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Return the metrics computed during the last restore() call."""
        return self.last_metrics

    # ------------------------------------------------------------------ #
    # Legacy block-based colour correction
    # ------------------------------------------------------------------ #

    def correct_colors(
        self,
        block_width: int = 4,
        block_height: int = 4,
        strategy: Strategies = Strategies.AVERAGE,
        tolerance: int = 1,
        shrink_output: bool = False,
    ) -> Image.Image:
        """Apply block-based colour correction (legacy method)."""
        if self.current_image is None:
            raise ValueError("No image loaded")

        start_time = time.time()

        if self.current_image.mode != "RGBA":
            img_data = np.array(self.current_image.convert("RGBA"))
        else:
            img_data = np.array(self.current_image)

        processed, height, width = self._fix_image(
            img_data,
            self.current_image.height,
            self.current_image.width,
            block_width,
            block_height,
            strategy,
            tolerance,
            shrink_output,
        )

        if processed.dtype != np.uint8:
            processed = processed.astype(np.uint8)

        if processed.ndim == 3 and processed.shape[2] == 4:
            self.current_image = Image.fromarray(processed, "RGBA")
        elif processed.ndim == 3 and processed.shape[2] == 3:
            self.current_image = Image.fromarray(processed, "RGB")
        else:
            self.current_image = Image.fromarray(processed)

        processing_time = time.time() - start_time

        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type="color_correction",
                parameters={
                    "block_width": block_width,
                    "block_height": block_height,
                    "strategy": strategy.name,
                    "tolerance": tolerance,
                    "shrink_output": shrink_output,
                },
                processing_time=processing_time,
            )

        return self.current_image

    # ------------------------------------------------------------------ #
    # Legacy effects
    # ------------------------------------------------------------------ #

    def pixelate(self, pixel_size: int = 256) -> Image.Image:
        """Apply pixelation effect."""
        if self.current_image is None:
            raise ValueError("No image loaded")

        start_time = time.time()
        self.current_image = apply_pixelation(self.current_image, pixel_size)
        processing_time = time.time() - start_time

        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type="pixelation",
                parameters={"pixel_size": pixel_size},
                processing_time=processing_time,
            )
        return self.current_image

    def dither(self, levels: int = 10) -> Image.Image:
        """Apply Floyd-Steinberg dithering."""
        if self.current_image is None:
            raise ValueError("No image loaded")

        start_time = time.time()
        self.current_image = apply_dithering(self.current_image, levels)
        processing_time = time.time() - start_time

        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type="dithering",
                parameters={"levels": levels},
                processing_time=processing_time,
            )
        return self.current_image

    def reduce_palette(self, num_colors: int = 32) -> Image.Image:
        """Apply median palette reduction."""
        if self.current_image is None:
            raise ValueError("No image loaded")

        start_time = time.time()
        self.current_image = apply_median_palette(self.current_image, num_colors)
        processing_time = time.time() - start_time

        if self.auto_save_db and self.source_db_id:
            self._save_to_database(
                correction_type="palette_reduction",
                parameters={"num_colors": num_colors},
                processing_time=processing_time,
            )
        return self.current_image

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #

    def reset(self) -> None:
        """Reset the current image to the original."""
        if self.original_image is None:
            raise ValueError("No image loaded")
        self.current_image = self.original_image.copy()
        self.last_metrics = None

    def get_current_image(self) -> Image.Image:
        if self.current_image is None:
            raise ValueError("No image loaded")
        return self.current_image

    def get_original_image(self) -> Image.Image:
        if self.original_image is None:
            raise ValueError("No image loaded")
        return self.original_image

    def get_last_correction_db_id(self) -> Optional[int]:
        return self.last_correction_db_id

    def get_all_corrections(self) -> list:
        if not self.source_db_id:
            return []
        with get_session() as session:
            corrections = ImageRepository.get_corrected_images_by_source(
                session, self.source_db_id
            )
            return [corr.to_dict() for corr in corrections]

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _save_to_database(
        self,
        correction_type: str,
        parameters: Dict[str, Any],
        processing_time: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            with get_session() as session:
                original_prompt = None
                if self.source_db_id:
                    source = ImageRepository.get_generated_image(
                        session, self.source_db_id
                    )
                    if source:
                        original_prompt = source.prompt

                db_image = ImageRepository.save_corrected_image(
                    session=session,
                    image=self.current_image,
                    source_image_id=self.source_db_id,
                    correction_type=correction_type,
                    parameters=parameters,
                    original_prompt=original_prompt,
                    processing_time=processing_time,
                    metadata=metadata,
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
        shrink_output: bool = False,
    ) -> Tuple[np.ndarray, int, int]:
        """Process an image using block-based colour strategies (legacy)."""
        adjusted_width = (width // out_pix_width) * out_pix_width
        adjusted_height = (height // out_pix_height) * out_pix_height

        blocks = []
        for y in range(0, adjusted_height, out_pix_height):
            for x in range(0, adjusted_width, out_pix_width):
                block = image_data[y : y + out_pix_height, x : x + out_pix_width]
                blocks.append(block.reshape(-1, block.shape[-1]))

        processed_blocks = []
        for block in blocks:
            processed_block = self._process_block(block, strategy, tolerance)
            processed_blocks.append(processed_block)

        if shrink_output:
            out_height = adjusted_height // out_pix_height
            out_width = adjusted_width // out_pix_width
            out_data = np.array([block[0] for block in processed_blocks])
            out_data = out_data.reshape(out_height, out_width, -1)
        else:
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
        self, block: np.ndarray, strategy: Strategies, tolerance: int
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
