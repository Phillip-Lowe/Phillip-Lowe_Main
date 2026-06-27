# SAOS Customer Dashboard — Technical Specification

**Document ID:** SYS-DASHBOARD-SPEC-v1.0
**Prepared for:** ORACLE (System Design Agent)
**Prepared by:** SOL
**Date:** June 25, 2026
**Status:** COMPLETE — Authoritative

---

## Executive Summary

The SAOS Customer Dashboard is a **Flask-based web application** serving a single-page HTML frontend to SAOS Fleet subscribers. It provides:
- PIN-based authentication
- Real-time chat with AI agents
- Fleet status monitoring
- Task tracking
- Tier-specific service documentation
- Mobile-responsive design

**Access:** Tailscale VPN only (no public internet exposure)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT BROWSER                          │
│              (Tailscale-connected device)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              TAILSCALE SERVE PROXY                           │
│     https://phillips-macbook-air.tail573d57.ts.net           │
│                    /dashboard/*  ─────►                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           FLASK API (Python) — Port 8768                      │
│  • Serves static HTML/CSS/JS (index.html)                    │
│  • RESTful API endpoints (/api/*)                             │
│  • PostgreSQL database backend                                │
│  • PIN-based authentication + session tokens                │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              POSTGRESQL DATABASE                             │
│  • saos_clients (client profiles, PINs, tiers)               │
│  • client_auth_tokens (session management)                  │
│  • tasks (task queue and history)                            │
│  • agents (fleet metadata, status)                          │
│  • messages (chat history)                                   │
│  • conversations (chat threads)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
Systack/content/saos/saos-data/customer-dashboard/
├── index.html                      # Frontend SPA (119 KB, ~2,900 lines)
├── api.py                          # Flask backend (43 KB, ~1,100 lines)
├── schema.sql                      # Database schema (2.7 KB)
├── admin_client.py                 # CLI admin tool (6.3 KB)
├── n8n-chat-bridge.json            # n8n chat integration workflow
├── n8n-email-dispatcher.json       # n8n email notification workflow
├── deliverables/                   # Client deliverables directory
│   └── [task-specific files]
├── README.md                       # Basic overview
├── migration_v2.1.sql              # DB migration script
├── populate_task_descriptions.sql  # Task seed data
├── seed_agents.sql                 # Agent seed data
│
# PDF Documentation (generated from markdown)
├── SAOS-Service-Manual-v5.0.pdf    # 393 KB (latest)
├── SAOS-Dashboard-User-Guide-v3.0.pdf  # 481 KB
├── SAOS-Dashboard-Mobile-Access-Guide-v2.0.pdf  # 281 KB
├── SAOS-Quick-Start-Guide-v5.0.pdf  # 279 KB
├── SAOS-Architecture-Overview-v4.0.pdf  # 429 KB
│
# Markdown Sources
├── SAOS-Service-Manual-v5.0.md
├── SAOS-Dashboard-User-Guide-v3.0.md
├── SAOS-Dashboard-Mobile-Access-Guide-v2.0.md
├── SAOS-Quick-Start-Guide-v5.0.md
├── SAOS-Architecture-Overview-v4.0.md
│
# Backup files
├── index.html.backup.20260624_052514
├── index.html.broken
└── index.html.fixed
```

---

## Frontend (`index.html`)

### Technology Stack
- **Pure HTML/CSS/JavaScript** — No frameworks (no React, Vue, etc.)
- **CSS:** Custom properties (CSS variables) for theming
- **JS:** Vanilla JavaScript with fetch API for HTTP requests
- **No build step** — Direct file serving

### Design System

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-deep` | `#001a2d` | Page background |
| `--bg-card` | `rgba(255,255,255,0.04)` | Card backgrounds |
| `--accent` | `#00a1db` | Primary buttons, links |
| `--accent-bright` | `#00c5e0` | Active states, highlights |
| `--text` | `#e2e8f0` | Primary text |
| `--text-muted` | `#94a3b8` | Secondary text |
| `--green` | `#22c55e` | Success, online status |
| `--amber` | `#f59e0b` | Warning, pending status |
| `--red` | `#ef4444` | Error, failed status |
| `--purple` | `#8b5cf6` | Accent gradients |
| `--radius` | `14px` | Card corners |
| `--radius-sm` | `10px` | Button corners |

### Layout
- **Mobile-first responsive design**
- **CSS Grid + Flexbox** for layouts
- **Safe area insets** for iPhone notch (`env(safe-area-inset-top)`)
- **Touch targets:** Minimum 44px for mobile buttons

### Application Structure

```javascript
// Main app object (simplified)
window.App = {
  clientId: null,
  token: null,
  currentTab: 'dashboard',
  currentConversationId: null,
  
  init() { /* Initialize app */ },
  checkAuth() { /* Check localStorage for token */ },
  login(clientId, pin) { /* POST /api/auth/login */ },
  logout() { /* Clear localStorage + POST /api/auth/logout */ },
  
  // Tab handlers
  showTab(tabName) { /* Switch visible tab */ },
  renderDashboard() { /* Fleet status + metrics */ },
  renderChat() { /* Conversation list + message area */ },
  renderServices() { /* Tier-specific service cards */ },
  renderTasks() { /* Task history table */ },
  renderDocs() { /* Documentation iframe/links */ },
  renderActivity() { /* Activity log (v2.1) */ },
  
  // Chat
  loadConversations() { /* GET /api/chat/conversations */ },
  loadMessages(convId) { /* GET /api/chat/conversations/{id}/messages */ },
  sendMessage(text) { /* POST /api/chat/conversations/{id}/messages */ },
  pollForUpdates() { /* GET /api/chat/poll every 5s */ },
  
  // API helper
  apiFetch(endpoint, options) { /* Wrapper with auth header */ }
};
```

### Dynamic API Base Detection (Critical for Tailscale)

```javascript
// Runtime detection of /dashboard prefix for reverse proxy
const API_BASE = (() => {
  const path = window.location.pathname;
  if (path.startsWith('/dashboard/')) return '/dashboard';
  if (path.startsWith('/dashboard')) return '/dashboard';
  return '';
})();

// All API calls use: `${API_BASE}/api/...`
// This prevents "The string did not match the expected pattern" errors
```

---

## Backend (`api.py`)

### Technology Stack
- **Python 3** with Flask
- **Flask-CORS** for cross-origin requests
- **psycopg2** for PostgreSQL
- **No ORM** — Raw SQL with RealDictCursor

### Database Configuration
```python
DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")
```

### Authentication System

#### PIN-Based Login Flow
```
1. Client enters Client ID + PIN
2. POST /api/auth/login
3. Server verifies PIN hash in saos_clients table
4. Generates secure token (secrets.token_urlsafe(32))
5. Stores token hash in client_auth_tokens table
6. Returns token to client
7. Client stores in localStorage
8. All subsequent requests include: Authorization: Bearer <token>
```

#### Session Management
- **Token expiry:** 30 days
- **Auto-renew:** On activity (last_used_at updated)
- **Storage:** Browser localStorage
- **Logout:** Clears localStorage + revokes token in DB

### API Endpoints

#### Authentication
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/register` | POST | No | First-time client registration |
| `/api/auth/login` | POST | No | Get Bearer token |
| `/api/auth/logout` | POST | Yes | Revoke token |
| `/api/auth/me` | GET | Yes | Current client info |

#### Portal (Fleet Data)
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/portal/health` | GET | No | Health check |
| `/api/portal/status` | GET | Yes | Fleet overview + client record |
| `/api/portal/tasks` | GET | Yes | Task history (last 50) |
| `/api/portal/agents` | GET | No | All agent states |
| `/api/portal/client` | GET | Yes | Single client details |

#### Chat
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/chat/conversations` | GET | Yes | List conversations |
| `/api/chat/conversations` | POST | Yes | Create conversation |
| `/api/chat/conversations/{id}/messages` | GET | Yes | Get messages |
| `/api/chat/conversations/{id}/messages` | POST | Yes | Send message |
| `/api/chat/conversations/{id}/close` | POST | Yes | Close conversation |
| `/api/chat/poll` | GET | Yes | Poll for updates |
| `/api/chat/webhook/agent-response` | POST | No | Webhook for agents |

#### Admin (Protected)
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/admin/clients` | GET | Admin | List all clients |
| `/api/admin/clients` | POST | Admin | Create new client |

### Database Schema

#### saos_clients
```sql
CREATE TABLE saos_clients (
    id SERIAL PRIMARY KEY,
    client_id VARCHAR(50) UNIQUE NOT NULL,  -- "TEST-001"
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    pin_hash VARCHAR(64),  -- SHA256 of PIN
    tier VARCHAR(20),       -- personal/business/enterprise/etc.
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### client_auth_tokens
```sql
CREATE TABLE client_auth_tokens (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES saos_clients(id),
    token_hash VARCHAR(64) NOT NULL,  -- SHA256 of token
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '30 days',
    last_used_at TIMESTAMP,
    revoked_at TIMESTAMP
);
```

#### tasks
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES saos_clients(id),
    agent_name VARCHAR(50),
    task_type VARCHAR(50),
    description TEXT,
    status VARCHAR(20),  -- pending/running/completed/failed/dead
    priority VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

#### messages + conversations
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES saos_clients(id),
    title VARCHAR(200),
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    sender_type VARCHAR(20),  -- 'user' or 'agent'
    sender_name VARCHAR(50),  -- agent name or 'You'
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Network & Deployment

### Tailscale Configuration
```bash
# Tailscale serve config
tailscale serve https /dashboard/ http://localhost:8768
```

**URL:** `https://phillips-macbook-air.tail573d57.ts.net/dashboard/`

### LaunchAgent (Auto-Start)
**File:** `~/Library/LaunchAgents/net.systack.customer-dashboard.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>net.systack.customer-dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/philliplowe/.openclaw/workspaces/sol/Systack/content/saos/saos-data/customer-dashboard/api.py</string>
        <string>--port</string>
        <string>8768</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>StandardErrorPath</key>
    <string>/tmp/customer-dashboard.err</string>
</dict>
</plist>
```

**Commands:**
```bash
launchctl load ~/Library/LaunchAgents/net.systack.customer-dashboard.plist
launchctl unload ~/Library/LaunchAgents/net.systack.customer-dashboard.plist
launchctl list | grep customer-dashboard
```

---

## Service Tier Configuration

The dashboard adapts content based on client's `tier` field:

| Tier | Price | Agents | VPS | Support | Docs Access |
|------|-------|--------|-----|---------|-------------|
| personal | $49/mo | 3 | Shared | Email | Base |
| personal+ | $99/mo | 5 | Shared | Priority | Base |
| business | $299/mo | 10 | 16GB | Same-day | Base + Enterprise |
| enterprise | $799/mo | 10 | 32GB | Dedicated | All |
| private | $799/mo | 10 | On-prem | Dedicated | All + Compliance |
| accelerate | $249/mo | 5 | Cloud | Email | Base |

**Tier-specific content in Services tab:**
- Business: Invoice processing, lead qualification, team Slack, reports
- Enterprise: Above + on-premise option, HIPAA, white-glove, 4hr SLA
- Private: Document extraction, compliance audit

---

## Known Issues & Gotchas

### 1. iOS Safari `.ts.net` Certificate Trust
**Issue:** iOS Safari doesn't trust Tailscale `.ts.net` certificates by default
**Status:** OPEN — needs investigation
**Workaround:** Use Tailscale app + "Use Tailscale DNS" setting

### 2. Reverse Proxy Path Prefix
**Issue:** When serving behind `/dashboard/` proxy, `fetch('/api/...')` resolves to root origin
**Solution:** `API_BASE` dynamically detects prefix from `window.location.pathname`
**File:** `index.html` line ~300

### 3. iOS Form Validation
**Issue:** iOS Safari blocks form submission with "The string did not match the expected pattern"
**Solution:** Button changed to `type="button"` with `onclick` handler
**File:** `index.html` login form

### 4. Mobile Layout
**Issue:** Navigation overflow on small screens
**Solution:** Compact nav, larger sidebar toggle, shorter placeholders
**File:** `index.html` CSS media queries

---

## Dependencies

### Python (for api.py)
```
flask>=2.0
flask-cors>=3.0
psycopg2-binary>=2.9
```

### External Services
- PostgreSQL (local or remote)
- Tailscale (for external access)
- n8n (optional, for chat bridge)

---

## Files Critical for ORACLE

When designing systems or researching solutions for the dashboard:

1. **`index.html`** — Frontend logic, API calls, auth flow, tab rendering
2. **`api.py`** — Backend endpoints, database queries, auth middleware
3. **`schema.sql`** — Database structure
4. **`n8n-chat-bridge.json`** — How chat messages route to agents
5. **`admin_client.py`** — How clients are provisioned

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-06-22 | Initial dashboard: Overview, Agents, Tasks, Account tabs |
| v2.0 | 2026-06-24 | Complete rebuild: Chat, Dashboard, Services, Tasks, Docs tabs |
| v2.1 | 2026-06-25 | Added Activity tab, PIN auth, session tokens, mobile fixes |

---

**Next Version:** v2.2 planned for iOS Safari cert fix + documentation updates

**Document Status:** AUTHORITATIVE — This is the single source of truth for dashboard technical details.

**Builder:** SOL 🛰️
**Date:** June 25, 2026
