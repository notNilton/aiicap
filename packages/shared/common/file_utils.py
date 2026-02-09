"""
File utilities for image loading and saving
"""

import os
from PIL import Image
from typing import Union


def save_image(image: Image.Image, save_path: str, filename: str) -> None:
    """
    Save a PIL Image object to the specified directory with a given filename.
    
    Args:
        image: PIL Image to save
        save_path: Directory path where image will be saved
        filename: Name of the file (including extension)
    
    Raises:
        Exception: If image cannot be saved
    """
    try:
        os.makedirs(save_path, exist_ok=True)  # Create directory if it doesn't exist
        full_path = os.path.join(save_path, filename)  # Join path and filename
        image.save(full_path)
        print(f"Image saved successfully at {full_path}")
    except Exception as e:
        print(f"Error saving the image: {e}")
        raise


def load_image(image_path: str) -> Image.Image:
    """
    Load an image from the specified path.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        PIL Image object
    
    Raises:
        FileNotFoundError: If image file doesn't exist
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    return Image.open(image_path)
