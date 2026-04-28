#!/usr/bin/env bash
set -euo pipefail
apt-get update
apt-get install -y docker.io docker-compose-plugin curl jq nftables fail2ban
systemctl enable --now docker
