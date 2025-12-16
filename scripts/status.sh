#!/bin/bash
# Script para verificar o status dos serviços

echo "=========================================="
echo " Status dos Serviços AIICAP"
echo "=========================================="
echo ""

# Verificar modo de storage
USE_DB=$(grep "^USE_DATABASE=" .env 2>/dev/null | cut -d'=' -f2)
STORAGE_MODE=$([ "$USE_DB" = "true" ] && echo "PostgreSQL" || echo "File System")

echo "📦 Modo de Storage: $STORAGE_MODE"
echo ""

# Status do gerador
echo "🎨 Gerador:"
if [ -f "logs/generator.pid" ]; then
    GENERATOR_PID=$(cat logs/generator.pid)
    if ps -p $GENERATOR_PID > /dev/null 2>&1; then
        echo "  Status: ✓ Rodando (PID: $GENERATOR_PID)"
        # Última linha do log
        if [ -f "logs/generator.log" ]; then
            LAST_LINE=$(tail -1 logs/generator.log | grep -oP '\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]' || echo "")
            if [ -n "$LAST_LINE" ]; then
                echo "  Última atividade: $LAST_LINE"
            fi
        fi
    else
        echo "  Status: ✗ Parado (PID inválido)"
    fi
else
    echo "  Status: ✗ Não iniciado"
fi

echo ""

# Status do corretor
echo "🔧 Corretor:"
if [ -f "logs/corrector.pid" ]; then
    CORRECTOR_PID=$(cat logs/corrector.pid)
    if ps -p $CORRECTOR_PID > /dev/null 2>&1; then
        echo "  Status: ✓ Rodando (PID: $CORRECTOR_PID)"
        # Última linha do log
        if [ -f "logs/corrector.log" ]; then
            LAST_LINE=$(tail -1 logs/corrector.log | grep -oP '\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]' || echo "")
            if [ -n "$LAST_LINE" ]; then
                echo "  Última atividade: $LAST_LINE"
            fi
        fi
    else
        echo "  Status: ✗ Parado (PID inválido)"
    fi
else
    echo "  Status: ✗ Não iniciado"
fi

echo ""

# Estatísticas
echo "📊 Estatísticas:"

if [ "$USE_DB" = "true" ]; then
    # PostgreSQL
    source .venv/bin/activate 2>/dev/null
    python3 -c "
from modules.storage import get_storage
try:
    storage = get_storage()
    stats = storage.get_statistics()
    print(f\"  Imagens geradas: {stats['total_generated_images']}\")
    print(f\"  Imagens corrigidas: {stats['total_corrected_images']}\")
    print(f\"  Total: {stats['total_images']}\")
except Exception as e:
    print(f'  Erro ao obter estatísticas: {e}')
" 2>/dev/null || echo "  Não disponível"
else
    # File System
    UNTREATED=$(ls data/untreated/*.png 2>/dev/null | wc -l)
    TREATED=$(ls data/treated/*.png 2>/dev/null | wc -l)
    TOTAL=$((UNTREATED + TREATED))
    echo "  Imagens geradas: $UNTREATED"
    echo "  Imagens corrigidas: $TREATED"
    echo "  Total: $TOTAL"
fi

echo ""
