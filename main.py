"""
Image Processor GUI Application

Main application using modular architecture:
- modules.image_generation: AI-powered image generation via ChatGPT API (DALL-E)
- modules.image_correction: Image correction techniques (dithering, pixelation, palette reduction, color fixing)
- modules.api_service: API integrations (to be implemented)
"""

from PIL import Image, ImageTk
import tkinter as tk
import os

# Import from new modular structure
from modules.image_generation import ImageGenerator
from modules.image_correction import ImageCorrector, Strategies
from modules.common import save_image


class ImageProcessorApp:
    """Main GUI application for image processing"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor - Modular Edition")
        
        # Image paths
        self.original_image_path = "./data/untreated/medieval-landscape.png"
        self.processed_image_path = "./data/treated/"
        
        # Initialize modules
        self.generator = ImageGenerator()  # For AI image generation
        self.corrector = ImageCorrector()   # For image correction
        
        # Load and store the original image in RGB mode
        try:
            input_image = Image.open(self.original_image_path)
            self.original_image = input_image.convert("RGB")
            self.current_image = self.original_image.copy()
            
            # Set image in corrector
            self.corrector.set_image(self.original_image)
        except FileNotFoundError:
            print(f"Error: File not found at {self.original_image_path}")
            exit()
        
        # Create image display frame
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack()
        
        # Display the original image
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()
        self.display_image(self.current_image)
        
        # Create buttons
        self.create_buttons()
    
    def display_image(self, image):
        """Display the image in the GUI without modifying the original."""
        # Create a copy for display
        display_image = image.copy()
        
        # Calculate maximum display size while maintaining aspect ratio
        max_width, max_height = 800, 600
        width, height = display_image.size
        ratio = min(max_width/width, max_height/height)
        new_size = (int(width * ratio), int(height * ratio))
        
        # Resize for display
        display_image = display_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to Tkinter format
        self.tk_image = ImageTk.PhotoImage(display_image)
        
        # Update the image label
        self.image_label.config(image=self.tk_image)
        self.image_label.image = self.tk_image  # Keep a reference
    
    def create_buttons(self):
        """Create application buttons."""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Image Correction section
        correction_label = tk.Label(button_frame, text="Image Correction:", font=("Arial", 10, "bold"))
        correction_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame, text="Pixelation", 
            command=self.apply_pixelation,
            bg="#4CAF50", fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, text="Dithering", 
            command=self.apply_dithering,
            bg="#4CAF50", fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, text="Reduce Palette", 
            command=self.apply_palette_reduction,
            bg="#4CAF50", fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, text="Color Correction", 
            command=self.apply_color_correction,
            bg="#2196F3", fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Strategy selection for color correction
        self.strategy_var = tk.StringVar(value=Strategies.AVERAGE.name)
        tk.OptionMenu(
            button_frame, 
            self.strategy_var, 
            *[s.name for s in Strategies]
        ).pack(side=tk.LEFT, padx=5)
        
        # Reset button
        tk.Button(
            button_frame, text="Reset", 
            command=self.reset_to_original,
            bg="#f44336", fg="white"
        ).pack(side=tk.LEFT, padx=5)
    
    def apply_pixelation(self):
        """Apply pixelation using the image correction module."""
        try:
            # Update corrector with current image
            self.corrector.set_image(self.current_image)
            
            # Apply effect
            pixelated_image = self.corrector.pixelate(pixel_size=256)
            
            # Update current image
            self.current_image = pixelated_image
            self.display_image(self.current_image)
            self.save_current_image("pixelated")
        except Exception as e:
            print(f"Error applying pixelation: {e}")
    
    def apply_dithering(self):
        """Apply dithering using the image correction module."""
        try:
            # Update corrector with current image
            self.corrector.set_image(self.current_image)
            
            # Apply effect
            dithered_image = self.corrector.dither(levels=10)
            
            # Update current image
            self.current_image = dithered_image
            self.display_image(self.current_image)
            self.save_current_image("dithered")
        except Exception as e:
            print(f"Error applying dithering: {e}")
    
    def apply_palette_reduction(self):
        """Apply median palette reduction using the image correction module."""
        try:
            # Update corrector with current image
            self.corrector.set_image(self.current_image)
            
            # Apply effect
            reduced_image = self.corrector.reduce_palette(num_colors=32)
            
            # Update current image
            self.current_image = reduced_image
            self.display_image(self.current_image)
            self.save_current_image("palette_reduced")
        except Exception as e:
            print(f"Error applying palette reduction: {e}")
    
    def apply_color_correction(self):
        """Apply color correction using the image correction module."""
        try:
            # Update corrector with current image
            self.corrector.set_image(self.current_image)
            
            # Get selected strategy
            strategy = Strategies[self.strategy_var.get()]
            
            # Apply correction
            corrected_image = self.corrector.correct_colors(
                block_width=4,
                block_height=4,
                strategy=strategy,
                tolerance=1,
                shrink_output=False
            )
            
            # Update current image
            self.current_image = corrected_image
            self.display_image(self.current_image)
            self.save_current_image(f"color_corrected_{strategy.name.lower()}")
        except Exception as e:
            print(f"Error applying color correction: {e}")
    
    def reset_to_original(self):
        """Reset the current image to the original state."""
        self.current_image = self.original_image.copy()
        self.corrector.reset()
        self.display_image(self.current_image)
    
    def save_current_image(self, suffix):
        """Save the current processed image."""
        try:
            filename = os.path.basename(self.original_image_path)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_{suffix}{ext}"
            
            # Use common save_image utility
            save_image(self.current_image, self.processed_image_path, output_filename)
        except Exception as e:
            print(f"Error saving image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()