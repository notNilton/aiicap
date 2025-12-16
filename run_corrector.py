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
from modules.database import init_db, get_session
from modules.database.models import GeneratedImage, CorrectedImage
from modules.database.repository import ImageRepository
from dotenv import load_dotenv
from sqlalchemy import and_, not_, exists

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
        print("[INFO] Inicializando banco de dados...")
        init_db()
        print("[OK] Banco de dados pronto\n")
        
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
                uncorrected_images = self._find_uncorrected_images()
                
                if not uncorrected_images:
                    print("[INFO] Nenhuma imagem nova para corrigir")
                else:
                    print(f"[INFO] Encontradas {len(uncorrected_images)} imagens para corrigir")
                    
                    # Processar cada imagem
                    for img_id in uncorrected_images:
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
    
    def _find_uncorrected_images(self):
        """Encontrar imagens que ainda não foram corrigidas"""
        with get_session() as session:
            # Buscar imagens geradas que não têm todas as correções
            query = session.query(GeneratedImage.id).filter(
                # Não tem todas as correções do pipeline
                not_(
                    exists().where(
                        and_(
                            CorrectedImage.source_image_id == GeneratedImage.id,
                            CorrectedImage.correction_type == self.correction_pipeline[-1]['name']
                        )
                    )
                )
            ).limit(self.batch_size)
            
            return [img_id for (img_id,) in query.all()]
    
    def _process_image(self, image_id: int):
        """Processar uma imagem aplicando todas as correções"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"  [{timestamp}] Processando imagem ID: {image_id}")
        
        try:
            # Carregar imagem do banco
            corrector = ImageCorrector(source_db_id=image_id, auto_save_db=True)
            corrector.load_from_database(image_id, is_generated=True)
            
            # Verificar quais correções já foram aplicadas
            existing_corrections = set()
            with get_session() as session:
                corrections = session.query(CorrectedImage.correction_type).filter(
                    CorrectedImage.source_image_id == image_id
                ).all()
                existing_corrections = {corr_type for (corr_type,) in corrections}
            
            # Aplicar correções que ainda não foram feitas
            for step in self.correction_pipeline:
                correction_name = step['name']
                
                if correction_name in existing_corrections:
                    print(f"    [SKIP] {correction_name} - já aplicada")
                    continue
                
                print(f"    [PROC] Aplicando {correction_name}...")
                
                try:
                    # Aplicar correção
                    step['function'](corrector)
                    print(f"    [OK] {correction_name} concluída")
                    
                except Exception as e:
                    print(f"    [ERROR] Erro em {correction_name}: {e}")
                    # Continuar com próxima correção mesmo se uma falhar
            
            print(f"  [OK] Imagem {image_id} processada com sucesso")
            
        except Exception as e:
            print(f"  [ERROR] Erro ao processar imagem {image_id}: {e}")
            import traceback
            traceback.print_exc()
    
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
