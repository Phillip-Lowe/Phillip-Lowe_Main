# Systack Private — Local Dashboard Setup

## Overview

The local dashboard replaces Slack for Private tier clients. It shows:
- Real-time automation activity
- Pending review items
- System health (n8n, Ollama, Postgres)
- SMS notification log

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  n8n flows  │────▶│  SQLite DB   │────▶│  Dashboard      │
│  (local)    │     │  (local)     │     │  (local server) │
└─────────────┘     └──────────────┘     └─────────────────┘
       │                                         │
       │                    ┌────────────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐     ┌──────────────┐
│  SMS (Twilio)│     │  Browser     │
│  (outbound) │     │  (localhost) │
└─────────────┘     └──────────────┘
```

## How It Works

1. **n8n flows** write execution data to **local SQLite** (n8n's default)
2. **Dashboard server** reads from SQLite and serves HTML
3. **Browser** displays the dashboard at `http://localhost:8080`
4. **SMS** still sent via Twilio for urgent alerts

## Setup Steps

### 1. Enable n8n SQLite Logging

In n8n settings, execution logging is already enabled by default. The database is at:
- `~/.n8n/database.sqlite`

### 2. Create Dashboard Server

The dashboard is a simple Python Flask server that reads from n8n's SQLite.

**File:** `templates/private/dashboard-server.py`

### 3. Install Dependencies

```bash
pip install flask
```

### 4. Run the Dashboard

```bash
python templates/private/dashboard-server.py
```

Access at: `http://localhost:8080`

## Dashboard Features

### Real-time Activity Feed
- Shows all automation runs
- Color-coded: success (green), error (red), warning (yellow)
- Click to expand details

### Pending Review Queue
- Items requiring human approval
- One-click approve/reject
- Shows context (invoice, booking, etc.)

### System Health
- n8n status
- Ollama model status
- Database connection
- Disk space

### SMS Log
- History of SMS notifications sent
- Delivery status
- Resend button

## Data Flow

### n8n Flow → Dashboard

Every n8n flow now includes an extra node:

```
[Process] → [Log to Dashboard] → [SMS if urgent]
```

The "Log to Dashboard" node writes to a simple SQLite table:

```sql
CREATE TABLE dashboard_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT,
    workflow_name TEXT,
    execution_id TEXT,
    event_type TEXT,  -- 'booking', 'invoice', 'onboard', 'error', 'warning'
    title TEXT,
    detail TEXT,
    status TEXT,  -- 'pending', 'completed', 'error'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notified BOOLEAN DEFAULT 0
);
```

### WebSocket Updates

The dashboard uses WebSocket for real-time updates:
- n8n flow writes to SQLite
- Dashboard server detects new row via polling
- Pushes update to browser via WebSocket
- Browser updates without refresh

## Security

- Dashboard only accessible from localhost
- No external network exposure
- No cloud APIs used
- All data stays on local machine

## Customization

Clients can customize:
- Brand colors (CSS variables)
- Logo
- Notification preferences (SMS thresholds)
- Auto-approve rules

## Files

| File | Purpose |
|------|---------|
| `local-dashboard.html` | Static dashboard UI (demo) |
| `dashboard-server.py` | Flask server (reads n8n SQLite) |
| `n8n-log-node.json` | Reusable n8n node for logging |

## Next Steps

1. Build `dashboard-server.py` (Flask + SQLite reader)
2. Create reusable n8n node for dashboard logging
3. Add WebSocket for real-time updates
4. Test with actual n8n executions
5. Add SMS delivery status tracking

## Note

The current `local-dashboard.html` is a **static demo**. The real dashboard will be served by `dashboard-server.py` reading live n8n data.
