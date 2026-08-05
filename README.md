# aiicap

Automated AI tool that corrects artifacts, sharpens edges, and optimizes color palettes in AI-generated pixel art images.

## Architecture

```
database/
  config.py           Database connection parameters
  models.py           SQLAlchemy models for generations and corrections
  repository.py       Database operations and persistence
  session.py          Session management
image_correction/
  color_utils.py      Color quantization and palette extraction
  corrector.py        Core correction engine
  effects.py          Outline and post-processing filters
  metrics.py          Image quality measurement functions
  pipeline.py         Multi-stage execution pipeline
  strategies.py       Edge sharpening and grid alignment algorithms
image_generation/
  generator.py        DALL-E 3 API client integration
app.py                Command line application
gui_corrector.py      Gradio web interface
correct.py            Image restoration CLI utility
generate.py           Image generation CLI utility
Makefile              Task automation
```

### Components

- `image_correction`: Pipeline for downscaling, color quantization (k-means), grid alignment, and edge sharpening.
- `image_generation`: OpenAI API integration for generating base pixel art images via DALL-E 3.
- `database`: SQLite persistence using SQLAlchemy for tracking generation and correction history.
- `gui_corrector.py`: Interactive Gradio web interface for adjusting parameters and previewing results.

### Correction Pipeline

1. **Grid Downscaling**: Resamples high-resolution AI output to target pixel grid (e.g. 64x64) using area resampling.
2. **Color Quantization**: Reduces color space to fixed palette size (e.g. 16 colors) using k-means clustering.
3. **Alpha Binarization**: Cleans semi-transparent anti-aliased edge pixels based on configurable threshold.
4. **Post-Processing**: Applies optional outline, contrast, and saturation adjustments.

## Development

### Prerequisites

- Python 3.10+
- Virtual environment (`venv`)

### Setup Environment

Create virtual environment, install dependencies, and initialize SQLite database:

```bash
make setup
```

### Usage

Launch Gradio web UI:

```bash
make gui
```

Run CLI image correction:

```bash
make correct INPUT=input.png OUTPUT=output.png TARGET_SIZE=64x64 PALETTE_SIZE=16
```

Generate base pixel art image (requires `OPENAI_API_KEY` in `.env`):

```bash
make generate PROMPT="a retro pixel art space ship"
```

### Service Endpoints

| Service | Type | Port / Command | Endpoint / Usage |
|---------|------|----------------|------------------|
| Web UI | Gradio UI | `7860` | http://localhost:7860 |
| Correction CLI | CLI | `make correct` | `INPUT=in.png OUTPUT=out.png` |
| Generation CLI | CLI | `make generate` | `PROMPT="description"` |
| Database | SQLite | File | `data.db` |


## Documentation

- [📋 Roadmap & TODOs](docs/TODO.md) - Planned features and project roadmap
- [📐 Architecture](docs/ARCHITECTURE.md) - System architecture and components
