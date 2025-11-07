#!/bin/bash
# Script para backup manual do PostgreSQL
# Uso: ./backup_postgres_manual.sh

set -e

BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/flow_forecaster_backup_$TIMESTAMP.sql"

echo "=== Backup PostgreSQL Flow Forecaster ==="
echo "Data: $(date)"
echo ""

# Criar diretório de backup se não existir
mkdir -p "$BACKUP_DIR"

# Iniciar proxy (porta 15432)
echo "[1/3] Iniciando proxy para PostgreSQL..."
flyctl proxy 15432:5432 --app flow-forecaster-db &
PROXY_PID=$!
sleep 3

# Fazer backup via pg_dump
echo "[2/3] Executando pg_dump..."
PGPASSWORD="4ZRplUZglrnfO3Y" pg_dump \
    -h localhost \
    -p 15432 \
    -U flow_forecaster \
    -d flow_forecaster \
    --format=plain \
    --no-owner \
    --no-privileges \
    > "$BACKUP_FILE"

# Comprimir backup
echo "[3/3] Comprimindo backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

# Parar proxy
kill $PROXY_PID 2>/dev/null || true

# Resumo
SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo ""
echo "✅ Backup concluído!"
echo "   Arquivo: $BACKUP_FILE"
echo "   Tamanho: $SIZE"
echo ""
echo "Backups existentes:"
ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "  (nenhum backup encontrado)"
