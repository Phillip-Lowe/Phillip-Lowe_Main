# Systack Credentials Registry

**Last Updated:** 2026-06-08
**Owner:** Phillip Lowe (Systack)
**Classification:** INTERNAL - Authorized personnel only
**Location:** `credentials/SYSTACK-CREDENTIALS-REGISTRY.md`

---

## ⚠️ CRITICAL REMINDER

**Never say "I don't have the credentials" without checking:**
1. This registry
2. `TOOLS.md` in workspace root
3. `MEMORY.md` in workspace root
4. macOS Keychain (`security find-generic-password`)
5. Credential files in `credentials/` directory
6. Environment variables

---

## n8n - Workflow Automation

| Field | Value | Notes |
|-------|-------|-------|
| **URL** | https://n8n.systack.net | Production instance |
| **Local URL** | http://localhost:5678 | Dev/testing |
| **Login Email** | plowe95@yahoo.com | |
| **Login Password** | `123GreeN23!` | Same for local and cloud |
| **Role** | global:owner | Full admin access |
| **User ID** | 06cb7b8f-698b-41c6-9a94-b3f350433cfa | |
| **Database** | ~/.n8n/database.sqlite | Local SQLite |
| **Tunnel** | Cloudflare (e2897c60-f66d-4f5b-9d93-4c85897ca85f) | |

### API Access

| Field | Value | Notes |
|-------|-------|-------|
| **API Key File** | `~/.openclaw/workspaces/sol/.n8n_api_key` | JWT token |
| **MCP Token File** | `~/.openclaw/workspaces/sol/.n8n_mcp_token` | For MCP Server API |
| **MCP URL** | https://n8n.systack.net/mcp-server/http | |
| **Auth Method** | Cookie-based session (REST API) | Use curl with -c/-b |

### n8n Credential IDs (from database)

| Service | Credential ID | Label |
|---------|--------------|-------|
| IMAP | `uZXvyt7Wd0RbQreY` | SUPPORT Systack IMAP |
| SMTP | `jL1iF7fhyhTe5tCp` | PLOWE Systack SMTP |
| Postgres | `iVuy7e5WTC05Hqwe` | Postgres account |
| Google Sheets | `REPLACE_WITH_CREDENTIAL_ID` | Not yet configured |

---

## Email Accounts

### Gmail - Utopia Deli (Primary SMTP)

| Field | Value | Notes |
|-------|-------|-------|
| **Email** | theutopiadelilittlerock@gmail.com | |
| **App Password** | `sacn gdyi nrqw otnx` | ⚠️ REVOKED by Google 2026-06-08 |
| **Keychain Service** | utopia-deli-smtp-app-password | |
| **Status** | ❌ INACTIVE - needs new app password | |

### Gmail - SOL Liaison (Secondary)

| Field | Value | Notes |
|-------|-------|-------|
| **Email** | sol.liaison@gmail.com | |
| **App Password** | `yxvstahusqlahbzv` | Active |
| **Keychain Service** | sol-email-smtp-app-password | |

### Systack Support Email

| Field | Value | Notes |
|-------|-------|-------|
| **Email** | support@systack.net | |
| **App Password** | `ordn fmio oewz asxl` | Active |
| **Keychain Service** | systack_email | |

### Systack Business Email

| Field | Value | Notes |
|-------|-------|-------|
| **Email** | sol.liaison@systack.net | |
| **App Password** | *(in keychain: sol.liaison@systack.net)* | |
| **Keychain Service** | systack_email | |

---

## LinkedIn - Systack Business

| Field | Value | Notes |
|-------|-------|-------|
| **Email** | plowe@systack.net | |
| **Password** | `d5jYa7CYqeDR0HH` | |
| **Passkey** | Apple credential validation | Use when prompted |
| **Purpose** | Systack business presence | |
| **Saved** | 2026-06-04 | |

---

## Microsoft 365 Copilot

| Field | Value | Notes |
|-------|-------|-------|
| **Account** | 81777@office365proplus.co | Company-owned |
| **Password** | `degtyg-6dixcy-pextyD` | Keychain: m365-copilot-81777 |
| **Browser** | Brave (OpenClaw-managed profile) | |
| **URL** | https://m365.cloud.microsoft/chat/ | |
| **Status** | Active consultation tool | |
| **Authorization** | User-approved 2026-06-04 | |

---

## Payment Processing

### Stripe (Systack SAOS)

| Field | Value | Notes |
|-------|-------|-------|
| **Publishable Key** | `pk_test_51Tcke70VH0hFryTQQZBAwVN6EQb2MRSeKtEMot5FXdHLNYdzWfNyNAio8XgyhStkhdL3aBGyQSxeCNK08D1Hp1qS0069Jl06Xv` | Test mode |
| **Secret Key** | `sk_test_51Tcke70VH0hFryTQXhDYJFwZqfBoaDqIVYqAeHdoG5kO7F74ekgXIf5o9OogM0zgkcYQHsqrje3tc2XeVNziOY9k00HClaCJit` | Test mode |
| **Keychain** | stripe-systack-saos-pk / stripe-systack-saos-sk | |

### Square (Utopia Deli)

| Field | Value | Notes |
|-------|-------|-------|
| **Access Token** | *(check n8n credentials or .env files)* | |
| **Location ID** | *(check n8n credentials)* | |
| **Environment** | Production | |

---

## Databases

### PostgreSQL (Local)

| Field | Value | Notes |
|-------|-------|-------|
| **Host** | localhost | |
| **Port** | 5432 | |
| **Superuser** | philliplowe | |
| **App User** | systack | |
| **App Password** | `Systack2026!CRM` | |
| **Database: crm** | For invoice parser | |
| **Database: utopia_deli** | For order system | |

### SQLite

| File | Purpose |
|------|---------|
| `~/.openclaw/workspaces/sol/utopia-deli-catering.db` | Catering leads |
| `~/.openclaw/workspaces/sol/invoice_data.db` | Invoice parser |
| `~/.n8n/database.sqlite` | n8n workflows |

---

## Cloud Services

### Cloudflare

| Field | Value | Notes |
|-------|-------|-------|
| **Tunnel ID** | `e2897c60-f66d-4f5b-9d93-4c85897ca85f` | For n8n |
| **Invoice API** | invoices.systack.net | Via tunnel |

### GitHub

| Field | Value | Notes |
|-------|-------|-------|
| **Utopia Deli Repo** | Phillip-Lowe/utopia-deli-order | |
| **Systack Site Repo** | Phillip-Lowe/systack-site | |
| **Auth** | SSH keys or token | Check git config |

---

## AI/ML Services

| Service | Status | Notes |
|---------|--------|-------|
| **Kling AI** | Lifetime subscription | Apple account required |
| **Runway ML** | Team: loudgreen1 | 855 credits remaining |
| **ElevenLabs** | API key configured | `ELEVENLABS_API_KEY` env |
| **OpenAI** | *(check .env)* | If configured |

---

## How to Retrieve Credentials

### From macOS Keychain
```bash
# List all Systack-related entries
security dump-keychain | grep -i "systack\|utopia\|n8n\|postgres"

# Get specific password
security find-generic-password -s "SERVICE_NAME" -w
```

### From Files
```bash
# n8n API key
cat ~/.openclaw/workspaces/sol/.n8n_api_key

# n8n MCP token
cat ~/.openclaw/workspaces/sol/.n8n_mcp_token

# n8n auth (full details)
cat ~/.openclaw/workspaces/sol/.n8n-auth
```

---

## Credential Locations Summary

| Storage | What Lives There |
|---------|-----------------|
| macOS Keychain | Email passwords, app passwords, API keys |
| `~/.openclaw/workspaces/sol/.n8n_api_key` | n8n REST API JWT |
| `~/.openclaw/workspaces/sol/.n8n_mcp_token` | n8n MCP Server JWT |
| `~/.openclaw/workspaces/sol/.n8n-auth` | Full n8n access documentation |
| `~/.openclaw/workspaces/sol/credentials/` | Organized credential files by project |
| `~/.n8n/database.sqlite` | n8n internal credentials (encrypted) |
| Environment variables | `ELEVENLABS_API_KEY`, etc. |

---

## Security Notes

- All credential files have `600` permissions (user read-only)
- Never commit credentials to git
- Rotate passwords quarterly
- Use app passwords (not account passwords) for SMTP/IMAP
- Keychain is the authoritative source for app passwords


---

## Twilio — Utopia Deli Messaging

**Signed up:** 2026-06-20
**Console:** https://1console.twilio.com/account/ACcadbd2a9b84a2cdab37480fdcded0b2b
**Status:** Active — awaiting phone number purchase

### Credentials
| Field | Location |
|-------|----------|
| Account SID | `credentials/Green/Twilio/Twilio credentials` |
| Auth Token | `credentials/Green/Twilio/Twilio credentials` |
| API Key SID | `credentials/Green/Twilio/Twilio credentials` |
| API Secret | `credentials/Green/Twilio/Twilio credentials` |
| Recovery Code | `credentials/Green/Twilio/Twilio Recovery code` |

### n8n Credential
| Field | Value | Notes |
|-------|-------|-------|
| Credential ID | `TWILIO_CREDENTIAL_ID` | Create in n8n UI after import |
| Type | `twilioApi` | Standard n8n Twilio node |

### n8n Workflows — Utopia Deli Messaging

| Workflow | ID | Status | Type |
|----------|-----|--------|------|
| Weekly Messaging | `51FhflWlsULl16K8` | Ready to activate | Scheduled triggers |
| Twilio STOP Handler | `JWqTMIeAn6w44y3U` | Ready to activate | Webhook (POST) |
| Email Unsubscribe | `pIRGULTOkbMQbVDH` | Ready to activate | Webhook (GET) |

### Webhook URLs
| Endpoint | URL |
|----------|-----|
| Twilio SMS inbound | `https://n8n.systack.net/webhook/twilio-sms-inbound` |
| Email unsubscribe | `https://n8n.systack.net/webhook/unsubscribe?email=USER@EXAMPLE.COM` |

### Twilio Console Configuration
- **Account SID**: `ACcadbd2a9b...`
- **Phone number**: `+18887614092` (toll-free)
- **SMS webhook**: `https://n8n.systack.net/webhook/twilio-sms-inbound`
- **Credential ID in n8n**: `Vv7vlxlkKbYCuWqr` (API Key format)

### Opt-Out Logic
- **STOP** → `unsubscribed_sms = true` (email unaffected)
- **START** → `unsubscribed_sms = false`
- **Email unsubscribe link** → `unsubscribed_email = true` (SMS unaffected)
- Channels are **independent** — opt out of one, the other continues

### Usage
- SMS campaigns for Utopia Deli
- Weekly: Monday menu push, Wednesday cutoff reminder, Friday specials
- Requires A2P 10DLC registration before bulk sends (>200/day)
- All templates include: STOP instructions + email unsubscribe link + physical address

---

**Last Updated:** 2026-06-20 04:37 CDT

