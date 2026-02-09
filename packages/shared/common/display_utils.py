"""
Display utilities for image viewing
"""

from PIL import Image, ImageTk
import tkinter as tk
from typing import List


def display_images(*images: Image.Image) -> None:
    """
    Load and display multiple images in a Tkinter window, resized to a maximum of 600x600.
    
    Args:
        *images: Variable number of PIL Image objects to display
    
    Raises:
        Exception: If images cannot be displayed
    """
    try:
        window = tk.Tk()
        window.title("Image Viewer")

        # Resize images if necessary
        max_size = (600, 600)

        # For each image, resize and display
        for image in images:
            display_img = image.copy()
            display_img.thumbnail(max_size)  # Resize the image
            tk_image = ImageTk.PhotoImage(display_img)  # Convert to Tkinter format

            label = tk.Label(window, image=tk_image)
            label.pack(side=tk.LEFT)
            label.image = tk_image  # Keep a reference to avoid garbage collection

        window.mainloop()
    except Exception as e:
        print(f"Error displaying images: {e}")
        raise
