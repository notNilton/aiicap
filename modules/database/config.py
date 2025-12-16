"""
Database configuration settings
"""

import os
from typing import Optional


class DatabaseConfig:
    """Database configuration from environment variables"""
    
    @staticmethod
    def get_database_url() -> str:
        """
        Get database URL from environment variables.
        
        Environment variables:
        - DATABASE_URL: Full database URL (takes precedence)
        - DB_HOST: Database host (default: localhost)
        - DB_PORT: Database port (default: 5432)
        - DB_NAME: Database name (default: aiicap)
        - DB_USER: Database user (default: postgres)
        - DB_PASSWORD: Database password (default: postgres)
        
        Returns:
            PostgreSQL database URL
        """
        # Check for full DATABASE_URL first
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Handle Heroku-style postgres:// URLs
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        
        # Build URL from individual components
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'aiicap')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    @staticmethod
    def get_echo_sql() -> bool:
        """
        Get whether to echo SQL statements (for debugging).
        
        Returns:
            True if DEBUG environment variable is set to 'true' or '1'
        """
        debug = os.getenv('DEBUG', 'false').lower()
        return debug in ('true', '1', 'yes')


# Configuration instance
config = DatabaseConfig()
DATABASE_URL = config.get_database_url()
ECHO_SQL = config.get_echo_sql()
