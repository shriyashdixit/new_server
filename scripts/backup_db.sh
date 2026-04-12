#!/bin/bash
# backup_db.sh — PostgreSQL database backup for Nazukware
#
# Usage:
#   BACKUP_DIR=/mnt/backup_drive/db_backups ./scripts/backup_db.sh
#
# Cron example (runs nightly at 2:00 AM):
#   0 2 * * * BACKUP_DIR=/mnt/backup_drive/db_backups /home/puneserver/new_server/scripts/backup_db.sh >> /var/log/nazukware_backup.log 2>&1
#
# The script reads credentials from .env.prod.db in the same directory as docker-compose.prod.yml.
# It runs pg_dump inside the running pg_db container and saves a gzip-compressed file to BACKUP_DIR.
# Backups older than 30 days are automatically removed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env.prod.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# ── Resolve backup destination ──────────────────────────────────────────────────
BACKUP_DIR="${BACKUP_DIR:-}"
if [ -z "$BACKUP_DIR" ]; then
    echo "[backup_db] ERROR: BACKUP_DIR is not set. Set it as an environment variable or in cron." >&2
    exit 1
fi

mkdir -p "$BACKUP_DIR"

# ── Read DB credentials from .env.prod.db ───────────────────────────────────────
if [ ! -f "$ENV_FILE" ]; then
    echo "[backup_db] ERROR: $ENV_FILE not found." >&2
    exit 1
fi

POSTGRES_USER=$(grep -E '^POSTGRES_USER=' "$ENV_FILE" | cut -d= -f2- | tr -d '"' | tr -d "'")
POSTGRES_DB=$(grep -E '^POSTGRES_DB=' "$ENV_FILE" | cut -d= -f2- | tr -d '"' | tr -d "'")

if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
    echo "[backup_db] ERROR: Could not read POSTGRES_USER or POSTGRES_DB from $ENV_FILE." >&2
    exit 1
fi

# ── Locate the running pg_db container ──────────────────────────────────────────
PG_CONTAINER=$(docker ps --filter "name=pg_db" --format "{{.Names}}" | head -n1)
if [ -z "$PG_CONTAINER" ]; then
    echo "[backup_db] ERROR: No running container matching 'pg_db' found." >&2
    exit 1
fi

# ── Run backup ───────────────────────────────────────────────────────────────────
BACKUP_FILE="$BACKUP_DIR/backup_${POSTGRES_DB}_${TIMESTAMP}.sql.gz"
echo "[backup_db] Starting backup: $BACKUP_FILE"

docker exec "$PG_CONTAINER" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

echo "[backup_db] Backup complete: $(du -sh "$BACKUP_FILE" | cut -f1)"

# ── Prune old backups (keep last 30 days) ───────────────────────────────────────
find "$BACKUP_DIR" -name "backup_${POSTGRES_DB}_*.sql.gz" -mtime +30 -delete
echo "[backup_db] Pruned backups older than 30 days."
