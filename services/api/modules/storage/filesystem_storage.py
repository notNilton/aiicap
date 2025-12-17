"""
File System Storage Implementation

Usa pastas 'untreated' e 'treated' para armazenar imagens.
"""

import os
import json
from typing import Optional, List, Dict, Any
from PIL import Image
from datetime import datetime
import glob


class FileSystemStorage:
    """Implementação usando sistema de arquivos"""
    
    def __init__(self):
        """Inicializar storage de sistema de arquivos"""
        self.untreated_dir = "./data/untreated"
        self.treated_dir = "./data/treated"
        self.metadata_dir = "./data/metadata"
        
        # Criar diretórios se não existirem
        os.makedirs(self.untreated_dir, exist_ok=True)
        os.makedirs(self.treated_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        self._next_id = self._get_next_id()
    
    def _get_next_id(self) -> int:
        """Obter próximo ID disponível"""
        # Procurar todos os arquivos de metadata
        metadata_files = glob.glob(os.path.join(self.metadata_dir, "generated_*.json"))
        if not metadata_files:
            return 1
        
        ids = []
        for f in metadata_files:
            try:
                basename = os.path.basename(f)
                id_str = basename.replace("generated_", "").replace(".json", "")
                ids.append(int(id_str))
            except:
                continue
        
        return max(ids) + 1 if ids else 1
    
    def save_generated_image(
        self,
        image: Image.Image,
        prompt: str,
        **metadata
    ) -> int:
        """Salvar imagem gerada em untreated/"""
        image_id = self._next_id
        self._next_id += 1
        
        # Salvar imagem
        image_path = os.path.join(self.untreated_dir, f"image_{image_id}.png")
        image.save(image_path)
        
        # Salvar metadata
        metadata_path = os.path.join(self.metadata_dir, f"generated_{image_id}.json")
        metadata_content = {
            'id': image_id,
            'prompt': prompt,
            'model': metadata.get('model', 'unknown'),
            'size': metadata.get('size', f"{image.width}x{image.height}"),
            'quality': metadata.get('quality', 'standard'),
            'created_at': datetime.now().isoformat(),
            'generation_time': metadata.get('generation_time', 0.0),
            'image_path': image_path,
            'corrections': []  # Lista de correções aplicadas
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata_content, f, indent=2)
        
        print(f"[FILESYSTEM] Imagem salva: {image_path}")
        return image_id
    
    def save_corrected_image(
        self,
        image: Image.Image,
        source_id: int,
        correction_type: str,
        parameters: Dict[str, Any]
    ) -> int:
        """Salvar imagem corrigida em treated/"""
        # Gerar ID único para correção
        correction_id = f"{source_id}_{correction_type}"
        
        # Salvar imagem
        image_path = os.path.join(self.treated_dir, f"corrected_{correction_id}.png")
        image.save(image_path)
        
        # Atualizar metadata da imagem original
        metadata_path = os.path.join(self.metadata_dir, f"generated_{source_id}.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Adicionar correção à lista
            metadata['corrections'].append({
                'type': correction_type,
                'parameters': parameters,
                'image_path': image_path,
                'created_at': datetime.now().isoformat()
            })
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        print(f"[FILESYSTEM] Correção salva: {image_path}")
        return source_id  # Retornar source_id como identificador
    
    def get_uncorrected_images(self, limit: int = 5) -> List[tuple]:
        """Obter imagens que ainda não foram totalmente corrigidas"""
        uncorrected = []
        
        # Procurar todos os arquivos de metadata
        metadata_files = glob.glob(os.path.join(self.metadata_dir, "generated_*.json"))
        
        for metadata_path in metadata_files[:limit]:
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Verificar se tem todas as 4 correções
                corrections = metadata.get('corrections', [])
                correction_types = {c['type'] for c in corrections}
                
                expected_types = {'pixelation', 'dithering', 'palette_reduction', 'color_correction'}
                
                if not expected_types.issubset(correction_types):
                    uncorrected.append((metadata['id'], metadata['prompt']))
                
                if len(uncorrected) >= limit:
                    break
                    
            except Exception as e:
                print(f"[ERROR] Erro ao ler metadata: {e}")
                continue
        
        return uncorrected
    
    def load_image(self, image_id: int, is_generated: bool = True) -> Optional[Image.Image]:
        """Carregar imagem do sistema de arquivos"""
        if is_generated:
            image_path = os.path.join(self.untreated_dir, f"image_{image_id}.png")
        else:
            # Para imagens corrigidas, precisaria do tipo de correção
            # Por simplicidade, vamos carregar a original
            image_path = os.path.join(self.untreated_dir, f"image_{image_id}.png")
        
        if os.path.exists(image_path):
            return Image.open(image_path)
        
        return None
    
    def get_statistics(self) -> Dict[str, int]:
        """Obter estatísticas do sistema de arquivos"""
        generated_files = glob.glob(os.path.join(self.untreated_dir, "image_*.png"))
        treated_files = glob.glob(os.path.join(self.treated_dir, "corrected_*.png"))
        
        return {
            'total_generated_images': len(generated_files),
            'total_corrected_images': len(treated_files),
            'total_images': len(generated_files) + len(treated_files)
        }
