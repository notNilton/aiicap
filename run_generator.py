#!/usr/bin/env python3
"""
Serviço Gerador de Imagens

Este serviço roda continuamente gerando imagens via ChatGPT API
e salvando-as automaticamente no PostgreSQL.

Uso:
    python3 run_generator.py

Configuração:
    - OPENAI_API_KEY no .env
    - Configurações do banco no .env
"""

import os
import time
from datetime import datetime
from modules.image_generation import ImageGenerator
from modules.database import init_db
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


class ImageGenerationService:
    """Serviço de geração contínua de imagens"""
    
    def __init__(self):
        """Inicializar serviço"""
        self.generator = ImageGenerator(auto_save_db=True)
        self.running = False
        
        # Configurações
        self.delay_between_generations = int(os.getenv('GENERATION_DELAY', '60'))  # segundos
        
        print("=" * 60)
        print(" Serviço Gerador de Imagens - AIICAP")
        print("=" * 60)
        print(f"Delay entre gerações: {self.delay_between_generations}s")
        print()
    
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
        generation_count = 0
        
        while self.running:
            try:
                generation_count += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"[{timestamp}] Geração #{generation_count}")
                print("-" * 60)
                
                # Aqui você pode implementar diferentes lógicas:
                # - Ler prompts de uma fila
                # - Ler de um arquivo
                # - Gerar baseado em padrões
                # - Etc.
                
                # Por enquanto, vamos gerar com prompts de exemplo
                prompt = self._get_next_prompt(generation_count)
                
                print(f"[INFO] Prompt: {prompt}")
                
                # Gerar imagem
                try:
                    image = self.generator.generate(
                        prompt=prompt,
                        size="1024x1024",
                        quality="standard"
                    )
                    
                    db_id = self.generator.get_last_db_id()
                    print(f"[OK] Imagem gerada e salva (ID: {db_id})")
                    
                except NotImplementedError:
                    # API ainda não implementada
                    print("[WARN] ChatGPT API não configurada. Use modo simulação:")
                    print("[WARN] Descomente o código em modules/image_generation/generator.py")
                    print("[WARN] Ou rode em modo simulação para testes")
                    
                    # Modo simulação para testes
                    if os.getenv('SIMULATION_MODE', 'false').lower() == 'true':
                        self._simulate_generation(prompt)
                    else:
                        print("[ERROR] Configure OPENAI_API_KEY ou ative SIMULATION_MODE=true")
                        self.running = False
                        break
                
                except Exception as e:
                    print(f"[ERROR] Erro ao gerar imagem: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Aguardar antes da próxima geração
                if self.running:
                    print(f"[INFO] Aguardando {self.delay_between_generations}s até próxima geração...")
                    print()
                    time.sleep(self.delay_between_generations)
                    
            except Exception as e:
                print(f"[ERROR] Erro no loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)  # Aguardar antes de tentar novamente
    
    def _get_next_prompt(self, count: int) -> str:
        """Obter próximo prompt para geração"""
        
        # Você pode implementar diferentes estratégias:
        # 1. Ler de um arquivo de prompts
        # 2. Ler de um banco de dados
        # 3. Gerar prompts aleatórios
        # 4. Ler de uma fila de mensagens
        
        # Exemplo simples: lista rotativa
        prompts = [
            "Uma paisagem medieval serena com montanhas ao fundo",
            "Um castelo guardado por dragões ao pôr do sol",
            "Uma floresta mística com criaturas mágicas",
            "Um mercado medieval movimentado",
            "Uma taverna acolhedora em uma vila antiga",
        ]
        
        return prompts[(count - 1) % len(prompts)]
    
    def _simulate_generation(self, prompt: str):
        """Modo simulação para testes sem API real"""
        from PIL import Image
        from modules.storage import get_storage
        import random
        
        print("[SIMULATION] Gerando imagem simulada...")
        
        # Criar imagem simples com cor aleatória
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink']
        color = random.choice(colors)
        image = Image.new('RGB', (512, 512), color=color)
        
        # Salvar usando storage abstrato
        storage = get_storage()
        db_id = storage.save_generated_image(
            image=image,
            prompt=prompt,
            model="simulation",
            size="512x512",
            quality="standard",
            generation_time=0.1,
            extra_metadata={'mode': 'simulation'}
        )
        print(f"[SIMULATION] Imagem simulada salva (ID: {db_id})")
    
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
    service = ImageGenerationService()
    service.start()


if __name__ == "__main__":
    main()
