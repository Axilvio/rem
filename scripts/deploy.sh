#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
docker compose pull
docker compose up -d --build
