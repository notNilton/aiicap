#!/bin/bash
# Script para reiniciar os serviços

echo "=========================================="
echo " Reiniciando Serviços AIICAP"
echo "=========================================="
echo ""

# Parar serviços
echo "[1/2] Parando serviços..."
./scripts/stop.sh
echo ""

# Aguardar um pouco
sleep 2

# Iniciar serviços
echo "[2/2] Iniciando serviços..."
./scripts/start.sh

echo ""
echo "✓ Reinicialização concluída!"
