Based on my analysis of the available memory and the Systack/SAOS automation platform context, I will now construct the Standard Architecture documentation for all five SAOS service types. The memory reveals a webhook-driven, n8n-orchestrated automation stack using Cloudflare tunnels, SQLite databases, and external integrations (Stripe, Google, etc.). I'll synthesize this into canonical architecture docs.

---

# SAOS Standard Architecture Documentation

## Overview

**SAOS** (Systack Automation Operating System) is a service delivery platform built on an n8n-orchestrated, webhook-driven automation stack. Each SAOS service type follows a consistent architectural pattern:

- **Edge Layer**: Cloudflare (DNS + Tunnel)
- **Orchestration Layer**: n8n workflows
- **Data Layer**: SQLite per-client, with optional external CRM sync
- **Integration Layer**: Webhook APIs + external service connectors

---

## 1. Booking Systems

### Purpose
Enable customers to schedule appointments, services, or reservations through an automated workflow that handles availability, confirmation, and calendar integration.

### Components
| Component | Technology | Role |
|-----------|-----------|------|
| Customer Facing UI | Static HTML/JS Form or Client Website | Captures booking intent |
| Webhook Endpoint | n8n Webhook Node | Receives booking payload |
| Validation Logic | n8n Function/Code Node | Validates input, checks conflicts |
| Availability Engine | n8n + External Calendar API | Checks real-time slot availability |
| Notification Service | n8n + Email/SMS Node | Sends confirmations & reminders |
| Data Store | SQLite (per-client) | Persists bookings |
| Calendar Sync | Google Calendar / Outlook API | Creates events |

### Data Flow
```
Customer Form → Cloudflare Edge → n8n Webhook
                                      ↓
                              [Validation Layer]
                                      ↓
                         [Availability Check]
                         ↙              ↘
                    Slot Available    Slot Unavailable
                         ↓                  ↓
                 [Create Booking]    [Return Error]
                         ↓
                 [Save to SQLite]
                         ↓
                 [Calendar Sync]
                         ↓
                 [Confirmation Email]
```

### DB Schema (SQLite)
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    customer_phone TEXT,
    service_type TEXT,
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    status TEXT DEFAULT 'pending', -- pending, confirmed, cancelled, completed
    source TEXT, -- 'website', 'phone', 'referral'
    notes TEXT,
    calendar_event_id TEXT, -- Google Calendar event ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bookings_date ON bookings(booking_date);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_email ON bookings(customer_email);
```

### API Endpoints (Webhook Paths)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/webhook/booking-create` | Submit new booking |
| GET | `/webhook/booking-availability` | Query available slots |
| POST | `/webhook/booking-cancel` | Cancel existing booking |
| POST | `/webhook/booking-reschedule` | Modify booking datetime |

### External Dependencies
- **Google Calendar API** — Event creation and availability checking
- **SendGrid / SMTP** — Confirmation emails
- **Twilio** (optional) — SMS reminders
- **Stripe** (optional) — Deposit/payment processing

### Deployment Topology
- Single n8n instance per client environment
- SQLite file stored in persistent Docker volume
- Cloudflare Tunnel exposes webhook endpoints securely
- No public server required — all traffic ingress through tunnel

---

## 2. Lead Capture Systems

### Purpose
Capture, validate, enrich, and route inbound leads from websites, ads, and landing pages into the client's sales pipeline.

### Components
| Component | Technology | Role |
|-----------|-----------|------|
| Lead Form | HTML Form / Landing Page | Data ingestion |
| Webhook Receiver | n8n Webhook Node | Accepts lead payload |
| Validation Layer | n8n Function Node | Validates required fields |
| Enrichment | n8n HTTP Request Node | Optional: Clearbit, Hunter.io |
| Scoring Logic | n8n Function Node | Assigns lead score |
| Router | n8n Switch Node | Routes by source/industry |
| CRM Sync | n8n Node (Airtable/HubSpot) | Pushes to CRM |
| Notification | n8n Email/Slack Node | Alerts sales team |
| Data Store | SQLite | Lead archive |

### Data Flow
```
Landing Page Form → Cloudflare Edge → n8n Webhook (/saos-lead)
                                              ↓
                                      [Field Validation]
                                              ↓
                                      [Lead Enrichment] (optional)
                                              ↓
                                      [Lead Scoring]
                                              ↓
                                      [Duplicate Check]
                                              ↓
                                      [Save to SQLite]
                                              ↓
                              ┌──────────┴──────────┐
                              ↓                     ↓
                        [CRM Insert]          [Notification]
                              ↓                     ↓
                        HubSpot/Airtable      Email/Slack Alert
```

### DB Schema (SQLite)
```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    business_name TEXT,
    industry TEXT,
    fleet_size INTEGER,
    message TEXT,
    source TEXT, -- 'saos-demo', 'adwords', 'organic', 'referral'
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    lead_score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new', -- new, contacted, qualified, disqualified, converted
    assigned_to TEXT,
    crm_record_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_created ON leads(created_at);
```

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/webhook/saos-lead` | Primary lead ingestion |
| POST | `/webhook/lead-enrich` | Trigger manual enrichment |
| GET | `/webhook/lead-status` | Query lead by email/ID |

### External Dependencies
- **HubSpot / Airtable / Pipedrive** — CRM integration
- **Slack** — Team notifications
- **Clearbit / Hunter.io** (optional) — Email enrichment
- **Google reCAPTCHA** — Form spam protection

### Deployment Topology
- Shared n8n instance can handle multiple lead capture workflows
- SQLite per-client isolation recommended for data separation
- Cloudflare Tunnel for secure webhook exposure
- Form JS embedded on client websites (CORS-enabled)

---

## 3. Customer Portals

### Purpose
Provide authenticated or semi-authenticated interfaces for customers to view status, history, and interact with their data.

### Components
| Component | Technology | Role |
|-----------|-----------|------|
| Portal Frontend | Static HTML/JS (or Client CMS) | UI layer |
| Auth Gateway | n8n Webhook + Token Validation | Session/auth check |
| Data API | n8n Webhook + SQLite Query | CRUD operations |
| Session Store | JWT in localStorage / Cookie | Stateless auth |
| File Storage | Local volume / R2 (optional) | Document delivery |

### Data Flow
```
Customer Browser → Portal Login Form
                          ↓
                  [n8n Auth Webhook]
                          ↓
                  [Validate Token/Password]
                          ↓
                  [Query SQLite for Customer Data]
                          ↓
                  [Return JSON Payload]
                          ↓
                  [Portal JS Renders Dashboard]
```

### DB Schema (SQLite) — Extends bookings/leads
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT, -- bcrypt hashed, optional for simple portals
    auth_token TEXT,
    token_expires_at DATETIME,
    name TEXT,
    phone TEXT,
    company TEXT,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

CREATE TABLE customer_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER REFERENCES customers(id),
    activity_type TEXT, -- 'login', 'view_booking', 'download_invoice'
    details TEXT,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_token ON customers(auth_token);
CREATE INDEX idx_activity_customer ON customer_activity(customer_id);
```

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/webhook/portal-login` | Authenticate customer |
| POST | `/webhook/portal-logout` | Invalidate session |
| GET | `/webhook/portal-data` | Fetch customer records |
| POST | `/webhook/portal-update` | Update customer info |

### External Dependencies
- **Cloudflare Access** (optional) — Zero-trust portal auth
- **SendGrid** — Password reset emails
- **Client CMS** — Portal iframe embedding

### Deployment Topology
- Static portal files served from Cloudflare Pages or client hosting
- n8n acts as backend-for-frontend (BFF)
- SQLite queried directly via n8n Function nodes
- Token-based auth with configurable expiry

---

## 4. Agent Deployments

### Purpose
Deploy autonomous or semi-autonomous AI agents that perform tasks, monitor systems, or interact with users on behalf of the client.

### Components
| Component | Technology | Role |
|-----------|-----------|------|
| Agent Core | n8n Workflow + AI Node | Decision engine |
| Trigger Layer | n8n Schedule / Webhook / Poll | Activation mechanism |
| Memory Store | SQLite / n8n Static Data | Context persistence |
| Tool Registry | n8n HTTP Request + Custom Nodes | External tool access |
| Output Channel | Email / Slack / API Callback | Result delivery |
| Monitor | n8n Execution Log | Observability |

### Data Flow
```
Trigger (Schedule/Webhook/Event)
              ↓
    [Agent Workflow Activation]
              ↓
    [Load Context from SQLite]
              ↓
    [Decision / AI Processing]
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
[Action Required]   [No Action]
    ↓                   ↓
[Execute Tool]      [Log & Sleep]
    ↓
[Save Result]
    ↓
[Notify / Callback]
```

### DB Schema (SQLite)
```sql
CREATE TABLE agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    trigger_type TEXT, -- 'scheduled', 'webhook', 'manual'
    status TEXT DEFAULT 'running', -- running, completed, failed, paused
    input_payload TEXT,
    output_payload TEXT,
    error_message TEXT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE TABLE agent_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    memory_key TEXT,
    memory_value TEXT,
    expires_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_runs_agent ON agent_runs(agent_id);
CREATE INDEX idx_agent_runs_status ON agent_runs(status);
CREATE INDEX idx_agent_memory_agent ON agent_memory(agent_id);
CREATE INDEX idx_agent_memory_key ON agent_memory(memory_key);
```

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/webhook/agent-trigger` | Manual agent activation |
| POST | `/webhook/agent-config` | Update agent parameters |
| GET | `/webhook/agent-status` | Check agent health/runs |
| POST | `/webhook/agent-pause` | Pause agent execution |

### External Dependencies
- **OpenAI / Anthropic API** — LLM inference
- **Client APIs** — Domain-specific tool access
- **Slack / Discord** — Agent communication channel
- **SERP APIs** (optional) — Web search capability

### Deployment Topology
- Each agent = one n8n workflow
- Scheduled triggers use n8n Cron node
- Webhook triggers for event-driven agents
- SQLite stores agent state between runs
- Execution logs provide audit trail

---

## 5. CRM Integrations

### Purpose
Synchronize data bi-directionally between SAOS systems and external CRM platforms, ensuring consistency and reducing manual data entry.

### Components
| Component | Technology | Role |
|-----------|-----------|------|
| Sync Orchestrator | n8n Workflow | Master sync logic |
| Source Connector | n8n Native Node / Webhook | Read from SAOS |
| Target Connector | n8n CRM Node / API | Write to CRM |
| Mapping Layer | n8n Set/Function Node | Field transformation |
| Conflict Resolver | n8n Switch + Function | Handle duplicates/conflicts |
| Sync Log | SQLite | Audit trail |
| Scheduler | n8n Cron Node | Periodic sync trigger |

### Data Flow
```
[n8n Cron Trigger] or [Webhook Event]
              ↓
    [Fetch SAOS Records (SQLite)]
              ↓
    [Fetch CRM Records (API)]
              ↓
    [Compare & Detect Changes]
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
[New in SAOS]     [Updated in CRM]
    ↓                   ↓
[Map & Insert]    [Map & Update]
    ↓                   ↓
    └─────────┬─────────┘
              ↓
    [Write to Sync Log]
              ↓
    [Error Handling if Failed]
```

### DB Schema (SQLite)
```sql
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sync_type TEXT, -- 'lead', 'booking', 'customer'
    direction TEXT, -- 'to_crm', 'from_crm'
    source_id TEXT,
    target_id TEXT,
    source_table TEXT,
    target_system TEXT, -- 'hubspot', 'airtable', 'pipedrive'
    status TEXT DEFAULT 'pending', -- pending, success, failed, conflict
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    payload_hash TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE TABLE crm_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    saos_field TEXT NOT NULL,
    crm_field TEXT NOT NULL,
    crm_system TEXT NOT NULL,
    transform_rule TEXT, -- 'uppercase', 'date_format', etc.
    is_required BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_status ON sync_log(status);
CREATE INDEX idx_sync_type ON sync_log(sync_type);
CREATE INDEX idx_sync_source ON sync_log(source_id);
CREATE INDEX idx_mappings_system ON crm_mappings(crm_system);
```

### API Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/webhook/crm-sync` | Trigger manual sync |
| POST | `/webhook/crm-config` | Update field mappings |
| GET | `/webhook/crm-status` | Check sync health |
| POST | `/webhook/crm-resync` | Force full re-sync |

### External Dependencies
- **HubSpot API** — Contacts, deals, engagements
- **Airtable API** — Flexible database sync
- **Pipedrive / Salesforce** — Alternative CRMs
- **Zapier** (optional) — Fallback connector

### Deployment Topology
- Sync workflows run on configurable schedule (default: every 15 min)
- Webhook-triggered sync for real-time updates
- SQLite sync_log provides idempotency and retry capability
- Field mappings stored in DB for client-specific customization

---

## Shared Infrastructure

### Across All Service Types

| Layer | Component | Notes |
|-------|-----------|-------|
| Edge | Cloudflare DNS + Tunnel | All traffic ingress |
| Compute | n8n Docker Container | Per-client or shared |
| Storage | SQLite (Docker volume) | Persistent, portable |
| Secrets | n8n Credentials Vault | API keys, tokens |
| Monitoring | n8n Execution Log | Built-in observability |
| Backup | Volume snapshot + Export | Manual or scripted |

### Naming Conventions
- Webhook paths: `/webhook/{client}-{service}-{action}-{version}`
- DB files: `{client}_{service}.db`
- Workflow IDs: `{ClientName}_{Service}_{Action}`

### Security Model
- Webhooks accept POST by default; GET for queries
- No sensitive data in URL parameters
- API keys stored in n8n credential vault, never in code
- SQLite files backed up before schema migrations

---

## Summary Table

| Service | Primary Trigger | Data Store | Key External |
|---------|-----------------|------------|--------------|
| Booking | Form POST | bookings table | Google Calendar |
| Lead Capture | Form POST | leads table | CRM (HubSpot) |
| Customer Portal | Auth Token | customers table | Email/SMTP |
| Agent | Schedule/Event | agent_runs table | LLM API |
| CRM Integration | Cron/Webhook | sync_log table | CRM API |

---

This documentation provides the canonical reference for implementing any SAOS service type. All architectures share the same foundational pattern (n8n + SQLite + Cloudflare Tunnel) while varying in their specific components, schemas, and external integrations based on service purpose.