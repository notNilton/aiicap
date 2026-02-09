"""
AIICAP Shared Package

Contains shared modules for database, storage, and common utilities.
"""

__version__ = "1.0.0"

from .database import init_db, get_session, GeneratedImage, CorrectedImage
from .storage import get_storage, StorageMode
from .common import save_image, display_image
