# SAOS Customer Dashboard User Guide

**Document ID:** SYS-DASHBOARD-GUIDE-v1.0  
**Version:** 1.0  
**Status:** LIVE  
**Prepared for:** SAOS Business & Enterprise Fleet Clients  
**Prepared by:** Systack  
**Builder:** SOL + ASSEMBLY  
**Source System:** SAOS Customer Portal v2026.06  
**Date:** June 23, 2026  
**Support:** support@systack.net

---

## Your Customer Dashboard

The SAOS Customer Dashboard is your command center for monitoring your AI fleet, tracking tasks, and accessing documentation.

---

## 1. Accessing the Dashboard

### Requirements
- Tailscale installed and connected to your tailnet
- Client ID (provided after signup)

### URL
```
https://phillips-macbook-air.tail573d57.ts.net/dashboard/?client_id=YOUR_ID
```

**Note:** Replace `YOUR_ID` with your assigned client ID. Bookmark this URL for quick access.

---

## 2. Dashboard Tabs

### Overview Tab
Your fleet at a glance:
- **Status Banner** — Green (healthy), Amber (degraded), or Red (down)
- **Metrics Cards** — Pending tasks, running tasks, completed tasks, active agents
- **VPS Info** — Server specs, uptime, resource usage
- **Recent Activity** — Latest tasks and status changes
- **Auto-refresh:** Every 30 seconds

### Agents Tab
Full fleet visibility:
- **Agent Cards** — Each agent shows:
  - Emoji + Name (e.g., 🛰️ SOL)
  - Role description
  - Status dot (green = online, amber = busy, gray = offline)
  - Current task (if any)
  - Total tasks completed
- **10 Agents** — All fleet members visible in a responsive grid

### Tasks Tab
Task history and tracking:
- **Status Filtering** — Pending, Running, Completed, Failed, Dead
- **Task Details** — Type, assigned agent, priority, timestamps
- **Color-coded** — Green (done), Blue (running), Amber (pending), Red (failed)
- **Last 50 tasks** displayed by default

### Documents Tab
Your document library:
- **Service Manual** — Full SAOS documentation
- **Quick Start Guide** — Getting started instructions
- **Enterprise Deployment Guide** — For Enterprise clients only
- **Tier-based Access** — Business vs Enterprise see different docs

### Account Tab
Your subscription details:
- Business name and email
- Plan type (Business or Enterprise)
- Server IP address
- Active agent count
- Support contact information

---

## 3. Dashboard Features

### Real-time Updates
The dashboard polls the API every 30 seconds. No manual refresh needed.

### Responsive Design
Works on desktop, tablet, and mobile devices within your Tailscale network.

### Dark Theme
Navy base (`#001a2d`) with Systack cyan accents. Easy on the eyes for monitoring.

---

## 4. Troubleshooting

| Problem | Solution |
|---------|----------|
| Dashboard won't load | Ensure Tailscale is connected: `tailscale status` |
| "Client not found" error | Check your client ID in the URL parameter |
| Agents show as offline | Check VPS status in Overview tab or contact support |
| Tasks not updating | Wait 30 seconds for auto-refresh, or reload page |
| PDF won't download | Ensure browser allows popups/downloads from tailnet |
| Slow loading | Check Tailscale connection strength; may need closer exit node |

---

## 5. Security Notes

- Dashboard is **tailnet-only** — no public internet access
- HTTPS via Tailscale TLS termination
- No login required within tailnet (auth via Tailscale identity)
- Client ID scopes data to your account only

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-23 | Initial release |

**Latest version:** https://systack.net/docs/client/SAOS-Dashboard-User-Guide-v1.0.pdf
