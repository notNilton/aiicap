#!/bin/bash
# Script para parar os serviços AIICAP

echo "=========================================="
echo " Parando Serviços AIICAP"
echo "=========================================="
echo ""

STOPPED=0

# Parar gerador
if [ -f "logs/generator.pid" ]; then
    GENERATOR_PID=$(cat logs/generator.pid)
    if ps -p $GENERATOR_PID > /dev/null 2>&1; then
        echo "[INFO] Parando gerador (PID: $GENERATOR_PID)..."
        kill $GENERATOR_PID
        echo "  ✓ Gerador parado"
        STOPPED=$((STOPPED + 1))
    else
        echo "[INFO] Gerador não está rodando"
    fi
    rm -f logs/generator.pid
else
    echo "[INFO] Gerador não está rodando"
fi

# Parar corretor
if [ -f "logs/corrector.pid" ]; then
    CORRECTOR_PID=$(cat logs/corrector.pid)
    if ps -p $CORRECTOR_PID > /dev/null 2>&1; then
        echo "[INFO] Parando corretor (PID: $CORRECTOR_PID)..."
        kill $CORRECTOR_PID
        echo "  ✓ Corretor parado"
        STOPPED=$((STOPPED + 1))
    else
        echo "[INFO] Corretor não está rodando"
    fi
    rm -f logs/corrector.pid
else
    echo "[INFO] Corretor não está rodando"
fi

echo ""
if [ $STOPPED -eq 0 ]; then
    echo "Nenhum serviço estava rodando"
else
    echo "✓ $STOPPED serviço(s) parado(s)"
fi
echo ""
