# Quick Reference Guide

## 📚 Module Import Cheatsheet

### Image Correction

```python
# High-level API (Recommended)
from modules.image_correction import ImageCorrector, Strategies

corrector = ImageCorrector()
corrector.load_image("path/to/image.png")
corrector.pixelate(pixel_size=128)
corrector.dither(levels=10)
corrector.reduce_palette(num_colors=32)
corrector.correct_colors(strategy=Strategies.AVERAGE)
result = corrector.get_current_image()
```

```python
# Functional API
from modules.image_correction import (
    apply_pixelation,
    apply_dithering,
    apply_median_palette,
    Strategies
)

img = apply_pixelation(img, pixel_size=128)
img = apply_dithering(img, levels=10)
img = apply_median_palette(img, num_colors=32)
```

```python
# Low-level color utilities
from modules.image_correction.color_utils import (
    get_average_of_colors,
    get_harmonic_mean_of_colors,
    get_geometric_mean_of_colors,
    get_midrange_of_colors,
    get_quadratic_mean_of_colors,
    get_cubic_mean_of_colors,
    get_majority_color
)
```

### Image Generation (AI)

```python
# ChatGPT API (DALL-E) Integration
from modules.image_generation import ImageGenerator
import os

os.environ['OPENAI_API_KEY'] = 'your-api-key'
generator = ImageGenerator()

# Generate from prompt
image = generator.generate(
    prompt="A medieval landscape",
    size="1024x1024",
    quality="hd"
)

# Create variations
variation = generator.generate_variation(image)

# Get last generated
last = generator.get_last_image()
```

### Common Utilities

```python
# File operations
from modules.common import save_image, load_image

img = load_image("path/to/image.png")
save_image(img, "./output/", "result.png")
```

```python
# Display utilities
from modules.common import display_images

display_images(img1, img2, img3)  # Shows in Tkinter window
```

## 🎨 Available Strategies

```python
from modules.image_correction import Strategies

# Statistical strategies
Strategies.AVERAGE      # Arithmetic mean
Strategies.HARMONIC     # Harmonic mean
Strategies.GEOMETRIC    # Geometric mean
Strategies.MIDRANGE     # (min + max) / 2
Strategies.QUADRATIC    # RMS (Root Mean Square)
Strategies.CUBIC        # Cubic mean
Strategies.MAJORITY     # Most common color

# Algorithm-based (coverage thresholds)
Strategies.ALG05        # 5% coverage
Strategies.ALG10        # 10% coverage
Strategies.ALG20        # 20% coverage
Strategies.ALG30        # 30% coverage
Strategies.ALG40        # 40% coverage
Strategies.ALG50        # 50% coverage
Strategies.ALG60        # 60% coverage
Strategies.ALG70        # 70% coverage
Strategies.ALG80        # 80% coverage
Strategies.ALG90        # 90% coverage
```

## 🔧 Common Workflows

### Workflow 1: Basic Correction Chain

```python
from modules.image_correction import ImageCorrector, Strategies
from modules.common import save_image

# Initialize and load
corrector = ImageCorrector()
corrector.load_image("input.png")

# Apply corrections in sequence
corrector.pixelate(pixel_size=256)      # Step 1: Pixelate
corrector.dither(levels=10)              # Step 2: Dither
corrector.reduce_palette(num_colors=16)  # Step 3: Reduce colors

# Save result
result = corrector.get_current_image()
save_image(result, "./output/", "corrected.png")
```

### Workflow 2: Multiple Strategy Comparison

```python
from modules.image_correction import ImageCorrector, Strategies
from modules.common import save_image

corrector = ImageCorrector()
corrector.load_image("input.png")

strategies = [
    Strategies.AVERAGE,
    Strategies.HARMONIC,
    Strategies.GEOMETRIC,
    Strategies.MAJORITY
]

for strategy in strategies:
    corrector.reset()  # Reset to original
    corrector.correct_colors(
        block_width=4,
        block_height=4,
        strategy=strategy
    )
    result = corrector.get_current_image()
    save_image(result, "./output/", f"corrected_{strategy.name}.png")
```

### Workflow 3: AI Generation + Correction

```python
from modules.image_generation import ImageGenerator
from modules.image_correction import ImageCorrector
from modules.common import save_image

# Generate with AI
generator = ImageGenerator(api_key="your-key")
generated = generator.generate("A medieval castle")

# Apply corrections
corrector = ImageCorrector(generated)
corrector.pixelate(pixel_size=128)
corrector.dither(levels=8)

# Save
result = corrector.get_current_image()
save_image(result, "./output/", "ai_corrected.png")
```

## 📝 Parameter Reference

### `ImageCorrector` Methods

```python
# pixelate(pixel_size: int = 256)
corrector.pixelate(pixel_size=128)  # Smaller = more pixelated

# dither(levels: int = 10)
corrector.dither(levels=5)  # Fewer levels = more dithering

# reduce_palette(num_colors: int = 32)
corrector.reduce_palette(num_colors=8)  # Fewer colors = more dramatic

# correct_colors(...)
corrector.correct_colors(
    block_width=4,         # Width of processing blocks
    block_height=4,        # Height of processing blocks
    strategy=Strategies.AVERAGE,  # Color strategy
    tolerance=1,           # Color matching tolerance (for MAJORITY)
    shrink_output=False    # If True, output 1 pixel per block
)
```

### Individual Functions

```python
# apply_pixelation(image, pixel_size)
from modules.image_correction import apply_pixelation
result = apply_pixelation(img, pixel_size=256)

# apply_dithering(image, levels)
from modules.image_correction import apply_dithering
result = apply_dithering(img, levels=10)

# apply_median_palette(image, num_colors)
from modules.image_correction import apply_median_palette
result = apply_median_palette(img, num_colors=32)
```

## 🚫 What NOT to Import

```python
# ❌ DEPRECATED - Don't use these
from functions.image_processor import floyd_steinberg
from functions.strategies import Strategies
from functions.utils import save_image

# ✅ Use these instead
from modules.image_correction import apply_dithering, Strategies
from modules.common import save_image
```

## 🐛 Troubleshooting

### Import Errors

```python
# If you get: ModuleNotFoundError: No module named 'modules'
# Make sure you're running from the project root:
cd /path/to/aiicap
python3 main.py
```

### Deprecation Warnings

```python
# If you see deprecation warnings:
# Update your imports from 'functions' to 'modules'
# See MIGRATION.md for details
```

### Missing Dependencies

```bash
# Install all dependencies:
pip install -r requirements.txt

# For AI generation:
pip install openai
```

## 📖 More Information

- Full documentation: [README.md](README.md)
- Migration guide: [MIGRATION.md](MIGRATION.md)
- Refactoring details: [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
