# Deployment guide (Ubuntu 24.04/25.04)

## 1) Prepare 4+ servers
1. Panel server (private, no public ingress except tunnel/zero-trust).
2. RU entry node (ASN-1).
3. EU clean exit node (ASN-2).
4. Alt dirty/fallback node (ASN-3).

## 2) Base OS hardening
```bash
sudo bash scripts/install.sh
sudo timedatectl set-timezone UTC
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

## 3) Kernel tuning (BBRv2)
```bash
cat <<'CONF' | sudo tee /etc/sysctl.d/99-vpn.conf
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
net.ipv4.tcp_fastopen=3
net.ipv4.tcp_mtu_probing=1
net.ipv4.ip_local_port_range=10240 65535
CONF
sudo sysctl --system
```

## 4) Configure environment
```bash
cp .env.example .env
nano .env
```
Set domains, API keys, Telegram token, payment secrets.

## 5) Deploy panel server
```bash
cd infra/panel
docker compose --env-file ../../.env -f docker-compose-prod.yml up -d
```

## 6) Deploy node servers
On each node:
```bash
cd infra/node
docker compose --env-file ../../.env -f docker-compose-node.yml up -d
```

## 7) Deploy bot/admin stack
```bash
cd /workspace/rem
docker compose up -d --build
alembic upgrade head
```

## 8) Set bridge chain
Create config profiles from `docs/config-profiles-examples.md`, assign squads and service user, then enable server-side routing in RU entry profile.

## 9) Monitoring
Run Prometheus/Grafana stack in `infra/monitoring` and import dashboards.

## 10) Backup and DR
Set cron:
```bash
0 2 * * * /workspace/rem/scripts/backup.sh
```
Sync `backups/` to offsite (S3/rclone/borg).
