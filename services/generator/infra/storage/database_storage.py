"""
PostgreSQL Database Storage Implementation
"""

from typing import Optional, List, Dict, Any
from PIL import Image
from datetime import datetime

from . import ImageStorage
from ..database import get_session, init_db
from ..database.repository import ImageRepository
from ..database.models import GeneratedImage, CorrectedImage
from sqlalchemy import and_, not_, exists


class DatabaseStorage(ImageStorage):
    """Implementação usando PostgreSQL"""
    
    def __init__(self):
        """Inicializar storage de banco de dados"""
        init_db()
        self._next_correction_id = 1
    
    def save_generated_image(
        self,
        image: Image.Image,
        prompt: str,
        **metadata
    ) -> int:
        """Salvar imagem gerada no banco de dados"""
        with get_session() as session:
            db_image = ImageRepository.save_generated_image(
                session=session,
                image=image,
                prompt=prompt,
                model=metadata.get('model', 'unknown'),
                size=metadata.get('size', f"{image.width}x{image.height}"),
                quality=metadata.get('quality', 'standard'),
                generation_time=metadata.get('generation_time', 0.0),
                metadata=metadata.get('extra_metadata')
            )
            return db_image.id
    
    def save_corrected_image(
        self,
        image: Image.Image,
        source_id: int,
        correction_type: str,
        parameters: Dict[str, Any]
    ) -> int:
        """Salvar imagem corrigida no banco de dados"""
        with get_session() as session:
            # Obter prompt original
            source = ImageRepository.get_generated_image(session, source_id)
            original_prompt = source.prompt if source else None
            
            db_image = ImageRepository.save_corrected_image(
                session=session,
                image=image,
                source_image_id=source_id,
                correction_type=correction_type,
                parameters=parameters,
                original_prompt=original_prompt,
                processing_time=parameters.get('processing_time', 0.0)
            )
            return db_image.id
    
    def get_uncorrected_images(self, limit: int = 5) -> List[tuple]:
        """Obter imagens que ainda não foram totalmente corrigidas"""
        with get_session() as session:
            # Buscar imagens que não têm correção de color_correction
            query = session.query(GeneratedImage.id, GeneratedImage.prompt).filter(
                not_(
                    exists().where(
                        and_(
                            CorrectedImage.source_image_id == GeneratedImage.id,
                            CorrectedImage.correction_type == 'color_correction'
                        )
                    )
                )
            ).limit(limit)
            
            return [(img_id, prompt) for img_id, prompt in query.all()]
    
    def load_image(self, image_id: int, is_generated: bool = True) -> Optional[Image.Image]:
        """Carregar imagem do banco de dados"""
        with get_session() as session:
            if is_generated:
                db_image = ImageRepository.get_generated_image(session, image_id)
                if db_image:
                    return ImageRepository.load_image_from_db(db_image)
            else:
                db_image = ImageRepository.get_corrected_image(session, image_id)
                if db_image:
                    return ImageRepository.load_corrected_image_from_db(db_image)
        return None
    
    def get_statistics(self) -> Dict[str, int]:
        """Obter estatísticas do banco"""
        with get_session() as session:
            return ImageRepository.get_statistics(session)
