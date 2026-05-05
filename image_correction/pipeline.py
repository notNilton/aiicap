"""
Deterministic restoration pipeline from the article.

P(I) = f_α( f_k( f_g(I) ) )

1. Geometric Grid Reconstruction (Nearest-Neighbor resampling)
2. Chromatic Quantization (K-Means with k-means++ initialization)
3. Opacity Binarization (threshold τ = 128)
"""

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def geometric_reconstruction(
    image: Image.Image, target_size: tuple[int, int]
) -> Image.Image:
    """
    Stage 1: Nearest-Neighbor resampling to restore the discrete grid
    and eliminate mixels.

    For an input image I_in and target resolution W_out × H_out:
        I_out(x,y) = I_in( floor(x * W_in/W_out + 0.5),
                           floor(y * H_in/H_out + 0.5) )

    Args:
        image: Input PIL Image.
        target_size: (width, height) of the desired sprite resolution.

    Returns:
        Resampled PIL Image with sharp, grid-aligned pixels.
    """
    return image.resize(target_size, Image.Resampling.NEAREST)


def chromatic_quantization(image: Image.Image, palette_size: int) -> Image.Image:
    """
    Stage 2: K-Means color quantization in RGB space.

    Finds K centroids {μ_1, …, μ_k} that minimise the sum of squared
    Euclidean distances from each pixel to its nearest centroid.

    Args:
        image: PIL Image (RGB or RGBA).
        palette_size: Number of palette colours K.

    Returns:
        Quantised PIL Image where every pixel maps to one of the K centroids.
    """
    img_array = np.array(image)
    h, w = img_array.shape[:2]
    pixels = img_array.reshape(-1, img_array.shape[2])

    has_alpha = img_array.shape[2] == 4

    if has_alpha:
        rgb = pixels[:, :3].astype(np.float32)
        alpha = pixels[:, 3:4].copy()

        kmeans = KMeans(
            n_clusters=palette_size,
            init="k-means++",
            random_state=0,
            n_init=10,
        ).fit(rgb)

        quantized_rgb = kmeans.cluster_centers_[kmeans.labels_].astype(np.uint8)
        result = np.concatenate([quantized_rgb, alpha], axis=1).reshape(h, w, 4)
    else:
        rgb = pixels.astype(np.float32)
        kmeans = KMeans(
            n_clusters=palette_size,
            init="k-means++",
            random_state=0,
            n_init=10,
        ).fit(rgb)
        result = kmeans.cluster_centers_[kmeans.labels_].astype(np.uint8).reshape(h, w, -1)

    return Image.fromarray(result)


def alpha_binarization(image: Image.Image, tau: int = 128) -> Image.Image:
    """
    Stage 3: Binarize the alpha channel.

    Given input alpha A_in:
        A_out(u,v) = 255  if A_in(u,v) ≥ τ
        A_out(u,v) = 0    if A_in(u,v) < τ

    τ = 128 is adopted based on technical sprite standards.

    Args:
        image: PIL Image.
        tau: Threshold (default 128).

    Returns:
        PIL Image with binarised alpha (RGBA) or unchanged (RGB).
    """
    if image.mode != "RGBA":
        return image

    data = np.array(image)
    data[..., 3] = np.where(data[..., 3] >= tau, 255, 0).astype(np.uint8)
    return Image.fromarray(data, "RGBA")


def restore(
    image: Image.Image,
    target_size: tuple[int, int],
    palette_size: int,
    alpha_threshold: int = 128,
    original_size: tuple[int, int] | None = None,
) -> Image.Image:
    """
    Run the full restoration pipeline P(I) = f_α( f_k( f_g(I) ) ).

    Args:
        image: Input PIL Image.
        target_size: Desired sprite resolution (e.g. (64, 64)).
        palette_size: Number of colours K for K-Means.
        alpha_threshold: Alpha binarisation threshold τ.
        original_size: If provided, the processed sprite is upscaled back to
            this size using Nearest-Neighbour so the preview matches the
            original dimensions while keeping the pixel-art look.

    Returns:
        Restored PIL Image (engine-ready sprite, or preview-sized if
        original_size is set).
    """
    # Normalise mode so alpha handling is well-defined
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA") if image.mode in ("P", "LA", "L", "PA") else image.convert("RGB")

    # 1. Geometric reconstruction
    img = geometric_reconstruction(image, target_size)

    # 2. Chromatic quantization
    img = chromatic_quantization(img, palette_size)

    # 3. Alpha binarization
    img = alpha_binarization(img, alpha_threshold)

    # Optional: upscale back for side-by-side preview
    if original_size is not None:
        img = img.resize(original_size, Image.Resampling.NEAREST)

    return img
