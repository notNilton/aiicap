"""
Database session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from .config import DATABASE_URL, ECHO_SQL
from .models import Base

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=ECHO_SQL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """
    Initialize the database by creating all tables.
    
    This should be called once when setting up the application.
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def drop_all_tables():
    """
    Drop all tables. Use with caution!
    
    This is useful for development/testing but should not be used in production.
    """
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped")


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get a database session with automatic cleanup.
    
    Usage:
        with get_session() as session:
            image = GeneratedImage(...)
            session.add(image)
            session.commit()
    
    Yields:
        SQLAlchemy Session object
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI/frameworks that need a database session.
    
    Usage:
        @app.get("/images")
        def get_images(db: Session = Depends(get_db)):
            return db.query(GeneratedImage).all()
    
    Yields:
        SQLAlchemy Session object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
