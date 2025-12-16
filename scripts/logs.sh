#!/bin/bash
# Script para ver os logs dos serviços em tempo real

echo "=========================================="
echo " Logs dos Serviços AIICAP"
echo "=========================================="
echo ""
echo "Pressione Ctrl+C para sair"
echo ""

# Verificar se os serviços estão rodando
RUNNING=0

if [ -f "logs/generator.pid" ]; then
    GENERATOR_PID=$(cat logs/generator.pid)
    if ps -p $GENERATOR_PID > /dev/null 2>&1; then
        echo "✓ Gerador rodando (PID: $GENERATOR_PID)"
        RUNNING=$((RUNNING + 1))
    fi
fi

if [ -f "logs/corrector.pid" ]; then
    CORRECTOR_PID=$(cat logs/corrector.pid)
    if ps -p $CORRECTOR_PID > /dev/null 2>&1; then
        echo "✓ Corretor rodando (PID: $CORRECTOR_PID)"
        RUNNING=$((RUNNING + 1))
    fi
fi

if [ $RUNNING -eq 0 ]; then
    echo "⚠ Nenhum serviço rodando"
    echo ""
    echo "Logs estáticos:"
    if [ -f "logs/generator.log" ]; then
        echo ""
        echo "=== Gerador (últimas 20 linhas) ==="
        tail -20 logs/generator.log
    fi
    
    if [ -f "logs/corrector.log" ]; then
        echo ""
        echo "=== Corretor (últimas 20 linhas) ==="
        tail -20 logs/corrector.log
    fi
else
    echo ""
    echo "Acompanhando logs em tempo real..."
    echo ""
    tail -f logs/generator.log logs/corrector.log
fi
