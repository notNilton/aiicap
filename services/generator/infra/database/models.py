"""
Database models for storing generated and corrected images
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import json

Base = declarative_base()


class GeneratedImage(Base):
    """
    Model for AI-generated images from ChatGPT/DALL-E.
    
    Stores the original generated image along with all generation metadata.
    """
    __tablename__ = 'generated_images'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Generation metadata
    prompt = Column(Text, nullable=False, index=True)
    model = Column(String(50), nullable=False, default='dall-e-3')
    size = Column(String(20), nullable=False, default='1024x1024')
    quality = Column(String(20), nullable=False, default='standard')
    
    # Image data
    image_data = Column(LargeBinary, nullable=False)  # Stored as binary PNG/JPEG
    image_format = Column(String(10), nullable=False, default='PNG')  # PNG, JPEG, etc.
    
    # File metadata
    original_filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    generation_time = Column(Float, nullable=True)  # Time taken to generate (seconds)
    
    # Additional metadata (stored as JSON)
    extra_metadata = Column(Text, nullable=True)  # JSON string for extra data
    
    # Relationships
    corrected_images = relationship(
        'CorrectedImage',
        back_populates='source_image',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        return f"<GeneratedImage(id={self.id}, prompt='{self.prompt[:50]}...', created_at={self.created_at})>"
    
    def to_dict(self):
        """Convert to dictionary (excluding binary data)"""
        return {
            'id': self.id,
            'prompt': self.prompt,
            'model': self.model,
            'size': self.size,
            'quality': self.quality,
            'image_format': self.image_format,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'generation_time': self.generation_time,
            'extra_metadata': json.loads(self.extra_metadata) if self.extra_metadata else None
        }


class CorrectedImage(Base):
    """
    Model for corrected/processed images.
    
    Stores images that have been processed using correction techniques,
    linked to their source generated image.
    """
    __tablename__ = 'corrected_images'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to source image
    source_image_id = Column(Integer, ForeignKey('generated_images.id'), nullable=False, index=True)
    
    # Correction metadata
    correction_type = Column(String(50), nullable=False)  # pixelation, dithering, palette_reduction, color_correction
    parameters = Column(Text, nullable=False)  # JSON string of parameters used
    
    # If it's a chain of corrections, store the original prompt
    original_prompt = Column(Text, nullable=True)
    
    # Image data
    image_data = Column(LargeBinary, nullable=False)  # Stored as binary PNG/JPEG
    image_format = Column(String(10), nullable=False, default='PNG')
    
    # File metadata
    filename = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    processing_time = Column(Float, nullable=True)  # Time taken to process (seconds)
    
    # Additional metadata
    extra_metadata = Column(Text, nullable=True)  # JSON string for extra data
    
    # Relationships
    source_image = relationship('GeneratedImage', back_populates='corrected_images')
    
    def __repr__(self):
        return f"<CorrectedImage(id={self.id}, type='{self.correction_type}', source_id={self.source_image_id}, created_at={self.created_at})>"
    
    def to_dict(self):
        """Convert to dictionary (excluding binary data)"""
        return {
            'id': self.id,
            'source_image_id': self.source_image_id,
            'correction_type': self.correction_type,
            'parameters': json.loads(self.parameters) if self.parameters else None,
            'original_prompt': self.original_prompt,
            'image_format': self.image_format,
            'filename': self.filename,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processing_time': self.processing_time,
            'extra_metadata': json.loads(self.extra_metadata) if self.extra_metadata else None
        }
