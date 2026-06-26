#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="${1:-}"
CONTAINER_NAME="${CONTAINER_NAME:-gabaritoac_2-db-1}"

if [ -z "$BACKUP_FILE" ]; then
    echo "Uso: $0 <caminho/para/backup.sql.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Erro: arquivo '$BACKUP_FILE' não encontrado."
    exit 1
fi

echo "==> Restaurando backup: $BACKUP_FILE"

if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" \
        psql -U "${POSTGRES_USER:-gabaritoac}" -d "${POSTGRES_DB:-gabaritoac}"
else
    docker exec -i "$CONTAINER_NAME" \
        psql -U "${POSTGRES_USER:-gabaritoac}" -d "${POSTGRES_DB:-gabaritoac}" < "$BACKUP_FILE"
fi

echo "==> Restauração concluída."