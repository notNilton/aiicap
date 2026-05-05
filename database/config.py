"""
Database configuration settings
"""

import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")
ECHO_SQL = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
