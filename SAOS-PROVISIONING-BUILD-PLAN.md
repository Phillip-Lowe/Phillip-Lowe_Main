# SAOS Client Provisioning Pipeline — Build Plan

**Plan ID:** PLAN-000001  
**Created:** 2026-06-17  
**Status:** ACTIVE (draft)  
**Owner:** ASSEMBLY (builder)  
**Co-builders:** CODY (code implementation), ASSEMBLY (integration)  
**Scope:** Business Fleet ($299/mo) client provisioning end-to-end

---

## Table of Contents

1. [Component Inventory](#1-component-inventory)
2. [Implementation Phases](#2-implementation-phases)
3. [n8n Workflow Node-by-Node Spec](#3-n8n-workflow-node-by-node-spec)
4. [VPS Provisioning Approach](#4-vps-provisioning-approach)
5. [Identity File Generation](#5-identity-file-generation)
6. [Dashboard Requirements](#6-dashboard-requirements)
7. [Error Handling Matrix](#7-error-handling-matrix)
8. [Testing Plan](#8-testing-plan)
9. [Time Estimates](#9-time-estimates)

---

## 1. Component Inventory

### What Exists (Verified Working)

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| **Orchestrator daemon** | `~/.openclaw/workspaces/sol/orchestrator-daemon.py` | ✅ Running (PID 70691) via launchd | Polls Postgres `task_queue`, dispatches to 10 fleet agents |
| **Orchestrator (Phase 1)** | `~/.openclaw/workspaces/sol/orchestrator.py` | ✅ Working | Core dispatcher, task claiming, agent state, retry logic |
| **OpenClaw bridge** | `~/.openclaw/workspaces/sol/openclaw_bridge.py` | ✅ Working | Sub-agent spawning via `openclaw agent --agent <id>` |
| **Postgres task queue** | `systack_memory` DB | ✅ Operational | Tables: `task_queue`, `agent_state`, `execution_log`, `message_bus` |
| **10 fleet agents** | Registered in Postgres | ✅ Seeded | SOL, CODY, ASSEMBLY, VALI, PESSI, ORACLE, ATLAS, CHATTY, GENI, JURIS |
| **n8n instance** | `n8n.systack.net` | ✅ 19 active workflows | SAOS Lead Capture (`saos-lead` webhook) is live |
| **Private templates** | `templates/private/*.json` | ✅ Imported to n8n | 3 workflows: booking, onboarding, invoice |
| **Accelerate templates** | `templates/accelerate/*.json` | ✅ Imported to n8n | Same 3 with cloud integrations (Slack, Google Drive, Calendar) |
| **Stripe buttons** | `systack-site/saos/index.html` | ✅ Active | Business $299/mo, Enterprise $799/mo payment links |
| **Thanks page** | `systack-site/saos/thanks.html` | ✅ Exists | Static page shown after payment |
| **Percy deployment** | Vultr VPS via Tailscale | ✅ Working (Jacqueline) | Reference for how SAOS agents deploy |
| **Percy identity files** | `sol/clients/mcdonalds-gm/percy-workspace/` | ✅ Exists | SOUL.md, AGENTS.md, USER.md, MEMORY.md as templates |
| **SAOS Foundation Spec** | `SAOS-FOUNDATION-SPEC.md` | ✅ Architecture defined | RSI loop, fleet mapping, tier definitions |
| **Template architecture** | `templates/TEMPLATE-ARCHITECTURE.md` | ✅ Documented | Private vs Accelerate substitution map |
| **Stripe catalog** | `saos-products/STRIPE-CATALOG.md` | ✅ Products live | SKUs SAOS-BIZ-M ($299), SAOS-ENT-M ($799) |
| **Client onboarding guide** | `templates/CLIENT-ONBOARDING-GUIDE.md` | ✅ Written | Credential setup guide for clients |
| **Dashboard template** | `templates/private/dashboard.html` + `dashboard-server.py` | ✅ Exists | Flask-based local dashboard with n8n polling |

### What Needs Building

| Component | Priority | Description |
|-----------|----------|-------------|
| **Stripe webhook receiver** | P0 | n8n workflow that receives `checkout.session.completed` |
| **Client record creation** | P0 | Postgres schema + insert for `saos_clients` table |
| **VPS provisioning script** | P0 | Python script or n8n node to call Vultr API |
| **OpenClaw installer** | P0 | Script to install OpenClaw on fresh VPS |
| **Ollama installer** | P0 | Script to install Ollama + pull models |
| **n8n installer** | P0 | Script to install n8n + configure |
| **Template installer** | P0 | Script to import tier-appropriate workflows into client n8n |
| **Identity renderer** | P0 | Jinja2/python template engine for SOUL.md, AGENTS.md, USER.md, MEMORY.md |
| **Health checker** | P0 | Script that validates deployment before notifying client |
| **Client notification** | P0 | Email with Tailscale URL, credentials, setup instructions |
| **Provisioning dashboard** | P1 | Real-time status page showing "Your fleet is live" |
| **Retry/rescue logic** | P1 | Failure recovery, rollback, cleanup on partial deploy |
| **Test mode** | P1 | Flag to run provisioning without real VPS creation or Stripe charges |
| **Provisioning DB schema** | P0 | New tables: `saos_clients`, `saos_deployments`, `saos_provisioning_log` |

### What Needs Research

| Question | Where to Find Answer |
|----------|----------------------|
| How was Percy/Jacqueline actually deployed? | Percy deployment files, Tailscale invite scripts |
| Does Vultr API key exist? | Search `credentials/` or `.env` files |
| What model/config for client agents? | `SAOS-FOUNDATION-SPEC.md` — tier→model mapping |
| How does Tailscale URL get generated? | Tailscale admin console or API docs |
| What email provider for notifications? | Check if SendGrid/SMTP credentials exist |

---

## 2. Implementation Phases

### Phase 0: Foundation (Prerequisites)
**Goal:** All dependencies exist before provisioning pipeline starts.

1. **Vultr API key** — Verify or create API key with `compute:write` scope
2. **Tailscale API key** — Verify or create auth key for programmatic device invites
3. **Stripe webhook signing secret** — Get from Stripe Dashboard → Developers → Webhooks
4. **Email provider** — Verify SendGrid/SMTP credentials for client notifications
5. **Provisioning DB schema** — Create tables in `systack_memory`:
   - `saos_clients` (id, stripe_customer_id, stripe_subscription_id, email, name, tier, status, created_at)
   - `saos_deployments` (id, client_id, vps_id, vps_ip, tailscale_ip, tailscale_url, ssh_key, status, created_at, deployed_at)
   - `saos_provisioning_log` (id, deployment_id, step_name, status, output, error, timestamp)
6. **Test Stripe mode** — Ensure `test` mode can trigger webhooks without real charges

**Deliverable:** All credentials verified, schema created, test mode functional.

### Phase 1: Stripe Webhook + Client Record
**Goal:** Payment completion creates a client record in Postgres.

1. Create n8n workflow: `SAOS Provisioning Trigger`
2. Webhook node: `POST /webhook/saos-provision` (or Stripe native webhook)
3. Validate webhook signature (Stripe signature verification)
4. Extract: `customer.id`, `customer.email`, `subscription.id`, `subscription.items[0].price.product`
5. Map product SKU → tier (`SAOS-BIZ-M` → `business`, `SAOS-ENT-M` → `enterprise`)
6. Insert `saos_clients` record (status: `provisioning`)
7. Create `saos_deployments` record (status: `pending`)
8. Log to `saos_provisioning_log`
9. Trigger Phase 2 via message_bus or direct task_queue insert

**Deliverable:** n8n workflow that receives Stripe events and writes to Postgres.

### Phase 2: VPS Provisioning
**Goal:** Client gets a deployed VPS with OpenClaw + Ollama + n8n.

1. Read `saos_deployments` record where status = `pending`
2. Call Vultr API: `POST /v2/instances` with:
   - Region: `ord` (Chicago) or `dfw` (Dallas)
   - Plan: `vc2-1c-2gb` for Business? Wait — spec says 16GB minimum. Check `SAOS-FOUNDATION-SPEC.md`: Business Fleet needs 16GB. Vultr plan: `vhp-2c-8gb` or `vhp-4c-16gb`. **Use `vhp-4c-16gb` for Business Fleet.**
   - OS: `Ubuntu 22.04 LTS`
   - Label: `saos-{client_id}`
   - User data: cloud-init script for base setup
3. Wait for VPS to reach `running` state (poll Vultr API)
4. Generate SSH keypair for client access (or use existing Systack deploy key)
5. SSH into VPS and run provisioning script:
   - Install Tailscale, join tailnet
   - Install Docker + Docker Compose
   - Install OpenClaw (via official installer or Docker)
   - Install Ollama, pull model (`qwen2.5:14b` for Business)
   - Install n8n (Docker)
   - Configure firewall (ufw: allow 22, 5678, 11434)
6. Capture VPS IP, Tailscale IP, Tailscale URL
7. Update `saos_deployments` (status: `vps_ready`)

**Deliverable:** Python script (`provision_vps.py`) that can create and configure a VPS.

### Phase 3: Template Deployment
**Goal:** Client n8n has working workflows for their tier.

1. Determine tier from `saos_clients.tier`
2. Select template directory: `templates/private/` or `templates/accelerate/`
3. Import workflows via n8n REST API:
   - `POST /api/v1/workflows` with JSON payload
   - Or use n8n CLI `n8n import:workflow --separate`
4. Configure credentials in client n8n:
   - Postgres: cloud VPS host, client-specific DB name
   - Stripe: client-provided (marked as "pending" initially)
   - Slack/Google: client-provided (marked as "pending")
5. Activate workflows
6. Update `saos_deployments` (status: `templates_deployed`)

**Deliverable:** Script (`deploy_templates.py`) that imports and activates tier-appropriate workflows.

### Phase 4: Identity File Generation
**Goal:** Client agent has personalized SOUL.md, AGENTS.md, USER.md, MEMORY.md.

1. Read client data from `saos_clients` (name, email, business_name, industry)
2. Load base templates (see Section 5 for template paths)
3. Render with Jinja2:
   - `client_name` → agent name (e.g., Percy, Alex)
   - `business_name` → from Stripe customer name
   - `industry` → from onboarding form or Stripe metadata
   - `tier` → `business` or `enterprise`
   - `owner_name` → client's name
   - `tailscale_url` → generated URL
4. Write to client workspace: `~/.openclaw/workspaces/{client_name}/`
5. Restart OpenClaw to pick up new workspace
6. Update `saos_deployments` (status: `identity_ready`)

**Deliverable:** Identity renderer script + template files.

### Phase 5: Health Check + Verification
**Goal:** VALI validates that everything works before client sees it.

1. Run health checks:
   - VPS: `ping` IP, `curl` n8n health endpoint
   - Ollama: `curl localhost:11434/api/tags` (model loaded)
   - n8n: `curl localhost:5678/healthz`
   - Tailscale: `tailscale status` shows connected
   - OpenClaw: `openclaw agent --status` or equivalent
2. Run VALI validation task via orchestrator:
   - Create task: `VALIDATE` → `saos-deployment-{id}`
   - VALI executes validation script, returns pass/fail
3. If all pass: update `saos_deployments` (status: `verified`)
4. If any fail: update status → `needs_attention`, log errors, trigger retry or escalate

**Deliverable:** `health_check.py` + VALI integration.

### Phase 6: Client Delivery
**Goal:** Client receives email with everything they need.

1. Generate email from template:
   - Tailscale URL (e.g., `https://{client-name}.tailnet-{id}.ts.net`)
   - OpenClaw web URL (if exposed)
   - n8n URL
   - Setup instructions (PDF or HTML)
   - SSH credentials (or Tailscale SSH)
   - Support contact info
2. Send via email provider (SendGrid SMTP)
3. Update `saos_clients` (status: `active`)
4. Update `saos_deployments` (status: `delivered`)
5. Log to `saos_provisioning_log`

**Deliverable:** Email template + send script.

### Phase 7: Dashboard Integration
**Goal:** Client sees "Your fleet is live" with real agent status.

1. Build or extend `dashboard.html` to show:
   - Agent status (green/yellow/red)
   - Recent task completions
   - System health (disk, Ollama, n8n)
   - Fleet agent list with emojis
2. Dashboard queries:
   - Client n8n executions (via API)
   - Client Postgres `agent_state` table
   - Tailscale device status (via API)
3. Host dashboard:
   - Option A: Static HTML served from client VPS (nginx)
   - Option B: Embedded in Systack admin panel
4. Access control: Tailscale-only or password-protected

**Deliverable:** Updated dashboard.html + data API.

### Phase 8: Cleanup + Monitoring
**Goal:** Pipeline is observable, recoverable, and doesn't leak resources.

1. Add cleanup for failed deployments:
   - Destroy VPS if provisioning fails after N retries
   - Delete partial records
   - Notify Systack admin
2. Add monitoring:
   - Daily check: `saos_deployments` where status != `delivered` and created_at > 24h
   - Alert via Slack/email
3. Add cost tracking:
   - Log VPS creation time → compute cost
   - Monthly report: active clients × VPS cost

---

## 3. n8n Workflow Node-by-Node Spec

### Workflow: `SAOS Provisioning Pipeline`
**ID:** `saos-provision`  
**Trigger:** Stripe webhook `checkout.session.completed`  
**Output:** Client deployed, notified, dashboard live

#### Node 1: Webhook Trigger
```
Type: n8n-nodes-base.webhook
Method: POST
Path: saos-provision
Response Mode: responseNode
Authentication: Stripe signature verification
```
**Input:** Stripe event JSON payload  
**Output:** Raw Stripe event

#### Node 2: Validate Stripe Signature
```
Type: n8n-nodes-base.code
Language: JavaScript
```
**Logic:**
- Read `Stripe-Signature` header
- Verify using Stripe webhook signing secret + timestamp tolerance (5 min)
- If invalid → return error, stop workflow
- If valid → extract event type

**Output:** `{ valid: true, event_type: "checkout.session.completed", payload: {...} }`

#### Node 3: Filter by Event Type
```
Type: n8n-nodes-base.if
Condition: event_type === "checkout.session.completed"
```
**True branch → Node 4**  
**False branch → Node 3b (log and exit)**

#### Node 3b: Log Non-Provisioning Event
```
Type: n8n-nodes-base.postgres (or code node to log)
Action: INSERT INTO saos_provisioning_log (step_name, status, output)
```

#### Node 4: Extract Customer Data
```
Type: n8n-nodes-base.code
```
**Extracts:**
- `customer.id` → `stripe_customer_id`
- `customer.email` → `client_email`
- `customer.name` → `client_name`
- `subscription.id` → `stripe_subscription_id`
- `subscription.items[0].price.id` → `stripe_price_id`
- `subscription.items[0].price.product` → `stripe_product_id`

**Lookup:** Map `stripe_product_id` → tier via local mapping table (or hardcoded for now)

**Output:** `{ customer_id, email, name, subscription_id, price_id, tier }`

#### Node 5: Check for Duplicate
```
Type: n8n-nodes-base.postgres
Query: SELECT id FROM saos_clients WHERE stripe_customer_id = $1
```
**If exists → Node 5b (update existing, skip provisioning)**  
**If new → Node 6**

#### Node 5b: Update Existing Subscription
```
Type: n8n-nodes-base.postgres
Query: UPDATE saos_clients SET stripe_subscription_id = $1, tier = $2, status = 'active' WHERE id = $3
```

#### Node 6: Create Client Record
```
Type: n8n-nodes-base.postgres
Query: INSERT INTO saos_clients (stripe_customer_id, stripe_subscription_id, email, name, tier, status, created_at) VALUES (...) RETURNING id
```
**Output:** `client_id`

#### Node 7: Create Deployment Record
```
Type: n8n-nodes-base.postgres
Query: INSERT INTO saos_deployments (client_id, status, created_at) VALUES ($client_id, 'pending', NOW()) RETURNING id
```
**Output:** `deployment_id`

#### Node 8: Call Provisioning API
```
Type: n8n-nodes-base.httpRequest
Method: POST
URL: http://localhost:8000/api/provision  (or internal API endpoint)
Body: { client_id, deployment_id, tier, email, name }
Timeout: 300 seconds
```
**Note:** This calls a Python Flask/FastAPI service that handles the actual VPS provisioning (Phase 2). n8n should not do SSH directly.

#### Node 9: Wait for Provisioning
```
Type: n8n-nodes-base.wait
Time: 300 seconds (5 min)
```
**Alternative:** Use polling loop (HTTP Request → Check Status) with max 10 retries

#### Node 10: Check Provisioning Status
```
Type: n8n-nodes-base.httpRequest
Method: GET
URL: http://localhost:8000/api/provision/{deployment_id}/status
```

#### Node 11: Branch on Status
```
Type: n8n-nodes-base.if
Condition: status === "verified"
```
**True → Node 12 (send email)**  
**False → Node 11b (log error, alert admin)**

#### Node 11b: Log Failure + Alert
```
Type: n8n-nodes-base.code
Actions:
- Log to saos_provisioning_log
- Send Slack message to #systack-alerts
- Update saos_deployments status = 'failed'
```

#### Node 12: Generate Client Email
```
Type: n8n-nodes-base.code
```
**Builds email body from template with variables:**
- `client_name`, `tailscale_url`, `n8n_url`, `agent_name`
- Setup instructions (markdown → HTML)

#### Node 13: Send Email
```
Type: n8n-nodes-base.emailSend (or HTTP to SendGrid API)
To: {{ client_email }}
Subject: "Your SAOS Fleet is Live — Welcome Aboard"
Body: {{ email_html }}
```

#### Node 14: Update Records
```
Type: n8n-nodes-base.postgres
Queries:
- UPDATE saos_clients SET status = 'active' WHERE id = $client_id
- UPDATE saos_deployments SET status = 'delivered', delivered_at = NOW() WHERE id = $deployment_id
```

#### Node 15: Respond to Stripe
```
Type: n8n-nodes-base.respondToWebhook
Status: 200
Body: { "received": true, "client_id": {{ client_id }} }
```

### Workflow Diagram (Text)

```
[Webhook] → [Validate Signature] → [Filter Event] → [Extract Data]
                                              ↓
                                    [Check Duplicate] → [Update Existing]
                                              ↓ (new)
                                    [Create Client] → [Create Deployment]
                                              ↓
                                    [Call Provision API] → [Wait]
                                              ↓
                                    [Check Status] → [Verified?]
                                              ↓ Yes
                                    [Generate Email] → [Send Email]
                                              ↓
                                    [Update Records] → [Respond 200]
```

---

## 4. VPS Provisioning Approach

### Decision: Python Script + Vultr API

**Rejected options:**
- **Terraform:** Adds complexity, state management overhead. Rejected for Phase 1.
- **Manual provisioning:** Not scalable. Rejected.
- **Ansible:** Good for config management, but adds dependency. Consider for Phase 2.

**Chosen approach:** Python script using `requests` to call Vultr API directly.

### Vultr API Requirements

**API Key:** Must exist in environment or credential store.  
**Permissions needed:** `compute:write`, `compute:read`, `startup:read`

### Provisioning Script Structure

**File:** `scripts/provision_vps.py`

```python
#!/usr/bin/env python3
"""Provision a Vultr VPS for SAOS client."""

import os, json, time, requests
import paramiko  # for SSH
from datetime import datetime

VULTR_API_KEY = os.environ["VULTR_API_KEY"]
TAILSCALE_AUTH_KEY = os.environ["TAILSCALE_AUTH_KEY"]
BASE_HEADERS = {"Authorization": f"Bearer {VULTR_API_KEY}", "Content-Type": "application/json"}

TIER_PLANS = {
    "business":    {"plan": "vhp-4c-16gb", "region": "ord", "os_id": 1743},  # Ubuntu 22.04
    "enterprise":  {"plan": "vhp-4c-16gb", "region": "ord", "os_id": 1743},
}

def create_instance(client_id: str, tier: str) -> dict:
    """Create Vultr instance."""
    config = TIER_PLANS[tier]
    payload = {
        "region": config["region"],
        "plan": config["plan"],
        "os_id": config["os_id"],
        "label": f"saos-{client_id}",
        "hostname": f"saos-{client_id}",
        "user_data": generate_cloud_init(tier),
        "enable_ipv6": False,
        "backups": "enabled"
    }
    r = requests.post("https://api.vultr.com/v2/instances", headers=BASE_HEADERS, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["instance"]

def generate_cloud_init(tier: str) -> str:
    """Return cloud-init script for base setup."""
    return """#!/bin/bash
# Base setup
apt-get update && apt-get install -y curl wget git docker.io docker-compose
usermod -aG docker root

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --authkey {TAILSCALE_AUTH_KEY} --hostname saos-{client_id}

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:14b

# Install OpenClaw
# TODO: add official installer or Docker run
# curl -fsSL ... | bash

# Install n8n via Docker
docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n:latest

# Configure firewall
ufw allow 22/tcp
ufw allow 5678/tcp
ufw allow 11434/tcp
ufw --force enable

# Signal completion
curl -X POST http://provisioning.systack.net/api/vps-ready \
  -d "{client_id}" -H "Content-Type: application/json"
""".format(TAILSCALE_AUTH_KEY=TAILSCALE_AUTH_KEY, client_id="{client_id}")

def wait_for_instance(instance_id: str, timeout=600) -> dict:
    """Poll until instance is running."""
    start = time.time()
    while time.time() - start < timeout:
        r = requests.get(f"https://api.vultr.com/v2/instances/{instance_id}", headers=BASE_HEADERS, timeout=30)
        r.raise_for_status()
        instance = r.json()["instance"]
        if instance["status"] == "active":
            return instance
        time.sleep(10)
    raise TimeoutError(f"Instance {instance_id} did not become active within {timeout}s")

def run_provision(client_id: str, tier: str) -> dict:
    """Full provision: create VPS, wait, capture details."""
    instance = create_instance(client_id, tier)
    instance = wait_for_instance(instance["id"])
    
    # Wait a bit for cloud-init
    time.sleep(60)
    
    # Get Tailscale IP (via Tailscale API or SSH)
    # tailscale_ip = get_tailscale_ip(instance["main_ip"])
    
    return {
        "vps_id": instance["id"],
        "vps_ip": instance["main_ip"],
        "tailscale_ip": None,  # filled later
        "tailscale_url": None,  # filled later
        "status": "vps_ready"
    }
```

### Cloud-Init vs SSH Approach

**Chosen:** Cloud-init for base packages + SSH for fine-grained setup.

| Approach | Pros | Cons |
|----------|------|------|
| Cloud-init only | No SSH dependency, runs on boot | Limited debugging, no feedback |
| SSH only | Full control, can retry steps | Requires VPS to be booted + SSH accessible |
| Hybrid (chosen) | Cloud-init does heavy lifting, SSH does config | Requires both mechanisms |

### Tailscale Integration

1. VPS boots → cloud-init installs Tailscale → `tailscale up --authkey ...`
2. VPS appears in Systack tailnet
3. Tailscale assigns hostname: `saos-{client_id}`
4. MagicDNS creates: `saos-{client_id}.tailnet-{id}.ts.net`
5. Client accesses: `http://saos-{client_id}.tailnet-{id}.ts.net:5678` for n8n

---

## 5. Identity File Generation

### Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{{agent_name}}` | Client preference or generated (e.g., Percy, Alex) | "Percy" |
| `{{client_name}}` | Stripe customer name | "Jacqueline" |
| `{{business_name}}` | Stripe metadata or onboarding form | "McDonald's" |
| `{{industry}}` | Onboarding form or Stripe metadata | "food" |
| `{{tier}}` | Product SKU mapping | "business" |
| `{{tailscale_url}}` | Generated after Tailscale join | `https://percy.tailnet-abc.ts.net` |
| `{{vps_ip}}` | Vultr instance IP | `123.45.67.89` |
| `{{model}}` | Tier→model mapping from spec | `qwen2.5:14b` |
| `{{owner_name}}` | Client's name from Stripe | "Jacqueline" |
| `{{owner_email}}` | Client's email from Stripe | "jacqueline@example.com" |
| `{{created_date}}` | Provisioning timestamp | "2026-06-17" |
| `{{fleet_commander}}` | Always "SOL" | "SOL" |
| `{{support_email}}` | Static | "support@systack.net" |
| `{{support_phone}}` | Static | "(501) 274-6231" |

### Rendering Engine

**File:** `scripts/render_identity.py`

**Tech:** Python `Jinja2` templating

**Input:**
- Template directory: `templates/identity/` (to be created)
- Client data: dict from `saos_clients` record

**Output:**
- Workspace directory: `~/.openclaw/workspaces/{agent_name}/`
- Files: `SOUL.md`, `AGENTS.md`, `USER.md`, `MEMORY.md`, `IDENTITY.md`, `TOOLS.md`

**Base Templates (to create):**

1. `templates/identity/SOUL.md.j2` — Based on Percy's SOUL.md, with customizable sections
2. `templates/identity/AGENTS.md.j2` — Based on Percy's AGENTS.md, with tier-appropriate rules
3. `templates/identity/USER.md.j2` — Based on Percy's USER.md, with client-specific context
4. `templates/identity/MEMORY.md.j2` — Empty with structure for daily memory
5. `templates/identity/IDENTITY.md.j2` — Agent identity (name, emoji, avatar)
6. `templates/identity/TOOLS.md.j2` — Tool permissions based on tier

**Rendering example:**

```python
from jinja2 import Environment, FileSystemLoader
import os

env = Environment(loader=FileSystemLoader("templates/identity"))

def render_identity(client_data: dict) -> str:
    workspace = f"~/.openclaw/workspaces/{client_data['agent_name']}"
    os.makedirs(workspace, exist_ok=True)
    
    for template_name in ["SOUL.md.j2", "AGENTS.md.j2", "USER.md.j2", "MEMORY.md.j2", "IDENTITY.md.j2", "TOOLS.md.j2"]:
        template = env.get_template(template_name)
        output = template.render(**client_data)
        with open(f"{workspace}/{template_name[:-3]}", "w") as f:
            f.write(output)
    
    return workspace
```

### Agent Naming Convention

| Client Input | Generated Agent Name | Example |
|--------------|---------------------|---------|
| Client provides name | Use client's choice | "Percy" |
| No preference | Generate from business name | "McD-Assistant" → "Mickey" (not ideal, needs rules) |
| Default | "SAOS-{random}" | "SAOS-Alpha7" |

**Recommendation:** Ask client for agent name preference on onboarding form. Default to "{FirstName}-Assistant" if not provided.

---

## 6. Dashboard Requirements

### Client Dashboard: "Your Fleet is Live"

**Purpose:** Single pane of glass for client to see their agent fleet status.

**Data to Show:**

| Section | Data Source | Refresh |
|---------|-------------|---------|
| **Fleet Status** | `agent_state` table in client Postgres | Real-time (SSE or 30s poll) |
| **Agent Cards** | Agent names, emojis, current status, last heartbeat | 30s |
| **Recent Activity** | `task_queue` + `execution_log` | 30s |
| **System Health** | n8n health, Ollama health, disk space | 60s |
| **Quick Actions** | Restart n8n, pull model, view logs | On click |
| **Support** | Link to Systack support, phone, email | Static |

### Dashboard Hosting Options

| Option | Pros | Cons |
|--------|------|------|
| **A: Client VPS** (Flask app on port 8080) | Zero Systack hosting cost, client-only access | Client must remember URL |
| **B: Systack admin panel** (Netlify/Vercel) | Centralized, easy to manage | Requires CORS/API to client VPS |
| **C: Tailscale-only** (no public URL) | Maximum security | Requires Tailscale on viewer's device |

**Recommendation:** Start with Option A (client VPS, Tailscale-only). Add Option B later for Systack admin convenience.

### Dashboard API Endpoints (on client VPS)

```
GET /api/agents      → [{name, status, emoji, last_heartbeat}]
GET /api/tasks       → [{id, type, status, assigned_agent, created_at}]
GET /api/health      → {ollama, n8n, disk, postgres}
GET /api/activity    → [{type, title, detail, timestamp}]  (merged n8n + task data)
POST /api/restart    → {service: "n8n"|"ollama"|"openclaw"}
```

### Dashboard HTML Structure

Reuse `templates/private/dashboard.html` as base:
- Dark theme (matches SAOS branding)
- Grid layout: status cards on top, activity feed below
- Agent cards with emojis (SOL ☀️, VALI ✅, etc.)
- System health indicators with color coding

---

## 7. Error Handling Matrix

| Step | Failure Mode | Detection | Recovery | Escalation |
|------|-------------|-----------|----------|------------|
| **1. Stripe webhook** | Invalid signature | Signature verification fails | Return 400, log attempt | Alert admin if >5 invalid in 1h |
| **1. Stripe webhook** | Duplicate event | Duplicate `id` in `saos_clients` | Skip processing, return 200 | None (idempotent) |
| **2. Create client record** | DB connection lost | Postgres exception | Retry 3× with backoff, then queue for later | Alert admin after 3 failures |
| **3. VPS creation** | Vultr API error (e.g., region capacity) | HTTP 4xx/5xx from Vultr | Retry with different region, or queue | Alert admin, offer refund |
| **3. VPS creation** | Timeout (VPS never reaches `active`) | Poll timeout (10 min) | Destroy partial instance, retry once | Alert admin |
| **4. Cloud-init** | Script fails (package not found) | No "vps-ready" signal | SSH in, run manual fix script | Alert admin |
| **5. Tailscale join** | Auth key invalid | `tailscale up` fails | Generate new auth key, retry | Alert admin |
| **6. Ollama install** | Model download fails | `ollama pull` error | Retry download, or use smaller model fallback | Alert admin |
| **7. n8n install** | Docker pull fails | Container not running | Retry docker pull, check disk space | Alert admin |
| **8. Template import** | n8n API error | HTTP 4xx/5xx from n8n | Log error, mark templates as pending manual fix | Alert admin |
| **9. Identity render** | Template missing variable | Jinja2 exception | Use default values, log warning | None (non-blocking) |
| **10. Health check** | Any service down | Health endpoint non-200 | Retry service restart, log | Alert admin if still down after 3 restarts |
| **11. Email send** | SMTP failure | SendGrid/ SMTP error | Retry 3×, then queue for manual send | Alert admin |
| **12. Dashboard** | API timeout | Request >5s | Show cached data with "stale" indicator | None |

### Retry Policy

- **Exponential backoff:** 2^retry × 30 seconds, max 5 minutes
- **Max retries per step:** 3 (except Stripe webhook = 0, must be idempotent)
- **Global timeout:** 30 minutes from webhook receipt to delivery
- **Cleanup on failure:** After max retries, destroy VPS if created, delete partial records, notify admin

---

## 8. Testing Plan

### How to Verify End-to-End Without Spending Real Money

#### Test Mode Architecture

Add a `test_mode` flag to the provisioning pipeline:

```python
TEST_MODE = os.environ.get("SAOS_TEST_MODE", "false").lower() == "true"

if TEST_MODE:
    # Skip real VPS creation
    vps_id = f"TEST-{uuid4()}"
    vps_ip = "192.0.2.1"  # TEST-NET-1 (RFC 5737)
    # Skip real Tailscale join
    tailscale_ip = "100.64.0.1"
    # Skip real email send — log to console/file instead
```

#### Test Stripe Events

Use Stripe CLI to trigger test webhooks:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login (test mode)
stripe login

# Trigger checkout completion
stripe trigger checkout.session.completed \
  --override checkout_session:customer_email="test@example.com" \
  --override checkout_session:amount_subtotal=29900
```

#### Test Scenarios

| # | Scenario | Expected Result | How to Trigger |
|---|----------|-----------------|----------------|
| 1 | Successful Business Fleet provisioning | Client record created, VPS simulated, email logged, status = `delivered` | Stripe CLI trigger with test mode |
| 2 | Duplicate Stripe customer | Updates existing, no new VPS | Trigger same customer twice |
| 3 | Invalid Stripe signature | Returns 400, no processing | Send fake webhook without signature |
| 4 | VPS creation failure | Retries 3×, then marks failed, alerts admin | Break Vultr API key |
| 5 | Health check failure | Retries service restart, marks needs_attention | Stop Ollama container mid-provision |
| 6 | Email send failure | Retries 3×, queues for manual | Break SMTP credentials |

#### Local Testing Script

```python
# test_provisioning.py
import os, json, requests
os.environ["SAOS_TEST_MODE"] = "true"

from provision_vps import run_provision
from render_identity import render_identity

# Mock client data
client = {
    "client_id": "test-001",
    "tier": "business",
    "email": "test@example.com",
    "name": "Test Client",
    "agent_name": "Testy"
}

# Run provision
result = run_provision(**client)
assert result["status"] == "vps_ready"
assert result["vps_id"].startswith("TEST-")

# Render identity
workspace = render_identity(client)
assert os.path.exists(f"{workspace}/SOUL.md")

print("✅ All tests passed")
```

#### Integration Testing

1. **Stripe → n8n:** Trigger Stripe CLI event → verify n8n webhook receives it
2. **n8n → Postgres:** Verify `saos_clients` record created
3. **n8n → Provision API:** Verify provision script called with correct args
4. **Provision → Health Check:** Verify all services report healthy (mocked)
5. **Health Check → Email:** Verify email logged (not sent in test mode)

#### Regression Testing

After each deployment:
- Run full test suite (10-15 min)
- Verify no existing clients affected
- Check Stripe webhook still responds to real events

---

## 9. Time Estimates

### Per Phase (Assembly + CODY)

| Phase | Tasks | Estimated Hours | Owner |
|-------|-------|-----------------|-------|
| **Phase 0: Foundation** | Verify/create API keys, create DB schema, test mode setup | 4h | ASSEMBLY |
| **Phase 1: Stripe Webhook** | Build n8n workflow (15 nodes), signature verification, client record creation | 6h | ASSEMBLY + CODY (n8n nodes) |
| **Phase 2: VPS Provisioning** | Build `provision_vps.py`, cloud-init script, Vultr API integration | 8h | CODY |
| **Phase 3: Template Deployment** | Build `deploy_templates.py`, n8n REST API integration | 4h | ASSEMBLY |
| **Phase 4: Identity Generation** | Create Jinja2 templates, build `render_identity.py` | 6h | ASSEMBLY |
| **Phase 5: Health Checks** | Build `health_check.py`, VALI integration | 4h | CODY |
| **Phase 6: Client Delivery** | Email template, send script, update records | 3h | ASSEMBLY |
| **Phase 7: Dashboard** | Extend dashboard.html, build API endpoints | 6h | CODY |
| **Phase 8: Cleanup + Monitoring** | Failure cleanup, daily monitoring, cost tracking | 4h | ASSEMBLY |
| **Testing + Integration** | End-to-end test, Stripe CLI tests, regression tests | 6h | ASSEMBLY + CODY |
| **Documentation** | README, runbook, troubleshooting guide | 3h | ASSEMBLY |
| **Buffer** | Unexpected issues, debugging | 8h | — |
| **TOTAL** | | **62 hours** | |

### Calendar Estimate

- **Assembly + CODY working in parallel:** ~40 hours of actual work
- **With other fleet duties:** ~2 weeks calendar time
- **Milestone 1 (Phases 0-2):** End of Week 1 — Stripe webhook → VPS creation working
- **Milestone 2 (Phases 3-6):** End of Week 2 — Full provisioning pipeline working
- **Milestone 3 (Phases 7-8):** End of Week 3 — Dashboard + monitoring live

---

## Appendix A: Files to Create

| File | Path | Phase |
|------|------|-------|
| `SAOS-PROVISIONING-BUILD-PLAN.md` | `~/.openclaw/workspaces/assembly/` | This file |
| `provision_vps.py` | `~/.openclaw/workspaces/sol/scripts/` | Phase 2 |
| `deploy_templates.py` | `~/.openclaw/workspaces/sol/scripts/` | Phase 3 |
| `render_identity.py` | `~/.openclaw/workspaces/sol/scripts/` | Phase 4 |
| `health_check.py` | `~/.openclaw/workspaces/sol/scripts/` | Phase 5 |
| `send_client_email.py` | `~/.openclaw/workspaces/sol/scripts/` | Phase 6 |
| `templates/identity/*.j2` | `~/.openclaw/workspaces/sol/templates/identity/` | Phase 4 |
| `n8n-saos-provision.json` | `~/.openclaw/workspaces/sol/n8n-workflows/` | Phase 1 |
| `test_provisioning.py` | `~/.openclaw/workspaces/sol/tests/` | Testing |
| `README-PROVISIONING.md` | `~/.openclaw/workspaces/sol/` | Documentation |

## Appendix B: Database Schema (Proposed)

```sql
-- saos_clients
CREATE TABLE saos_clients (
    id SERIAL PRIMARY KEY,
    stripe_customer_id TEXT UNIQUE NOT NULL,
    stripe_subscription_id TEXT,
    email TEXT NOT NULL,
    name TEXT,
    business_name TEXT,
    industry TEXT,
    tier TEXT CHECK (tier IN ('business', 'enterprise')),
    status TEXT DEFAULT 'provisioning' CHECK (status IN ('provisioning', 'active', 'suspended', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- saos_deployments
CREATE TABLE saos_deployments (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES saos_clients(id),
    vps_id TEXT,
    vps_ip TEXT,
    tailscale_ip TEXT,
    tailscale_url TEXT,
    ssh_key TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'vps_ready', 'templates_deployed', 'identity_ready', 'verified', 'delivered', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP,
    delivered_at TIMESTAMP,
    error_message TEXT
);

-- saos_provisioning_log
CREATE TABLE saos_provisioning_log (
    id SERIAL PRIMARY KEY,
    deployment_id INTEGER REFERENCES saos_deployments(id),
    step_name TEXT NOT NULL,
    status TEXT,
    output TEXT,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

**Plan Author:** ASSEMBLY  
**Reviewers:** SOL (commander), VALI (validator)  
**Next Step:** SOL approves plan → CODY + ASSEMBLY begin Phase 0
