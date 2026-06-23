# SAOS Customer Dashboard — Tailscale Exposed
**Date:** 2026-06-23 10:37 CDT

---

## Configuration

### Tailscale Serve (Tailnet-Only Access)
**Command used:**
```bash
tailscale serve --bg --set-path /dashboard 8768
```

### Endpoints

| URL | Purpose | Access |
|-----|---------|--------|
| `https://phillips-macbook-air.tail573d57.ts.net/dashboard/` | Dashboard UI | Tailnet only |
| `https://phillips-macbook-air.tail573d57.ts.net/dashboard/api/portal/health` | Health check | Tailnet only |
| `https://phillips-macbook-air.tail573d57.ts.net/dashboard/api/portal/status` | Fleet status | Tailnet only |
| `https://phillips-macbook-air.tail573d57.ts.net/dashboard/SAOS-Service-Manual-v2.0.pdf` | Service Manual | Tailnet only |
| `https://phillips-macbook-air.tail573d57.ts.net/dashboard/SAOS-Quick-Start-Guide.pdf` | Quick Start | Tailnet only |

### Tailscale Serve Status
```
Domain: phillips-macbook-air.tail573d57.ts.net:443
  /        -> http://127.0.0.1:18789  (OpenClaw)
  /dashboard -> http://127.0.0.1:8768  (SAOS Customer Dashboard)
```

### Security
- **Tailnet only** — requires Tailscale connection
- **HTTPS** — TLS terminated by Tailscale
- **No auth on dashboard yet** — client_id param only
- **Port 8768** — local-only, not exposed to LAN

### Persistence
- Tailscale serve config survives reboots (stored in tailscaled state)
- LaunchAgent `net.systack.customer-dashboard` ensures local Flask app restarts
- Both services auto-start on boot

### To Remove
```bash
# Remove just the /dashboard path
tailscale serve --https=443 --set-path /dashboard off

# Or reset all serve configs
tailscale serve reset
```

---
*Session saved: 2026-06-23 10:37 CDT*
