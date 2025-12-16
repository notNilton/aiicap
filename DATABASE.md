# PostgreSQL Database Guide

This document explains the PostgreSQL database setup and usage for AIICAP.

## 🗄️ Database Schema

The application uses two main tables:

### `generated_images`

Stores AI-generated images from ChatGPT/DALL-E.

| Column              | Type         | Description                          |
| ------------------- | ------------ | ------------------------------------ |
| `id`                | Integer (PK) | Unique identifier                    |
| `prompt`            | Text         | Generation prompt                    |
| `model`             | String       | AI model used (e.g., "dall-e-3")     |
| `size`              | String       | Image size (e.g., "1024x1024")       |
| `quality`           | String       | Quality setting ("standard" or "hd") |
| `image_data`        | LargeBinary  | Image stored as binary PNG/JPEG      |
| `image_format`      | String       | Format (PNG, JPEG, etc.)             |
| `original_filename` | String       | Original filename if any             |
| `file_size`         | Integer      | Size in bytes                        |
| `width`             | Integer      | Image width                          |
| `height`            | Integer      | Image height                         |
| `created_at`        | DateTime     | Generation timestamp                 |
| `generation_time`   | Float        | Time taken to generate (seconds)     |
| `metadata`          | Text         | Additional metadata as JSON          |

### `corrected_images`

Stores processed/corrected images.

| Column            | Type         | Description                        |
| ----------------- | ------------ | ---------------------------------- |
| `id`              | Integer (PK) | Unique identifier                  |
| `source_image_id` | Integer (FK) | References `generated_images.id`   |
| `correction_type` | String       | Type (pixelation, dithering, etc.) |
| `parameters`      | Text         | Correction parameters as JSON      |
| `original_prompt` | Text         | Original generation prompt         |
| `image_data`      | LargeBinary  | Corrected image as binary          |
| `image_format`    | String       | Format (PNG, JPEG, etc.)           |
| `filename`        | String       | Filename if any                    |
| `file_size`       | Integer      | Size in bytes                      |
| `width`           | Integer      | Image width                        |
| `height`          | Integer      | Image height                       |
| `created_at`      | DateTime     | Processing timestamp               |
| `processing_time` | Float        | Time taken to process (seconds)    |
| `metadata`        | Text         | Additional metadata as JSON        |

**Relationship**: One `generated_image` can have many `corrected_images` (one-to-many).

## 🚀 Setup

### 1. Install PostgreSQL

#### Ubuntu/Debian:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS:

```bash
brew install postgresql
brew services start postgresql
```

#### Windows:

Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL:
CREATE DATABASE aiicap;
CREATE USER aiicap_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aiicap TO aiicap_user;
\q
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
# PostgreSQL Configuration
DATABASE_URL=postgresql://aiicap_user:your_password@localhost:5432/aiicap

# Or use individual components
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aiicap
DB_USER=aiicap_user
DB_PASSWORD=your_password

# OpenAI API (for image generation)
OPENAI_API_KEY=your-openai-api-key

# Debug (optional)
DEBUG=false
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize Database Tables

```bash
python3 setup_database.py
```

You should see:

```
============================================================
 AIICAP Database Setup
============================================================

Database URL: postgresql://aiicap_user:***@localhost:5432/aiicap

Creating tables...
✓ Database tables created successfully!

Created tables:
  - generated_images
  - corrected_images

============================================================
```

## 💻 Usage

### Load Environment Variables

```python
from dotenv import load_dotenv
load_dotenv()
```

### Generate and Save Image

```python
from modules.image_generation import ImageGenerator
from modules.database import init_db

# Initialize database (only needed once)
init_db()

# Generate image (automatically saved to database)
generator = ImageGenerator(api_key="your-key")
image = generator.generate("A serene medieval landscape")

# Get database ID
db_id = generator.get_last_db_id()
print(f"Image saved with ID: {db_id}")
```

### Correct and Save Image

```python
from modules.image_correction import ImageCorrector

# Load image from database and correct
corrector = ImageCorrector(source_db_id=db_id)
corrector.load_from_database(db_id, is_generated=True)

# Apply corrections (automatically saved)
corrector.pixelate(pixel_size=128)
corrector.dither(levels=10)

# Get all corrections for this image
corrections = corrector.get_all_corrections()
for corr in corrections:
    print(f"Correction ID: {corr['id']}, Type: {corr['correction_type']}")
```

### Query Database

```python
from modules.database import get_session
from modules.database.repository import ImageRepository

# Get all generated images
generator = ImageGenerator()
images = generator.get_all_generated_images(limit=50)
for img in images:
    print(f"ID: {img['id']}, Prompt: {img['prompt'][:50]}...")

# Search by prompt
results = generator.search_by_prompt("medieval")
for result in results:
    print(f"Found: {result['prompt']}")

# Load image by ID
image = generator.load_from_database(db_id)
```

### Direct Repository Access

```python
from modules.database import get_session
from modules.database.repository import ImageRepository
from modules.database.models import GeneratedImage

# Custom query
with get_session() as session:
    # Get recent images
    recent = session.query(GeneratedImage)\
        .order_by(GeneratedImage.created_at.desc())\
        .limit(10)\
        .all()

    # Get statistics
    stats = ImageRepository.get_statistics(session)
    print(stats)
```

## 🔧 Maintenance

### Backup Database

```bash
pg_dump -U your_username aiicap > aiicap_backup.sql
```

### Restore Database

```bash
psql -U your_username aiicap < aiicap_backup.sql
```

### Reset Database (⚠️ Caution!)

```python
from modules.database.session import drop_all_tables, init_db

# Drop all tables
drop_all_tables()

# Recreate tables
init_db()
```

## 📊 Querying Examples

### Get images by date range

```python
from datetime import datetime, timedelta
from modules.database import get_session
from modules.database.models import GeneratedImage

with get_session() as session:
    # Images from last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent = session.query(GeneratedImage)\
        .filter(GeneratedImage.created_at >= week_ago)\
        .all()
```

### Get images by model

```python
with get_session() as session:
    dalle3_images = session.query(GeneratedImage)\
        .filter(GeneratedImage.model == 'dall-e-3')\
        .all()
```

### Get correction statistics

```python
from modules.database.models import CorrectedImage
from sqlalchemy import func

with get_session() as session:
    # Count corrections by type
    stats = session.query(
        CorrectedImage.correction_type,
        func.count(CorrectedImage.id)
    ).group_by(CorrectedImage.correction_type).all()

    for corr_type, count in stats:
        print(f"{corr_type}: {count}")
```

## 🐛 Troubleshooting

### Connection Error

If you get connection errors:

1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify credentials in `.env`
3. Check if database exists: `psql -l`

### Permission Denied

```bash
# Grant permissions
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE aiicap TO aiicap_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aiicap_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aiicap_user;
```

### Tables Not Created

Run setup again:

```bash
python3 setup_database.py
```

## 📚 Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
