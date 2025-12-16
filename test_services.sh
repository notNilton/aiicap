#!/bin/bash
# Script para testar os serviços simultaneamente

echo "=========================================="
echo " Teste dos Serviços AIICAP"
echo "=========================================="
echo ""

# Ativar ambiente virtual
source .venv/bin/activate

# Limpar logs antigos
rm -f test_generator.log test_corrector.log

echo "[INFO] Iniciando serviço gerador..."
python3 run_generator.py > test_generator.log 2>&1 &
GENERATOR_PID=$!
echo "  PID do gerador: $GENERATOR_PID"

sleep 2

echo "[INFO] Iniciando serviço corretor..."
python3 run_corrector.py > test_corrector.log 2>&1 &
CORRECTOR_PID=$!
echo "  PID do corretor: $CORRECTOR_PID"

echo ""
echo "✓ Serviços iniciados!"
echo ""
echo "Para ver os logs:"
echo "  tail -f test_generator.log"
echo "  tail -f test_corrector.log"
echo ""
echo "Para parar os serviços:"
echo "  kill $GENERATOR_PID $CORRECTOR_PID"
echo ""
echo "Os serviços estão rodando em background..."
echo "Aguarde 30 segundos e veja os logs!"
