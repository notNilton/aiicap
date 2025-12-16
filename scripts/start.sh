#!/bin/bash
# Script para iniciar os serviços AIICAP

source .venv/bin/activate

echo "=========================================="
echo " Iniciando Serviços AIICAP"
echo "=========================================="
echo ""

# Verificar modo de storage
USE_DB=$(grep "^USE_DATABASE=" .env | cut -d'=' -f2)
STORAGE_MODE=$([ "$USE_DB" = "true" ] && echo "PostgreSQL" || echo "File System")

echo "Modo de storage: $STORAGE_MODE"
echo ""

# Criar diretório de logs
mkdir -p logs

# Parar serviços antigos se existirem
./scripts/stop.sh 2>/dev/null || true

# Iniciar gerador
echo "[INFO] Iniciando serviço gerador..."
nohup python3 scripts/run_generator.py > logs/generator.log 2>&1 &
GENERATOR_PID=$!
echo $GENERATOR_PID > logs/generator.pid
echo "  ✓ Gerador iniciado (PID: $GENERATOR_PID)"

# Aguardar um pouco
sleep 2

# Iniciar corretor
echo "[INFO] Iniciando serviço corretor..."
nohup python3 scripts/run_corrector.py > logs/corrector.log 2>&1 &
CORRECTOR_PID=$!
echo $CORRECTOR_PID > logs/corrector.pid
echo "  ✓ Corretor iniciado (PID: $CORRECTOR_PID)"

echo ""
echo "=========================================="
echo " Serviços Iniciados! ✓"
echo "=========================================="
echo ""
echo "PIDs salvos em:"
echo "  - logs/generator.pid → $GENERATOR_PID"
echo "  - logs/corrector.pid → $CORRECTOR_PID"
echo ""
echo "Para ver os logs:"
echo "  ./scripts/logs.sh"
echo ""
echo "Para parar os serviços:"
echo "  ./scripts/stop.sh"
echo ""
