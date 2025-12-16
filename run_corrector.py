#!/usr/bin/env python3
"""
Serviço Corretor de Imagens

Este serviço monitora o banco de dados em busca de imagens geradas
que ainda não foram corrigidas, e aplica automaticamente as correções.

Uso:
    python3 run_corrector.py

Configuração:
    - Configurações do banco no .env
    - CORRECTION_TYPES: tipos de correção a aplicar
"""

import os
import time
from datetime import datetime
from modules.image_correction import ImageCorrector, Strategies, apply_pixelation, apply_dithering
from modules.storage import get_storage
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class ImageCorrectionService:
    """Serviço de correção automática de imagens"""
    
    def __init__(self):
        """Inicializar serviço"""
        self.running = False
        
        # Configurações
        self.check_interval = int(os.getenv('CORRECTION_CHECK_INTERVAL', '30'))  # segundos
        self.batch_size = int(os.getenv('CORRECTION_BATCH_SIZE', '5'))
        
        # Tipos de correção a aplicar (configurable)
        self.correction_pipeline = self._load_correction_pipeline()
        
        print("=" * 60)
        print(" Serviço Corretor de Imagens - AIICAP")
        print("=" * 60)
        print(f"Intervalo de verificação: {self.check_interval}s")
        print(f"Tamanho do lote: {self.batch_size}")
        print(f"Pipeline de correções: {len(self.correction_pipeline)} etapas")
        for i, step in enumerate(self.correction_pipeline, 1):
            print(f"  {i}. {step['name']}")
        print()
    
    def _load_correction_pipeline(self):
        """Carregar pipeline de correções"""
        # Você pode configurar isso via env vars ou arquivo
        return [
            {
                'name': 'pixelation',
                'function': lambda corrector: corrector.pixelate(pixel_size=128),
                'parameters': {'pixel_size': 128}
            },
            {
                'name': 'dithering',
                'function': lambda corrector: corrector.dither(levels=10),
                'parameters': {'levels': 10}
            },
            {
                'name': 'palette_reduction',
                'function': lambda corrector: corrector.reduce_palette(num_colors=16),
                'parameters': {'num_colors': 16}
            },
            {
                'name': 'color_correction',
                'function': lambda corrector: corrector.correct_colors(
                    block_width=4,
                    block_height=4,
                    strategy=Strategies.AVERAGE
                ),
                'parameters': {
                    'block_width': 4,
                    'block_height': 4,
                    'strategy': 'AVERAGE'
                }
            }
        ]
    
    def start(self):
        """Iniciar serviço"""
        print("[INFO] Inicializando storage...")
        self.storage = get_storage()
        
        use_db = os.getenv('USE_DATABASE', 'true').lower() == 'true'
        storage_type = "PostgreSQL" if use_db else "File System"
        print(f"[OK] Storage pronto ({storage_type})\n")
        
        self.running = True
        print(f"[INFO] Serviço iniciado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("[INFO] Pressione Ctrl+C para parar\n")
        
        try:
            self.run_loop()
        except KeyboardInterrupt:
            self.stop()
    
    def run_loop(self):
        """Loop principal do serviço"""
        check_count = 0
        
        while self.running:
            try:
                check_count += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"[{timestamp}] Verificação #{check_count}")
                print("-" * 60)
                
                # Buscar imagens que precisam de correção
                uncorrected_images = self.storage.get_uncorrected_images(self.batch_size)
                
                if not uncorrected_images:
                    print("[INFO] Nenhuma imagem nova para corrigir")
                else:
                    print(f"[INFO] Encontradas {len(uncorrected_images)} imagens para corrigir")
                    
                    # Processar cada imagem
                    for img_id, prompt in uncorrected_images:
                        self._process_image(img_id)
                
                # Aguardar antes da próxima verificação
                if self.running:
                    print(f"[INFO] Aguardando {self.check_interval}s até próxima verificação...")
                    print()
                    time.sleep(self.check_interval)
                    
            except Exception as e:
                print(f"[ERROR] Erro no loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)
    
    def _process_image(self, image_id: int):
        """Processar uma imagem aplicando todas as correções"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"  [{timestamp}] Processando imagem ID: {image_id}")
        
        try:
            # Carregar imagem do storage
            image = self.storage.load_image(image_id, is_generated=True)
            if not image:
                print(f"  [ERROR] Imagem {image_id} não encontrada")
                return
            
            # Verificar quais correções já foram aplicadas
            # Para file system, isso está no metadata
            # Para database, consultar banco
            existing_corrections = self._get_existing_corrections(image_id)
            
            # Aplicar correções que ainda não foram feitas
            corrector = ImageCorrector(auto_save_db=False)  # Não salvar automaticamente
            corrector.set_image(image)
            
            for step in self.correction_pipeline:
                correction_name = step['name']
                
                if correction_name in existing_corrections:
                    print(f"    [SKIP] {correction_name} - já aplicada")
                    continue
                
                print(f"    [PROC] Aplicando {correction_name}...")
                
                try:
                    # Aplicar correção
                    step['function'](corrector)
                    corrected_image = corrector.get_current_image()
                    
                    # Salvar no storage
                    self.storage.save_corrected_image(
                        image=corrected_image,
                        source_id=image_id,
                        correction_type=correction_name,
                        parameters=step['parameters']
                    )
                    
                    print(f"    [OK] {correction_name} concluída")
                    
                except Exception as e:
                    print(f"    [ERROR] Erro em {correction_name}: {e}")
            
            print(f"  [OK] Imagem {image_id} processada com sucesso")
            
        except Exception as e:
            print(f"  [ERROR] Erro ao processar imagem {image_id}: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_existing_corrections(self, image_id: int) -> set:
        """Obter correções já aplicadas"""
        use_db = os.getenv('USE_DATABASE', 'true').lower() == 'true'
        
        if use_db:
            # PostgreSQL
            from modules.database import get_session
            from modules.database.models import CorrectedImage
            
            with get_session() as session:
                corrections = session.query(CorrectedImage.correction_type).filter(
                    CorrectedImage.source_image_id == image_id
                ).all()
                return {corr_type for (corr_type,) in corrections}
        else:
            # File System - ler do metadata
            import json
            metadata_path = f"./data/metadata/generated_{image_id}.json"
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    corrections = metadata.get('corrections', [])
                    return {c['type'] for c in corrections}
            
            return set()
    
    def stop(self):
        """Parar serviço"""
        print("\n")
        print("[INFO] Parando serviço...")
        self.running = False
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[INFO] Serviço parado em {timestamp}")
        print("[OK] Até logo!")


def main():
    """Ponto de entrada"""
    service = ImageCorrectionService()
    service.start()


if __name__ == "__main__":
    main()
