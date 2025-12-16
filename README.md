# AIICAP - Artificial Intelligence Image Correction and Processing

A modular Python-based image processing application with GUI support for various image manipulation techniques including pixelation, dithering, palette reduction, and advanced color correction. Now with planned support for AI-powered image generation via ChatGPT API.

## 🏗️ Architecture

The application follows a **modular architecture** with clear separation of concerns:

```
aiicap/
├── modules/                      # Core modules (NEW)
│   ├── image_generation/         # AI-powered image generation
│   │   ├── __init__.py
│   │   └── generator.py          # ChatGPT/DALL-E API integration
│   ├── image_correction/         # Image correction techniques
│   │   ├── __init__.py
│   │   ├── corrector.py          # ImageCorrector class
│   │   ├── effects.py            # Pixelation, dithering, palette reduction
│   │   ├── strategies.py         # Color processing strategies
│   │   └── color_utils.py        # Color calculation functions
│   ├── api_service/              # API integrations (planned)
│   │   └── __init__.py
│   └── common/                   # Shared utilities
│       ├── __init__.py
│       ├── file_utils.py         # Image I/O operations
│       └── display_utils.py      # Image display utilities
├── functions/                    # ⚠️ DEPRECATED - See MIGRATION.md
├── data/
│   ├── untreated/               # Input images
│   └── treated/                 # Output images
├── main.py                      # GUI application
├── requirements.txt
├── README.md
└── MIGRATION.md                 # Migration guide from old structure
```

## ⚠️ Important Notice

**The `functions/` directory is DEPRECATED.** All functionality has been moved to the new `modules/` structure. Please see [MIGRATION.md](MIGRATION.md) for a complete migration guide.

## ✨ Features

### Image Generation Module (AI-Powered)

- **DALL-E Integration**: Generate images from text prompts using ChatGPT API
- **Image Variations**: Create variations of existing images
- **Image Editing**: Edit images with masks and prompts
- **High Quality**: Support for standard and HD quality outputs

### Image Correction Module

- **Pixelation**: Reduce image resolution and scale back up for a blocky pixel art effect
- **Floyd-Steinberg Dithering**: Apply error-diffusion dithering to reduce color banding
- **Median Palette Reduction**: Quantize images to a reduced color palette using k-means clustering
- **Block-based Color Correction**: Process images in blocks with various strategies
- **Multiple Color Strategies**:
  - `AVERAGE`: Arithmetic mean of colors
  - `HARMONIC`: Harmonic mean of colors
  - `GEOMETRIC`: Geometric mean of colors
  - `MIDRANGE`: Midpoint between min and max colors
  - `QUADRATIC`: Quadratic mean (RMS) of colors
  - `CUBIC`: Cubic mean of colors
  - `MAJORITY`: Most common color in block
  - `ALG05-ALG90`: Algorithm-based strategies with coverage thresholds

### API Service Module (Planned)

- REST API integration for external image processing services
- Authentication and rate limiting
- Request/response handling

## 🚀 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/notNilton/orion-aiicap.git
   cd aiicap
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Or install them manually:

   ```bash
   pip install numpy opencv-python matplotlib numba scikit-learn Pillow
   ```

3. (Optional) For AI image generation, install OpenAI SDK:
   ```bash
   pip install openai
   ```

## 💻 Usage

### GUI Application

1. Place your input images in the `./data/untreated/` directory
2. Run the application:
   ```bash
   python main.py
   ```
3. Use the buttons to apply different effects:
   - **Image Correction** section (green buttons):
     - Pixelation
     - Dithering
     - Reduce Palette
     - Color Correction (with strategy selection)
   - **Reset**: Reverts to the original image

Processed images are automatically saved to `./data/treated/` with descriptive suffixes.

### Programmatic Usage

#### AI Image Generation (Planned)

```python
from modules.image_generation import ImageGenerator
import os

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Initialize generator
generator = ImageGenerator()

# Generate image from prompt
image = generator.generate(
    prompt="A serene medieval landscape with mountains and a castle",
    size="1024x1024",
    quality="hd"
)
image.save("generated_landscape.png")

# Create variations
variation = generator.generate_variation(image)
variation.save("variation.png")
```

#### Image Correction

```python
from modules.image_correction import ImageCorrector, Strategies

# Initialize corrector
corrector = ImageCorrector()
corrector.load_image("path/to/image.png")

# Apply multiple corrections (chaining)
corrector.pixelate(pixel_size=128)
corrector.dither(levels=10)
corrector.reduce_palette(num_colors=32)
corrector.correct_colors(
    block_width=4,
    block_height=4,
    strategy=Strategies.AVERAGE
)

# Get and save result
result = corrector.get_current_image()
result.save("corrected.png")

# Reset to apply different corrections
corrector.reset()
corrector.dither(levels=5)
```

#### Using Individual Functions

```python
from modules.image_correction import apply_pixelation, apply_dithering, apply_median_palette
from modules.common import load_image, save_image

# Load image
img = load_image("path/to/image.png")

# Apply effects
pixelated = apply_pixelation(img, pixel_size=64)
dithered = apply_dithering(img, levels=8)
palette_reduced = apply_median_palette(img, num_colors=16)

# Save results
save_image(pixelated, "./output/", "pixelated.png")
save_image(dithered, "./output/", "dithered.png")
save_image(palette_reduced, "./output/", "palette_reduced.png")
```

## 📦 Module Documentation

### `modules.image_generation`

**Status:** Planned - API integration ready for implementation

**Classes:**

- `ImageGenerator`: AI-powered image generation using ChatGPT API (DALL-E)

**Methods:**

- `generate(prompt, size, quality, n, model)`: Generate images from text prompts
- `generate_variation(image, n, size)`: Create variations of existing images
- `edit(image, mask, prompt, n, size)`: Edit images with masks

**Setup:**

1. Install OpenAI SDK: `pip install openai`
2. Set API key: `export OPENAI_API_KEY='your-key'`
3. Uncomment implementation code in `generator.py`

### `modules.image_correction`

**Classes:**

- `ImageCorrector`: High-level interface for all correction operations
- `Strategies`: Enum of available color processing strategies

**Functions:**

- `apply_pixelation(image, pixel_size)`: Apply pixelation effect
- `apply_dithering(image, levels)`: Apply Floyd-Steinberg dithering
- `apply_median_palette(image, num_colors)`: Apply palette reduction

**ImageCorrector Methods:**

- `pixelate(pixel_size)`: Apply pixelation
- `dither(levels)`: Apply dithering
- `reduce_palette(num_colors)`: Reduce color palette
- `correct_colors(block_width, block_height, strategy)`: Block-based color correction
- `reset()`: Reset to original image

**Color Utilities:**

- Various color mean calculations (average, harmonic, geometric, etc.)
- `get_majority_color(pixels, tolerance)`: Find most common color

### `modules.common`

**Functions:**

- `save_image(image, path, filename)`: Save PIL Image to file
- `load_image(path)`: Load image from file
- `display_images(*images)`: Display images in Tkinter window

### `modules.api_service`

**Status:** Planned for future implementation

## 🔧 Technical Details

### Implemented Algorithms

1. **Floyd-Steinberg Dithering**:

   - Error-diffusion dithering algorithm
   - Reduces color banding while maintaining perceived color depth
   - Implemented with NumPy for efficient pixel operations

2. **Pixelation**:

   - Resizes image to lower resolution and scales back up
   - Uses nearest-neighbor interpolation to maintain blocky appearance

3. **Median Palette Reduction**:

   - Uses MiniBatchKMeans clustering to identify dominant colors
   - Quantizes image to the clustered color palette
   - More efficient than standard k-means for large images

4. **Block-based Color Correction**:
   - Processes images in configurable blocks
   - Applies various statistical color strategies
   - Supports multiple mean calculations and majority voting

### Dependencies

- **Python 3.7+**
- **Pillow (PIL Fork)** - Image processing
- **NumPy** - Numerical operations
- **scikit-learn** - K-means clustering
- **Tkinter** - GUI (usually included with Python)
- **OpenAI SDK** (optional) - For AI image generation

## 🗺️ Migration from Legacy Code

The legacy `functions/` directory is **DEPRECATED**. See [MIGRATION.md](MIGRATION.md) for a complete migration guide.

**Quick Reference:**

| Old                                           | New                                                        |
| --------------------------------------------- | ---------------------------------------------------------- |
| `functions.image_processor.floyd_steinberg()` | `modules.image_correction.apply_dithering()`               |
| `functions.image_processor.pixelate_image()`  | `modules.image_correction.apply_pixelation()`              |
| `functions.image_processor.fix_image()`       | `modules.image_correction.ImageCorrector.correct_colors()` |
| `functions.strategies.Strategies`             | `modules.image_correction.Strategies`                      |
| `functions.utils.*`                           | `modules.common.*`                                         |

## 🔮 Future Roadmap

- [x] Modular architecture implementation
- [x] Image correction module complete
- [ ] Complete ChatGPT API integration for image generation
- [ ] Add batch processing capabilities
- [ ] Implement more image effects (blur, sharpen, etc.)
- [ ] Add CLI interface
- [ ] Create REST API server
- [ ] Add unit and integration tests
- [ ] Performance optimizations with GPU support
- [ ] Docker containerization

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**notNilton**

- GitHub: [@notNilton](https://github.com/notNilton)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

**Note:** Make sure to read [MIGRATION.md](MIGRATION.md) if you're upgrading from an older version that used the `functions/` directory.
