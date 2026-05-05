"""
Repository pattern for database operations
"""

from typing import List, Optional, Dict, Any
from PIL import Image
import io
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import GeneratedImage, CorrectedImage, ImageJob


def _upload_dir() -> str:
    return os.getenv("UPLOAD_DIR", "./data/uploads")


def _save_image_file(image: Image.Image, folder: str, filename: str) -> tuple[str, str, int, str]:
    image_format = image.format or 'PNG'
    storage_root = _upload_dir()
    relative_path = os.path.join(folder, filename)
    absolute_path = os.path.join(storage_root, relative_path)
    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    image.save(absolute_path, format=image_format)
    return relative_path, f"/uploads/{relative_path}", os.path.getsize(absolute_path), image_format


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
        # Create database record
        db_image = GeneratedImage(
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            width=image.width,
            height=image.height,
            generation_time=generation_time,
            extra_metadata=json.dumps(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )
        
        session.add(db_image)
        session.flush()  # Get the ID without committing

        relative_path, public_url, file_size, image_format = _save_image_file(
            image,
            "generated",
            f"generated_{db_image.id}.png"
        )
        db_image.file_path = relative_path
        db_image.public_url = public_url
        db_image.image_format = image_format
        db_image.file_size = file_size
        
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
        # Create database record
        db_image = CorrectedImage(
            source_image_id=source_image_id,
            correction_type=correction_type,
            parameters=json.dumps(parameters),
            original_prompt=original_prompt,
            width=image.width,
            height=image.height,
            processing_time=processing_time,
            extra_metadata=json.dumps(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )
        
        session.add(db_image)
        session.flush()

        relative_path, public_url, file_size, image_format = _save_image_file(
            image,
            "corrected",
            f"corrected_{db_image.id}.png"
        )
        db_image.file_path = relative_path
        db_image.public_url = public_url
        db_image.image_format = image_format
        db_image.file_size = file_size
        
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
        if db_image.file_path:
            return Image.open(os.path.join(_upload_dir(), db_image.file_path))
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
        if db_image.file_path:
            return Image.open(os.path.join(_upload_dir(), db_image.file_path))
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


class ImageJobRepository:
    """Repository for persistent image generation jobs."""

    @staticmethod
    def create_job(
        session: Session,
        prompt: str,
        size: str = '1024x1024',
        quality: str = 'standard',
        style: Optional[str] = None,
        model: str = 'dall-e-3'
    ) -> ImageJob:
        job = ImageJob(
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            model=model,
            status='pending',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(job)
        session.flush()
        return job

    @staticmethod
    def get_job(session: Session, job_id: int) -> Optional[ImageJob]:
        return session.query(ImageJob).filter(ImageJob.id == job_id).first()

    @staticmethod
    def claim_next_job(session: Session) -> Optional[Dict[str, Any]]:
        job = (
            session.query(ImageJob)
            .filter(ImageJob.status == 'pending')
            .order_by(ImageJob.created_at)
            .with_for_update(skip_locked=True)
            .first()
        )
        if not job:
            return None

        job.status = 'processing'
        job.attempts += 1
        job.started_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        session.flush()

        return {
            'id': job.id,
            'prompt': job.prompt,
            'model': job.model,
            'size': job.size,
            'quality': job.quality,
            'style': job.style,
        }

    @staticmethod
    def complete_job(session: Session, job_id: int, image_id: int) -> Optional[ImageJob]:
        job = ImageJobRepository.get_job(session, job_id)
        if not job:
            return None

        job.status = 'completed'
        job.image_id = image_id
        job.error = None
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
        return job

    @staticmethod
    def fail_job(session: Session, job_id: int, error: str) -> Optional[ImageJob]:
        job = ImageJobRepository.get_job(session, job_id)
        if not job:
            return None

        job.error = error
        job.status = 'failed' if job.attempts >= job.max_attempts else 'pending'
        job.updated_at = datetime.utcnow()
        return job
