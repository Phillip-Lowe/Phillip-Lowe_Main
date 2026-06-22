---
title: "SyStack Enterprise Deployment Guide"
subtitle: "Multi-Location, Compliance-Ready Infrastructure"
version: "1.0"
date: "2026-06-19"
status: "PRODUCTION READY"
classification: "SYSTACK INTERNAL"
author: "SOL (Systack Operations Layer)"
---

# SyStack Enterprise Deployment Guide

## Overview

This guide covers the automated provisioning of **SAOS Enterprise** and **Enterprise XL** tiers with:
- Multi-region VPS deployment (up to 5 locations)
- SOC 2 / HIPAA / GDPR compliance documentation
- White-label dashboard generation
- Tailscale mesh networking across locations
- Automated audit logging and monitoring

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Vultr API Key** | With instance creation permissions |
| **Tailscale Auth Key** | Reusable, tagged for `tag:saos-client` |
| **Client Info** | ID, email, brand colors, logo URL |
| **Compliance Needs** | SOC2, HIPAA, GDPR, CCPA (comma-separated) |

---

## Quick Start

### 1. Provision Enterprise Infrastructure

```bash
cd /tmp/systack-saas-init

python3 scripts/provision_enterprise.py \
  --client-id ACME-CORP \
  --tier enterprise \
  --locations ord,lax,lon \
  --email "admin@acme.com" \
  --agent-name "AcmeAgent" \
  --compliance SOC2,HIPAA,GDPR \
  --wait
```

### 2. Generate White-Label Dashboard

```bash
python3 scripts/generate_dashboard.py \
  --client-id ACME-CORP \
  --client-name "Acme Corporation" \
  --primary-color "#1a365d" \
  --accent-color "#0ea5e9" \
  --logo-url "https://acme.com/logo.png" \
  --locations ord,lax,lon \
  --compliance SOC2,HIPAA,GDPR
```

### 3. Deploy Dashboard to VPS

```bash
# Copy dashboard to primary VPS
rsync -av dashboards/ACME-CORP/ root@<primary-ip>:/var/www/dashboard/

# Configure nginx (on VPS)
ssh root@<primary-ip> "
  apt install -y nginx
  ln -s /opt/systack-dashboard/nginx.conf /etc/nginx/sites-enabled/dashboard
  systemctl restart nginx
"
```

---

## Available Regions

| Region | City | Country | Compliance |
|--------|------|---------|------------|
| ord | Chicago | US | SOC 2, GDPR |
| lax | Los Angeles | US | SOC 2, CCPA |
| lon | London | UK | GDPR, UK-GDPR |
| ams | Amsterdam | NL | GDPR |
| fra | Frankfurt | DE | GDPR, BSI |

---

## Tier Specifications

| Spec | Enterprise | Enterprise XL |
|------|-----------|---------------|
| **Price** | $799/mo | Custom |
| **VCPU** | 8 | 16 |
| **RAM** | 32 GB | 64 GB |
| **Storage** | 320 GB NVMe | 640 GB NVMe |
| **Bandwidth** | 6 TB | Unmetered |
| **Backups** | Hourly | Continuous |
| **DDoS Protection** | ✅ Included | ✅ Included |
| **Multi-Location** | Up to 5 | Unlimited |
| **Custom Agents** | 10+ | Unlimited |

---

## Compliance Documentation

The provisioning script auto-generates compliance documentation in:
`docs/compliance/{client_id}/`

### Generated Documents

| Document | Contents |
|----------|----------|
| `SOC2-Readiness.md` | Controls assessment, gaps, remediation timeline |
| `HIPAA-BAA-Template.md` | Business Associate Agreement template |
| `GDPR-DPA.md` | Data Processing Agreement with subprocessor list |

### Compliance Features Deployed

| Feature | Implementation |
|---------|---------------|
| **Encryption at Rest** | LUKS disk encryption + AES-256-GCM |
| **Encryption in Transit** | TLS 1.3 + Tailscale WireGuard |
| **Audit Logging** | kernel auditd + application logs |
| **Access Control** | RBAC + Tailscale device tags |
| **Backup Encryption** | Encrypted snapshots with 30-day retention |
| **Monitoring** | Continuous health checks |

---

## Architecture

```
                    Client (Tailscale VPN)
                           │
                           ▼
        ┌─────────────────────────────────────┐
        │      Primary VPS (Chicago)          │
        │  ┌─────────┐  ┌─────────────┐     │
        │  │ Agents  │  │ Dashboard   │     │
        │  │ Ollama  │  │ Nginx       │     │
        │  │ n8n     │  │ Compliance  │     │
        │  │ Postgres│  │ Monitor     │     │
        │  └─────────┘  └─────────────┘     │
        └─────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
        ┌──────┐     ┌──────┐      ┌──────┐
        │ LAX  │◄───►│ LON  │◄────►│ AMS  │
        │(warm)│     │(warm)│      │(cold)│
        └──────┘     └──────┘      └──────┘
         (Tailscale mesh — all nodes see all nodes)
```

---

## Verification Checklist

After deployment, verify:

```bash
# Check all VPS instances
python3 -c "
from scripts.provision_vps import VultrProvisioner, load_credentials
prov = VultrProvisioner(load_credentials()['vultr'])
for inst in prov.list_instances():
    if 'ACME-CORP' in inst['label']:
        print(f'{inst[\"label\"]}: {inst[\"status\"]} @ {inst.get(\"main_ip\", \"pending\")}')
"

# Verify Tailscale mesh
ssh root@<primary-ip> "tailscale status | grep saos-"

# Check compliance monitor logs
ssh root@<primary-ip> "tail -20 /var/log/systack-compliance.log"

# Verify dashboard
open https://<primary-ip>/dashboard
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Secondary region fails | Check Vultr capacity; try different region |
| Tailscale not meshing | Verify tags match `tag:saos-client` |
| Dashboard not loading | Check nginx config, firewall port 443 |
| Compliance monitor warnings | Review `/var/log/systack-compliance.log` |

---

## Next Steps

1. **Custom domain** — Point client domain to primary VPS IP
2. **SSL certificate** — Run `certbot` for HTTPS
3. **Client training** — Schedule walkthrough of dashboard
4. **Handoff** — Transfer admin credentials via secure channel

---

*Generated by SOL on 2026-06-19. For updates, edit Markdown source and regenerate PDF.*
