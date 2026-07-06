# SAOS Internal Deployment Kit

**ASSEMBLY 🛠 | Build/Deploy Agent**
**Version:** 1.0 | **Date:** 2026-07-06

---

## 1. Environment Setup Procedure

### Prerequisites

| Component | Version | Install Command | Notes |
|-----------|---------|-----------------|-------|
| macOS / Linux | 12+ | — | Development on macOS, production on Linux VPS |
| Python | 3.9+ | `brew install python@3.9` | Using 3.9.6 on current Mac |
| PostgreSQL | 14+ | `brew install postgresql@14` | `systack_memory` database |
| n8n | Latest | `npm install -g n8n` | Runs on port 5678 |
| cloudflared | Latest | `brew install cloudflared` | Cloudflare Tunnel client |
| Tailscale | Latest | `brew install tailscale` | VPN mesh (optional) |
| Git | 2.30+ | `brew install git` | Source control |

### Environment Variables Checklist

Create `~/.zshenv` or `~/.bash_profile` with these exports:

```bash
# === SAOS Core ===
export SYSTACK_ADMIN_PIN="1234"                    # REQUIRED: 4-8 digit PIN for Command Center
export SAOS_INTERNAL_API_KEY="saos-internal-dev-key"  # Change to 64-char hex for production

# === PostgreSQL ===
export PGUSER="philliplowe"
export PGPASSWORD="***"
export PGHOST="localhost"
export PGDATABASE="systack_memory"

# === Stripe (Live) ===
export STRIPE_SECRET_KEY="sk_live_..."            # Restricted key
export STRIPE_PUBLISHABLE_KEY="pk_live_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."

# === n8n ===
export N8N_BASIC_AUTH_ACTIVE="true"
export N8N_BASIC_AUTH_USER="admin"
export N8N_BASIC_AUTH_PASSWORD="..."
export N8N_WEBHOOK_URL="https://n8n.systack.net/"

# === Cloudflare ===
export CLOUDFLARE_TUNNEL_TOKEN="..."              # For tunnel authentication

# === Optional ===
export OPENAI_API_KEY="sk-..."                     # For AI-powered features
export ANTHROPIC_API_KEY="sk-ant-..."               # Claude integration
```

### Database Initialization

```bash
# 1. Start PostgreSQL
brew services start postgresql@14

# 2. Create database (if not exists)
createdb systack_memory 2>/dev/null || echo "DB exists"

# 3. Run schema migration
# The API creates tables automatically on first run, but verify:
psql -d systack_memory -c "\dt" | grep saos_clients
```

### Service Startup Order

| Order | Service | Command | Port | Depends On |
|-------|---------|---------|------|------------|
| 1 | PostgreSQL | `brew services start postgresql@14` | 5432 | — |
| 2 | n8n | `n8n start` | 5678 | PostgreSQL |
| 3 | Customer Portal | `python3 api.py --port 8768` | 8768 | PostgreSQL |
| 4 | Command Center | `python3 api.py --port 8770` | 8770 | PostgreSQL |
| 5 | Invoice Dashboard | `python3 api.py --port 8766` | 8766 | PostgreSQL |
| 6 | Webhook Bridge | `python3 api.py --port 8767` | 8767 | PostgreSQL |
| 7 | Booking Dashboard | `python3 api.py --port 8772` | 8772 | PostgreSQL |
| 8 | BlueBubbles | `brew services start bluebubbles-server` | 1234 | — |
| 9 | Cloudflare Tunnel | `cloudflared tunnel run <id>` | — | Services 3-7 |

### Port Assignments

| Port | Service | Protocol |
|------|---------|----------|
| 8768 | Customer Portal | HTTP (Flask) |
| 8770 | Command Center | HTTP (Flask) |
| 8766 | Invoice Dashboard | HTTP (Flask) |
| 8767 | Webhook Bridge | HTTP (Flask) |
| 8772 | Booking Dashboard | HTTP (Flask) |
| 5678 | n8n | HTTP |
| 1234 | BlueBubbles | HTTP |
| 5432 | PostgreSQL | TCP |

### Conflict Resolution

If a port is already in use:
```bash
# Find what's using a port
lsof -i :8768

# Kill the process
kill $(lsof -t -i :8768)

# Or use a different port
python3 api.py --port 8769  # fallback
```

---

## 2. Delivery Checklist

### Pre-Deployment (Before Client Go-Live)

| # | Task | Owner | Time | PASS Criteria |
|---|------|-------|------|---------------|
| 2.1 | Create `saos_clients` record | SOL | 2 min | Record exists with customer_name, email, tier |
| 2.2 | Generate temp PIN | SOL | 1 min | `scripts/onboard_client.py` output shows PIN |
| 2.3 | Run `onboard_client.py` | SOL | 3 min | Client record updated, chat created, tasks created |
| 2.4 | Set up DNS | SOL | 5 min | CNAME created in Cloudflare dashboard |
| 2.5 | Verify SSL | SOL | 2 min | `curl -s https://portal.<client>.systack.net` returns 200 |
| 2.6 | Configure n8n workflows | SOL | 10 min | Client-specific workflow forked and activated |
| 2.7 | VALI Pre-Launch Checklist | VALI | 15 min | All 10 items PASS (see `Systack/qa/client-launch-checklists.md`) |

### Deployment (Go-Live Day)

| # | Task | Owner | Time | PASS Criteria |
|---|------|-------|------|---------------|
| 2.8 | Final backup | SOL | 3 min | `scripts/backup_verify.py` reports success |
| 2.9 | Switch DNS to production | SOL | 2 min | Global DNS resolves to production IP |
| 2.10 | Start all services | SOL | 2 min | `curl http://localhost:8768/api/portal/health` returns 200 |
| 2.11 | Health checks | SOL | 5 min | All services report healthy in Command Center |
| 2.12 | VALI Launch Checklist | VALI | 10 min | All 7 items PASS |

### Post-Deployment (First 48 Hours)

| # | Task | Owner | Time | PASS Criteria |
|---|------|-------|------|---------------|
| 2.13 | Monitor error logs | PESSI | 10 min | No ERROR entries in logs |
| 2.14 | Verify backup ran | SOL | 2 min | `backup_log` shows success |
| 2.15 | Client feedback call | Green | 30 min | Call completed, notes documented |
| 2.16 | VALI Post-Launch Checklist | VALI | 20 min | All 6 items PASS |

### Sign-Off Requirements

Before declaring deployment complete:
- [ ] Customer Portal loads at client URL
- [ ] Client can log in with PIN
- [ ] All requested services are visible in portal
- [ ] First automated workflow triggered successfully
- [ ] Health checks show 100% for 15 consecutive minutes
- [ ] Backup completed and verified
- [ ] Client confirmed receipt of welcome materials
- [ ] Green approved go-live

---

## 3. Deployment Procedure

### Step-by-Step: Zero to Live in Under 2 Hours

**Phase 1: Prep (15 minutes)**

1. Receive client payment confirmation
2. Create `saos_clients` record:
   ```python
   # Or use onboard_client.py
   python3 scripts/onboard_client.py --name "Client Name" --email "client@example.com" --tier "business"
   ```
3. Note temp PIN from output
4. Create Cloudflare DNS record (if custom domain)
5. Fork n8n workflows for client-specific customization

**Phase 2: Provision (20 minutes)**

6. Verify environment variables are set
7. Start PostgreSQL (if not running): `brew services start postgresql@14`
8. Start n8n (if not running): `n8n start`
9. Start Customer Portal: `python3 api.py --port 8768`
10. Verify portal health: `curl http://localhost:8768/api/portal/health`

**Phase 3: Validate (30 minutes)**

11. Run VALI Pre-Launch Checklist
12. Test client login with temp PIN
13. Complete onboarding wizard as client would
14. Verify all services visible in portal
15. Test chat functionality
16. Trigger one sample workflow in n8n
17. Verify data flows to correct tables

**Phase 4: Go-Live (10 minutes)**

18. Run final backup: `python3 scripts/backup_verify.py`
19. Update DNS to point to production (if custom domain)
20. Verify HTTPS: `curl -s https://portal.systack.net/api/portal/health`
21. Send go-live notification to client (CHATTY template)
22. Activate monitoring (fleet health check)

**Phase 5: Handoff (15 minutes)**

23. Document deployment in pipeline tracker
24. Schedule 48-hour check-in
25. Update weekly metrics dashboard

**Total time: ~90 minutes**

---

## 4. Rollback Procedure

### When to Rollback

Trigger rollback immediately if:
- Service health < 50% for >10 minutes
- Client data corruption detected
- Security incident (unauthorized access)
- Critical functionality broken (login, chat, core workflows)
- Client explicitly requests rollback

### Rollback Steps

| Step | Action | Time | Validation |
|------|--------|------|------------|
| 1 | **Stop services** — Kill all Flask processes: `kill $(lsof -t -i :8768,8766,8767,8770,8772)` | 1 min | `lsof -i :8768` shows nothing |
| 2 | **Restore database** — Use most recent verified backup: `psql -d systack_memory < backup_file.sql` | 2-5 min | `psql -c "SELECT COUNT(*) FROM saos_clients"` matches expected |
| 3 | **Verify backup integrity** — Run `scripts/backup_verify.py` on restored DB | 3 min | All checks PASS |
| 4 | **Restart services** — Start in order: PostgreSQL → n8n → Customer Portal → others | 3 min | Health checks return 200 |
| 5 | **Verify client access** — Login as client, check services | 2 min | Client can log in |
| 6 | **Notify stakeholders** — Alert client + Green via iMessage/Slack | 1 min | Messages sent |
| 7 | **Document incident** — Log to `incident_log`, create post-mortem ticket | 5 min | Incident recorded |

### Data Recovery

If only partial rollback needed (one client's data corrupted):
```bash
# Export just that client's data before restore
python3 -c "
import subprocess
client_id = 'X'
# Export client data to JSON
subprocess.run(['pg_dump', '-t', f'saos_clients WHERE id={client_id}', ...])
"
```

### Communication During Rollback

| Audience | Message | Timing |
|----------|---------|--------|
| Client | "We're experiencing a technical issue and are restoring service. ETA: 10 minutes." | Immediate |
| Green | "Rollback initiated for [client]. Reason: [X]. ETA: 10 min." | Immediate |
| Internal | Post-mortem scheduled after resolution | Within 1 hour |

---

## 5. Validation Procedure

### Post-Deployment Validation

After every deployment, run these checks:

```bash
#!/bin/bash
# validation.sh — Run after every deployment

echo "=== SAOS Deployment Validation ==="

# 1. Health checks
echo "1. Checking health endpoints..."
curl -s http://localhost:8768/api/portal/health | grep -q "ok" && echo "  ✅ Customer Portal" || echo "  ❌ Customer Portal"
curl -s http://localhost:8770/api/health | grep -q "ok" && echo "  ✅ Command Center" || echo "  ❌ Command Center"

# 2. Database connectivity
echo "2. Checking database..."
psql -d systack_memory -c "SELECT COUNT(*) FROM saos_clients;" >/dev/null 2>&1 && echo "  ✅ DB OK" || echo "  ❌ DB FAIL"

# 3. n8n
echo "3. Checking n8n..."
curl -s http://localhost:5678/healthz | grep -q "ok" && echo "  ✅ n8n" || echo "  ❌ n8n"

# 4. Backup
echo "4. Checking last backup..."
psql -d systack_memory -t -c "SELECT MAX(started_at) FROM backup_log WHERE verification_status='verified';" | grep -q "2026" && echo "  ✅ Backup verified" || echo "  ❌ No verified backup"

echo "=== Validation Complete ==="
```

---

## Appendix: Quick Reference

### Common Commands

```bash
# Check all service health
for port in 8768 8770 8766 8767 8772 5678 1234; do
    echo -n "Port $port: "
    curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/api/health 2>/dev/null || echo "down"
done

# Restart all services
brew services restart postgresql@14
n8n start &
cd customer-dashboard && python3 api.py --port 8768 &
cd saos-command-center && python3 api.py --port 8770 &

# View logs
tail -f /Users/philliplowe/.openclaw/workspaces/sol/Systack/content/saos/saos-data/logs/customer-dashboard.log

# Run backup manually
python3 scripts/backup_verify.py

# Check fleet health
python3 fleet-health-check.py
```

### Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| Green (CEO) | iMessage: +1-501-274-6231 | Any critical issue |
| SOL (Systems) | Internal | Technical issues |
| PESSI (Risk) | Internal | Security incidents |
| JURIS (Legal) | Internal | Legal/compliance |

---

*This is a living document. Update after every deployment.*
