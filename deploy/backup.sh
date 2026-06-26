#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
CONTAINER_NAME="${CONTAINER_NAME:-gabaritoac_2-db-1}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

mkdir -p "$BACKUP_DIR"

echo "==> Criando backup do banco PostgreSQL..."

docker exec "$CONTAINER_NAME" \
    pg_dump -U "${POSTGRES_USER:-gabaritoac}" -d "${POSTGRES_DB:-gabaritoac}" \
    --no-owner --no-acl --clean --if-exists \
    > "$BACKUP_DIR/backup_${TIMESTAMP}.sql"

echo "==> Backup salvo em: $BACKUP_DIR/backup_${TIMESTAMP}.sql"

echo "==> Comprimindo..."
gzip "$BACKUP_DIR/backup_${TIMESTAMP}.sql"
echo "==> Comprimido: $BACKUP_DIR/backup_${TIMESTAMP}.sql.gz"

echo "==> Removendo backups com mais de ${RETENTION_DAYS} dias..."
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime "+${RETENTION_DAYS}" -delete

echo "==> Backup finalizado com sucesso."