#!/usr/bin/env python3
"""
Exemplo completo de uso do AIICAP com PostgreSQL

Este script demonstra:
- Geração de imagens com IA (simulado)
- Aplicação de correções
- Salvamento automático no banco
- Consulta de histórico
"""

from modules.image_generation import ImageGenerator
from modules.image_correction import ImageCorrector, Strategies
from modules.database import init_db
from modules.common import save_image, load_image
from PIL import Image
import os


def main():
    """Exemplo de workflow completo"""
    
    print("=" * 60)
    print(" AIICAP - Exemplo Completo")
    print("=" * 60)
    
    # 1. Inicializar banco de dados
    print("\n1. Inicializando banco de dados...")
    init_db()
    print("✓ Banco inicializado")
    
    # 2. Para este exemplo, vamos carregar uma imagem local
    # (substituir por generator.generate() quando API estiver configurada)
    print("\n2. Carregando imagem de exemplo...")
    
    # Criar diretório de exemplo se necessário
    os.makedirs("./examples", exist_ok=True)
    
    # Tentar carregar imagem existente ou criar uma simples
    try:
        image = load_image("./data/untreated/medieval-landscape.png")
        print("✓ Imagem carregada de data/untreated/")
    except:
        # Criar uma imagem simples de exemplo
        print("⚠ Criando imagem de exemplo (imagem real não encontrada)")
        image = Image.new('RGB', (512, 512), color='lightblue')
        save_image(image, "./examples/", "exemplo.png")
        print("✓ Imagem de exemplo criada em examples/exemplo.png")
    
    # 3. Salvar no banco como se fosse gerada
    print("\n3. Salvando imagem no banco de dados...")
    from modules.database import get_session
    from modules.database.repository import ImageRepository
    
    with get_session() as session:
        db_image = ImageRepository.save_generated_image(
            session=session,
            image=image,
            prompt="Exemplo de paisagem medieval (simulado)",
            model="exemplo-manual",
            size=f"{image.width}x{image.height}",
            quality="standard",
            generation_time=0.0,
            metadata={'source': 'exemplo_completo.py'}
        )
        gen_id = db_image.id
        print(f"✓ Imagem salva no banco (ID: {gen_id})")
    
    # 4. Aplicar correções
    print("\n4. Aplicando correções...")
    corrector = ImageCorrector(source_db_id=gen_id, auto_save_db=True)
    corrector.set_image(image, source_db_id=gen_id)
    
    # Pixelação
    print("   - Aplicando pixelação...")
    corrector.pixelate(pixel_size=128)
    print("   ✓ Pixelação salva no banco")
    
    # Dithering
    print("   - Aplicando dithering...")
    corrector.dither(levels=10)
    print("   ✓ Dithering salvo no banco")
    
    # Redução de paleta
    print("   - Reduzindo paleta de cores...")
    corrector.reduce_palette(num_colors=16)
    print("   ✓ Paleta reduzida salva no banco")
    
    # Correção de cor
    print("   - Aplicando correção de cor...")
    corrector.correct_colors(
        block_width=4,
        block_height=4,
        strategy=Strategies.AVERAGE
    )
    print("   ✓ Correção de cor salva no banco")
    
    # 5. Ver histórico
    print("\n5. Consultando histórico de correções...")
    corrections = corrector.get_all_corrections()
    print(f"✓ Total de correções aplicadas: {len(corrections)}")
    for i, corr in enumerate(corrections, 1):
        print(f"   {i}. {corr['correction_type']}")
        print(f"      Parâmetros: {corr['parameters']}")
        if corr['processing_time']:
            print(f"      Tempo: {corr['processing_time']:.3f}s")
    
    # 6. Salvar resultado final
    print("\n6. Salvando resultado final...")
    final_image = corrector.get_current_image()
    save_image(final_image, "./examples/", "resultado_final.png")
    print("✓ Resultado salvo em examples/resultado_final.png")
    
    # 7. Estatísticas do banco
    print("\n7. Estatísticas do banco de dados...")
    with get_session() as session:
        stats = ImageRepository.get_statistics(session)
        print(f"✓ Total de imagens geradas: {stats['total_generated_images']}")
        print(f"✓ Total de imagens corrigidas: {stats['total_corrected_images']}")
        print(f"✓ Total geral: {stats['total_images']}")
    
    print("\n" + "=" * 60)
    print(" Exemplo concluído com sucesso! ✓")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Visualize a imagem: examples/resultado_final.png")
    print("2. Configure OPENAI_API_KEY para gerar imagens reais")
    print("3. Consulte DATABASE.md para mais operações")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n✗ Erro: {e}")
        import traceback
        traceback.print_exc()
