"""
Image Correction Module

This module handles all image correction operations including:
- Color correction using various strategies
- Pixelation effects
- Floyd-Steinberg dithering
- Median palette reduction
- Block-based processing
"""

from .corrector import ImageCorrector
from .strategies import Strategies
from .effects import (
    apply_pixelation,
    apply_dithering,
    apply_median_palette
)
from .color_utils import (
    get_average_of_colors,
    get_harmonic_mean_of_colors,
    get_geometric_mean_of_colors,
    get_midrange_of_colors,
    get_quadratic_mean_of_colors,
    get_cubic_mean_of_colors,
    get_majority_color
)

__all__ = [
    'ImageCorrector',
    'Strategies',
    'apply_pixelation',
    'apply_dithering',
    'apply_median_palette',
    'get_average_of_colors',
    'get_harmonic_mean_of_colors',
    'get_geometric_mean_of_colors',
    'get_midrange_of_colors',
    'get_quadratic_mean_of_colors',
    'get_cubic_mean_of_colors',
    'get_majority_color'
]
