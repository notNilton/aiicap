"""
Storage Abstraction Layer

Permite alternar entre PostgreSQL e sistema de arquivos
através da variável USE_DATABASE.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from PIL import Image
from datetime import datetime


class ImageStorage(ABC):
    """Interface abstrata para storage de imagens"""
    
    @abstractmethod
    def save_generated_image(
        self,
        image: Image.Image,
        prompt: str,
        **metadata
    ) -> int:
        """Salvar imagem gerada"""
        pass
    
    @abstractmethod
    def save_corrected_image(
        self,
        image: Image.Image,
        source_id: int,
        correction_type: str,
        parameters: Dict[str, Any]
    ) -> int:
        """Salvar imagem corrigida"""
        pass
    
    @abstractmethod
    def get_uncorrected_images(self, limit: int = 5) -> List[tuple]:
        """Obter imagens que precisam de correção"""
        pass
    
    @abstractmethod
    def load_image(self, image_id: int, is_generated: bool = True) -> Optional[Image.Image]:
        """Carregar imagem por ID"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, int]:
        """Obter estatísticas"""
        pass


def get_storage() -> ImageStorage:
    """
    Factory para obter storage apropriado baseado em USE_DATABASE.
    
    Returns:
        ImageStorage: PostgreSQL ou FileSystem storage
    """
    use_database = os.getenv('USE_DATABASE', 'true').lower() == 'true'
    
    if use_database:
        from .database_storage import DatabaseStorage
        return DatabaseStorage()
    else:
        from .filesystem_storage import FileSystemStorage
        return FileSystemStorage()


__all__ = ['ImageStorage', 'get_storage']
