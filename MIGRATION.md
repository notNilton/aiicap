# Migration Guide - Functions to Modules

This guide helps you migrate from the deprecated `functions/` directory to the new modular architecture.

## ⚠️ Deprecation Notice

The `functions/` directory is **DEPRECATED** and will be removed in a future version. All functionality has been moved to the new `modules/` structure.

## 📋 Migration Mapping

### Complete Function Mapping

| Old Location                                               | New Location                                                          | Notes                     |
| ---------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------- |
| `functions.image_processor.floyd_steinberg()`              | `modules.image_correction.apply_dithering()`                          | Renamed for clarity       |
| `functions.image_processor.pixelate_image()`               | `modules.image_correction.apply_pixelation()`                         | Renamed for clarity       |
| `functions.image_processor.apply_median_palette()`         | `modules.image_correction.apply_median_palette()`                     | Same name                 |
| `functions.image_processor.fix_image()`                    | `modules.image_correction.ImageCorrector.correct_colors()`            | Now a class method        |
| `functions.image_processor.get_average_of_colors()`        | `modules.image_correction.color_utils.get_average_of_colors()`        | Moved to color_utils      |
| `functions.image_processor.get_harmonic_mean_of_colors()`  | `modules.image_correction.color_utils.get_harmonic_mean_of_colors()`  | Moved to color_utils      |
| `functions.image_processor.get_geometric_mean_of_colors()` | `modules.image_correction.color_utils.get_geometric_mean_of_colors()` | Moved to color_utils      |
| `functions.image_processor.get_midrange_of_colors()`       | `modules.image_correction.color_utils.get_midrange_of_colors()`       | Moved to color_utils      |
| `functions.image_processor.get_quadratic_mean_of_colors()` | `modules.image_correction.color_utils.get_quadratic_mean_of_colors()` | Moved to color_utils      |
| `functions.image_processor.get_cubic_mean_of_colors()`     | `modules.image_correction.color_utils.get_cubic_mean_of_colors()`     | Moved to color_utils      |
| `functions.image_processor.get_majority_color()`           | `modules.image_correction.color_utils.get_majority_color()`           | Moved to color_utils      |
| `functions.strategies.Strategies`                          | `modules.image_correction.Strategies`                                 | Moved to image_correction |
| `functions.utils.save_image()`                             | `modules.common.save_image()`                                         | Same signature            |
| `functions.utils.load_images()`                            | `modules.common.display_images()`                                     | Renamed for clarity       |

## 🔄 Migration Examples

### Example 1: Simple Function Calls

**Before:**

```python
from functions.image_processor import floyd_steinberg, pixelate_image
from functions.utils import save_image

# Apply effects
dithered = floyd_steinberg(image)
pixelated = pixelate_image(image, pixel_size=128)

# Save
save_image(dithered, "./output/", "dithered.png")
```

**After:**

```python
from modules.image_correction import apply_dithering, apply_pixelation
from modules.common import save_image

# Apply effects
dithered = apply_dithering(image, levels=10)
pixelated = apply_pixelation(image, pixel_size=128)

# Save
save_image(dithered, "./output/", "dithered.png")
```

### Example 2: Using fix_image

**Before:**

```python
from functions.image_processor import fix_image
from functions.strategies import Strategies
import numpy as np

img_data = np.array(image)
processed, h, w = fix_image(
    img_data,
    image.height,
    image.width,
    out_pix_width=4,
    out_pix_height=4,
    strategy=Strategies.AVERAGE
)
```

**After:**

```python
from modules.image_correction import ImageCorrector, Strategies

corrector = ImageCorrector(image)
corrected = corrector.correct_colors(
    block_width=4,
    block_height=4,
    strategy=Strategies.AVERAGE
)
```

### Example 3: Using Color Utilities

**Before:**

```python
from functions.image_processor import (
    get_average_of_colors,
    get_majority_color
)

avg_color = get_average_of_colors(pixels)
maj_color, count = get_majority_color(pixels, tolerance=1)
```

**After:**

```python
from modules.image_correction.color_utils import (
    get_average_of_colors,
    get_majority_color
)

avg_color = get_average_of_colors(pixels)
maj_color, count = get_majority_color(pixels, tolerance=1)
```

### Example 4: Using the High-Level API (Recommended)

**New Approach:**

```python
from modules.image_correction import ImageCorrector

# Initialize corrector with image
corrector = ImageCorrector()
corrector.load_image("path/to/image.png")

# Chain multiple corrections
corrector.pixelate(pixel_size=128)
corrector.dither(levels=10)
corrector.reduce_palette(num_colors=32)
corrector.correct_colors(strategy=Strategies.AVERAGE)

# Get result
result = corrector.get_current_image()
result.save("output.png")
```

## ⚡ Quick Migration Steps

1. **Find and Replace Imports**:

   ```bash
   # In your project, replace:
   from functions.image_processor import -> from modules.image_correction import
   from functions.strategies import -> from modules.image_correction import
   from functions.utils import -> from modules.common import
   ```

2. **Update Function Names**:

   - `floyd_steinberg()` → `apply_dithering()`
   - `pixelate_image()` → `apply_pixelation()`
   - `fix_image()` → Use `ImageCorrector.correct_colors()`
   - `load_images()` → `display_images()`

3. **Refactor fix_image() Usage**:

   - Convert to object-oriented approach using `ImageCorrector` class
   - This provides better state management and chaining capabilities

4. **Test Your Code**:
   ```bash
   python -Wall your_script.py  # Will show deprecation warnings
   ```

## 🎯 Benefits of Migration

- **Better Organization**: Clear separation between generation and correction
- **Object-Oriented**: ImageCorrector class provides better state management
- **Future-Proof**: New modules will receive updates and improvements
- **Cleaner API**: More intuitive function and class names
- **Extensibility**: Easier to add new features in modular structure

## ⏰ Timeline

- **Now**: `functions/` is deprecated but still works (with warnings)
- **Next Release**: Backwards compatibility maintained
- **Future Release**: `functions/` directory will be removed

## 🆘 Need Help?

If you encounter issues during migration:

1. Check the examples above
2. Review the module documentation in README.md
3. Look at the updated `main.py` for reference
4. Open an issue on GitHub

## ✅ Migration Checklist

- [ ] Update all `from functions.*` imports
- [ ] Replace `floyd_steinberg` with `apply_dithering`
- [ ] Replace `pixelate_image` with `apply_pixelation`
- [ ] Convert `fix_image()` calls to `ImageCorrector.correct_colors()`
- [ ] Update `load_images` to `display_images`
- [ ] Update color utility imports to `color_utils`
- [ ] Test all functionality
- [ ] Remove any direct imports from `functions/`
- [ ] Run with `-Wall` to check for deprecation warnings
