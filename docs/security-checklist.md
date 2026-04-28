# Security checklist

- Panel is not public; only Cloudflare Tunnel/Zero Trust or mTLS+WireGuard.
- Separate Docker networks: edge/internal; DB and Redis only internal.
- Enforce webhook signature + idempotency keys for payment providers.
- Enable fail2ban + nftables ingress policy per node.
- Rotate shortIds and Reality keys on schedule.
- Disable weak TLS, pin modern ciphers and SNI allowlist.
- Apply least privilege: read-only FS, tmpfs, no-new-privileges where possible.
- Daily encrypted PostgreSQL backups + offsite copy + restore drills.
- Prometheus alerting to Telegram for node down/high packet loss/payment failures.
- Controlled updates via canary batches; no blind Watchtower updates.
