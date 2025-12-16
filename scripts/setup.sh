#!/bin/bash
# Script para configurar o projeto AIICAP pela primeira vez

set -e  # Parar em caso de erro

echo "=========================================="
echo " Setup do Projeto AIICAP"
echo "=========================================="
echo ""

# 1. Criar ambiente virtual
if [ ! -d ".venv" ]; then
    echo "[1/6] Criando ambiente virtual..."
    python3 -m venv .venv
    echo "✓ Ambiente virtual criado"
else
    echo "[1/6] Ambiente virtual já existe"
fi

# 2. Ativar ambiente
echo "[2/6] Ativando ambiente virtual..."
source .venv/bin/activate
echo "✓ Ambiente ativado"

# 3. Instalar dependências
echo "[3/6] Instalando dependências..."
pip install -q -r requirements.txt
echo "✓ Dependências instaladas"

# 4. Configurar .env
if [ ! -f ".env" ]; then
    echo "[4/6] Criando arquivo .env..."
    cp .env.example .env
    echo "✓ Arquivo .env criado (ajuste as configurações conforme necessário)"
else
    echo "[4/6] Arquivo .env já existe"
fi

# 5. Verificar modo de storage
USE_DB=$(grep "^USE_DATABASE=" .env | cut -d'=' -f2)

if [ "$USE_DB" = "true" ]; then
    echo "[5/6] Modo: PostgreSQL"
    echo "  Inicializando banco de dados..."
    python3 scripts/setup_database.py
    echo "  ✓ Banco de dados configurado"
else
    echo "[5/6] Modo: File System"
    echo "  Criando diretórios..."
    mkdir -p data/{untreated,treated,metadata}
    echo "  ✓ Diretórios criados"
fi

# 6. Verificar instalação
echo "[6/6] Verificando instalação..."
python3 -c "from modules.storage import get_storage; print('✓ Módulos importados com sucesso')"

echo ""
echo "=========================================="
echo " Setup Completo! ✓"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "  1. Ajustar configurações em .env (se necessário)"
echo "  2. Iniciar serviços: ./scripts/start.sh"
echo "  3. Ver logs: ./scripts/logs.sh"
echo ""
