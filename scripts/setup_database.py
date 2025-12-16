"""
Database Setup Script

Initialize the PostgreSQL database and create all tables.
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.database import init_db, engine
from modules.database.config import DATABASE_URL


def setup_database():
    """Initialize the database"""
    print("=" * 60)
    print(" AIICAP Database Setup")
    print("=" * 60)
    print(f"\nDatabase URL: {DATABASE_URL}")
    print("\nCreating tables...")
    
    try:
        init_db()
        print("\n✓ Database setup completed successfully!")
        print("\nCreated tables:")
        print("  - generated_images")
        print("  - corrected_images")
        print("\n" + "=" * 60)
        return True
    except Exception as e:
        print(f"\n✗ Error setting up database: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. Database credentials are correct (see .env.example)")
        print("  3. Database 'aiicap' exists (or create it)")
        print("\n" + "=" * 60)
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
