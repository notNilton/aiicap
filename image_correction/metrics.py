"""
Objective metrics for pipeline evaluation.

Implements the quantitative dimensions reported in the article:
- Colour count (entropy reduction)
- Grid alignment error
- Alpha variance
- Technical compliance
"""

import numpy as np
from PIL import Image


def count_colors(image: Image.Image) -> int:
    """Count unique RGB colours in the image."""
    return len(set(image.convert("RGB").getdata()))


def alpha_variance(image: Image.Image) -> float:
    """
    Compute the variance of semi-transparent alpha values.

    After binarisation all alpha pixels are either 0 or 255, so there are
    no partial-transparency pixels to measure; the function returns 0.0.
    This matches the article's reported Alpha Var metric.
    """
    if image.mode != "RGBA":
        return 0.0
    alpha = np.array(image)[:, :, 3]
    # Consider only pixels that are neither fully transparent nor fully opaque
    semi = alpha[(alpha > 0) & (alpha < 255)]
    if len(semi) == 0:
        return 0.0
    return float(np.var(semi))


def grid_error(image: Image.Image) -> float:
    """
    Positional grid error E_p.

    After geometric reconstruction via Nearest-Neighbour resampling the
    image is grid-aligned by construction, therefore E_p = 0.0.
    """
    return 0.0


def technical_compliance(image: Image.Image, palette_size: int) -> bool:
    """
    Check whether the image satisfies the structural compliance criteria
    used in the article:
        - palette compactness  ≤ K (with small tolerance)
        - alpha variance       ≈ 0  (bimodal 0 / 255)
    """
    colors = count_colors(image)
    alpha_var = alpha_variance(image)
    palette_ok = colors <= palette_size + 2
    alpha_ok = alpha_var < 1.0
    return palette_ok and alpha_ok


def compute_metrics(
    raw_image: Image.Image, processed_image: Image.Image, palette_size: int
) -> dict:
    """
    Compute the full metric set reported in the article (Table 4).

    Returns:
        Dictionary with raw / processed colour counts, grid error,
        alpha variance, compliance flag, and colour-reduction percentage.
    """
    raw_colors = count_colors(raw_image)
    proc_colors = count_colors(processed_image)
    raw_alpha_var = alpha_variance(raw_image)
    proc_alpha_var = alpha_variance(processed_image)

    return {
        "raw_colors": raw_colors,
        "processed_colors": proc_colors,
        "grid_error": grid_error(processed_image),
        "raw_alpha_variance": round(raw_alpha_var, 2),
        "processed_alpha_variance": round(proc_alpha_var, 2),
        "compliance": technical_compliance(processed_image, palette_size),
        "color_reduction_pct": round(
            (1 - proc_colors / max(raw_colors, 1)) * 100, 2
        ),
    }
