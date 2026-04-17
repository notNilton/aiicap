"""
Image effects and filters for generation module
"""

import numpy as np
from PIL import Image
from sklearn.cluster import MiniBatchKMeans
import warnings


def apply_pixelation(image: Image.Image, pixel_size: int = 256) -> Image.Image:
    """
    Pixelates the image by reducing it to the specified pixel dimensions 
    and scaling it back up using nearest neighbor interpolation.
    
    Args:
        image: Original PIL Image
        pixel_size: The desired pixel block size (e.g., 64 = 64x64 pixels)
                   Common values: 256, 128, 64, 32, 16
    
    Returns:
        Pixelated PIL Image with original colors
    """
    width, height = image.size
    
    # Calculate new dimensions maintaining aspect ratio
    aspect_ratio = width / height
    if width > height:
        new_width = pixel_size
        new_height = int(pixel_size / aspect_ratio)
    else:
        new_height = pixel_size
        new_width = int(pixel_size * aspect_ratio)
    
    # Ensure minimum dimension is at least 1 pixel
    new_width = max(1, new_width)
    new_height = max(1, new_height)
    
    # Reduce resolution and scale back up
    small_image = image.resize((new_width, new_height), Image.NEAREST)
    pixelated_image = small_image.resize((width, height), Image.NEAREST)
    
    return pixelated_image


def apply_dithering(image: Image.Image, levels: int = 10) -> Image.Image:
    """
    Applies Floyd-Steinberg dithering to RGB images with reduced palette.
    
    Args:
        image: Original PIL Image
        levels: Number of quantization levels (default: 10)
    
    Returns:
        Dithered PIL Image
    """
    # Convert image to numpy array
    pixels = np.array(image, dtype=float)
    width, height = image.size
    
    # Calculate quantization step
    step = 255.0 / (levels - 1)
    
    # Iterate over each pixel
    for y in range(height - 1):  # Avoid exceeding bounds
        for x in range(1, width - 1):  # Avoid exceeding bounds
            # Process each color channel (R, G, B)
            for c in range(3):
                old_pixel = pixels[y, x, c]
                
                # Quantize pixel to nearest level
                new_pixel = round(old_pixel / step) * step
                new_pixel = np.clip(new_pixel, 0, 255)
                
                # Set new pixel value
                pixels[y, x, c] = new_pixel
                
                # Calculate quantization error
                error = old_pixel - new_pixel
                
                # Distribute error to neighbors
                pixels[y, x + 1, c] += error * 7 / 16  # Right
                pixels[y + 1, x - 1, c] += error * 3 / 16  # Bottom-left
                pixels[y + 1, x, c] += error * 5 / 16  # Bottom
                pixels[y + 1, x + 1, c] += error * 1 / 16  # Bottom-right
    
    # Ensure pixel values are in range [0, 255]
    pixels = np.clip(pixels, 0, 255)
    
    # Convert array back to PIL Image
    return Image.fromarray(pixels.astype(np.uint8), mode="RGB")


def apply_median_palette(image: Image.Image, num_colors: int = 32) -> Image.Image:
    """
    Quantize the image using clustered colors.
    More efficient implementation using direct cluster centers.
    
    Args:
        image: Original PIL Image
        num_colors: Number of colors in the reduced palette
    
    Returns:
        Palette-reduced PIL Image
    """
    # Get the cluster colors
    palette_colors = _get_dominant_colors(image, num_colors)
    
    # Create a palette image
    palette = Image.new("P", (1, 1))
    palette_data = [color for rgb in palette_colors for color in rgb]
    # Pad palette with black if needed
    palette_data += [0] * (256 * 3 - len(palette_data))
    palette.putpalette(palette_data)
    
    # Quantize the image using the custom palette
    quantized = image.convert("RGB").quantize(palette=palette, dither=Image.NONE)
    return quantized.convert("RGB")


def _get_dominant_colors(image: Image.Image, num_colors: int) -> list:
    """
    Extract dominant colors by clustering and return median colors of each cluster.
    Uses MiniBatchKMeans which is more memory efficient.
    
    Args:
        image: PIL Image
        num_colors: Number of dominant colors to extract
    
    Returns:
        List of RGB tuples representing dominant colors
    """
    # Convert image to numpy array
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # Suppress KMeans warnings
        img_array = np.array(image.convert("RGB"))
        h, w, _ = img_array.shape
        
        # Reshape to 2D array of pixels (sample if too large)
        pixels = img_array.reshape((h * w, 3))
        
        # For large images, use a subset of pixels
        if len(pixels) > 10000:
            rng = np.random.default_rng()
            pixels = rng.choice(pixels, size=10000, replace=False)
        
        # Use MiniBatchKMeans which is more efficient
        kmeans = MiniBatchKMeans(
            n_clusters=num_colors, 
            random_state=0,
            batch_size=256,
            compute_labels=True
        ).fit(pixels)
        
        # Get cluster centers (already computed efficiently)
        cluster_colors = kmeans.cluster_centers_.astype(int)
        
        return [tuple(color) for color in cluster_colors]


def count_colors(image: Image.Image) -> int:
    """
    Count the number of unique colors in an image.
    
    Args:
        image: PIL Image
    
    Returns:
        Number of unique colors
    """
    return len(set(image.getdata()))
