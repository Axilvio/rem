#!/usr/bin/env bash
set -euo pipefail
docker compose ps
docker compose exec -T bot python -c 'print("bot ok")'
docker compose exec -T admin python -c 'print("admin ok")'
