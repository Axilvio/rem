#!/usr/bin/env bash
set -euo pipefail
STAMP="$(date -u +%F-%H%M%S)"
mkdir -p backups
for DB in bot admin; do
  docker exec "${DB}-db" pg_dump -U "$DB" "$DB" | gzip > "backups/${DB}-${STAMP}.sql.gz"
done
