#!/bin/bash
# Script para limpar dados (imagens e logs)

echo "=========================================="
echo " Limpeza de Dados AIICAP"
echo "=========================================="
echo ""
echo "⚠️  ATENÇÃO: Esta operação irá deletar:"
echo "  - Todas as imagens geradas e corrigidas"
echo "  - Todos os metadados"
echo "  - Todos os logs"
if [ "$1" = "--db" ]; then
    echo "  - Todos os registros do banco de dados"
fi
echo ""
read -p "Tem certeza? (digite 'sim' para confirmar): " CONFIRM

if [ "$CONFIRM" != "sim" ]; then
    echo "Operação cancelada"
    exit 0
fi

echo ""
echo "Limpando..."

# Parar serviços primeiro
echo "[1/4] Parando serviços..."
./scripts/stop.sh > /dev/null 2>&1
echo "  ✓ Serviços parados"

# Limpar File System
echo "[2/4] Limpando File System..."
rm -rf data/untreated/*.png 2>/dev/null
rm -rf data/treated/*.png 2>/dev/null
rm -rf data/metadata/*.json 2>/dev/null
echo "  ✓ Arquivos removidos"

# Limpar logs
echo "[3/4] Limpando logs..."
rm -rf logs/*.log 2>/dev/null
rm -rf logs/*.pid 2>/dev/null
echo "  ✓ Logs removidos"

# Limpar banco de dados (opcional)
if [ "$1" = "--db" ]; then
    echo "[4/4] Limpando banco de dados..."
    source .venv/bin/activate
    python3 -c "
from modules.database.session import drop_all_tables, init_db
drop_all_tables()
init_db()
print('  ✓ Banco de dados resetado')
"
else
    echo "[4/4] Banco de dados não foi alterado (use --db para limpar)"
fi

echo ""
echo "✓ Limpeza concluída!"
echo ""
