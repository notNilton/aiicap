"""
Repository pattern for database operations
"""

from typing import List, Optional, Dict, Any
from PIL import Image
import io
import json
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import GeneratedImage, CorrectedImage


class ImageRepository:
    """Repository for image database operations"""
    
    @staticmethod
    def save_generated_image(
        session: Session,
        image: Image.Image,
        prompt: str,
        model: str = 'dall-e-3',
        size: str = '1024x1024',
        quality: str = 'standard',
        generation_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GeneratedImage:
        """
        Save a generated image to the database.
        
        Args:
            session: SQLAlchemy session
            image: PIL Image object
            prompt: Generation prompt
            model: AI model used
            size: Image size
            quality: Image quality
            generation_time: Time taken to generate
            metadata: Additional metadata
        
        Returns:
            GeneratedImage object
        """
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        image_format = image.format or 'PNG'
        image.save(img_byte_arr, format=image_format)
        image_data = img_byte_arr.getvalue()
        
        # Create database record
        db_image = GeneratedImage(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            image_data=image_data,
            image_format=image_format,
            file_size=len(image_data),
            width=image.width,
            height=image.height,
            generation_time=generation_time,
            extra_metadata=json.dumps(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )
        
        session.add(db_image)
        session.flush()  # Get the ID without committing
        
        return db_image
    
    @staticmethod
    def save_corrected_image(
        session: Session,
        image: Image.Image,
        source_image_id: int,
        correction_type: str,
        parameters: Dict[str, Any],
        original_prompt: Optional[str] = None,
        processing_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CorrectedImage:
        """
        Save a corrected image to the database.
        
        Args:
            session: SQLAlchemy session
            image: PIL Image object
            source_image_id: ID of the source generated image
            correction_type: Type of correction applied
            parameters: Parameters used for correction
            original_prompt: Original generation prompt
            processing_time: Time taken to process
            metadata: Additional metadata
        
        Returns:
            CorrectedImage object
        """
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        image_format = image.format or 'PNG'
        image.save(img_byte_arr, format=image_format)
        image_data = img_byte_arr.getvalue()
        
        # Create database record
        db_image = CorrectedImage(
            source_image_id=source_image_id,
            correction_type=correction_type,
            parameters=json.dumps(parameters),
            original_prompt=original_prompt,
            image_data=image_data,
            image_format=image_format,
            file_size=len(image_data),
            width=image.width,
            height=image.height,
            processing_time=processing_time,
            extra_metadata=json.dumps(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )
        
        session.add(db_image)
        session.flush()
        
        return db_image
    
    @staticmethod
    def get_generated_image(session: Session, image_id: int) -> Optional[GeneratedImage]:
        """Get a generated image by ID"""
        return session.query(GeneratedImage).filter(GeneratedImage.id == image_id).first()
    
    @staticmethod
    def get_corrected_image(session: Session, image_id: int) -> Optional[CorrectedImage]:
        """Get a corrected image by ID"""
        return session.query(CorrectedImage).filter(CorrectedImage.id == image_id).first()
    
    @staticmethod
    def get_all_generated_images(
        session: Session,
        limit: int = 100,
        offset: int = 0
    ) -> List[GeneratedImage]:
        """Get all generated images with pagination"""
        return session.query(GeneratedImage)\
            .order_by(desc(GeneratedImage.created_at))\
            .limit(limit)\
            .offset(offset)\
            .all()
    
    @staticmethod
    def get_corrected_images_by_source(
        session: Session,
        source_image_id: int
    ) -> List[CorrectedImage]:
        """Get all corrected images for a source image"""
        return session.query(CorrectedImage)\
            .filter(CorrectedImage.source_image_id == source_image_id)\
            .order_by(desc(CorrectedImage.created_at))\
            .all()
    
    @staticmethod
    def search_by_prompt(
        session: Session,
        search_term: str,
        limit: int = 50
    ) -> List[GeneratedImage]:
        """Search generated images by prompt"""
        return session.query(GeneratedImage)\
            .filter(GeneratedImage.prompt.ilike(f'%{search_term}%'))\
            .order_by(desc(GeneratedImage.created_at))\
            .limit(limit)\
            .all()
    
    @staticmethod
    def load_image_from_db(db_image: GeneratedImage) -> Image.Image:
        """
        Load a PIL Image from a GeneratedImage database record.
        
        Args:
            db_image: GeneratedImage object
        
        Returns:
            PIL Image object
        """
        return Image.open(io.BytesIO(db_image.image_data))
    
    @staticmethod
    def load_corrected_image_from_db(db_image: CorrectedImage) -> Image.Image:
        """
        Load a PIL Image from a CorrectedImage database record.
        
        Args:
            db_image: CorrectedImage object
        
        Returns:
            PIL Image object
        """
        return Image.open(io.BytesIO(db_image.image_data))
    
    @staticmethod
    def delete_generated_image(session: Session, image_id: int) -> bool:
        """
        Delete a generated image and all its corrections.
        
        Args:
            session: SQLAlchemy session
            image_id: ID of the image to delete
        
        Returns:
            True if deleted, False if not found
        """
        image = session.query(GeneratedImage).filter(GeneratedImage.id == image_id).first()
        if image:
            session.delete(image)
            return True
        return False
    
    @staticmethod
    def get_statistics(session: Session) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_generated = session.query(GeneratedImage).count()
        total_corrected = session.query(CorrectedImage).count()
        
        return {
            'total_generated_images': total_generated,
            'total_corrected_images': total_corrected,
            'total_images': total_generated + total_corrected
        }
