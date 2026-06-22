# Systack Automation Templates — Complete Pack

**Date:** 2026-06-05
**For:** Phillip Lowe
**Status:** Ready for Copilot-assisted building

---

## How to Use This Pack

1. Read each template description
2. Click the n8n URL to view the original
3. Open Copilot (M365) and describe what you want to build
4. Reference the template patterns in this file
5. Copy JSON from `~/systack-n8n-workflows/workflows/` directory

---

## TEMPLATE 1: Deli Order System (Your Custom Build)

**Files:**
- `~/systack-n8n-workflows/workflows/systack/Utopia_Deli_HTML_Order_v2__CART_STATE_Aligned.json` (broken but fixed in notes)
- `~/systack-n8n-workflows/workflows/systack/Order_Received.json` (WKFL 4)
- `~/systack-n8n-workflows/workflows/systack/Contact__Item__Cart.json`
- `~/systack-n8n-workflows/workflows/systack/Cart_Renderer__Router.json`

**Key Patterns:**
```
Webhook → Validate JSON → If/Else → Code Nodes → Google Sheets → HTTP Request → Email
```

**Critical nodes you need:**
- **Webhook Trigger** — POST endpoint for frontend
- **Code Node** — Transform HTML payload to CART_STATE format
- **Google Sheets** — Append to CART_STATE, Update status to LOCKED
- **HTTP Request** — Create Square payment link
- **Code Node** — Build cart HTML for email
- **Email Send** — SMTP with branded HTML template
- **Respond to Webhook** — Return {order_id, payment_url}

**Square API endpoint:** `POST https://connect.squareup.com/v2/online-checkout/payment-links`
**Location ID:** `J4B6A3X6RYA63`
**Tax rate:** 9.52% (as separate line item)

---

## TEMPLATE 2: Website Downtime Monitor

**File:** `~/systack-n8n-workflows/workflows/monitoring/website-downtime-monitor.json`
**Original:** https://n8n.io/workflows/11763-website-downtime-monitoring-with-smart-alerts-via-telegram-and-email/

**What it does:**
- Runs every hour (Schedule Trigger)
- Checks 4 websites: systack.net, n8n.systack.net, utopia-deli.com, webhook endpoint
- Logs status to Google Sheets
- Sends email + Slack alert if any service is down

**Key nodes:**
```
Schedule Trigger → Code (service list) → Split In Batches → HTTP Request → If (status=200?) → Code (log) → Google Sheets → If (alert?) → Email + Slack
```

**Services to monitor:**
```javascript
[
  { name: 'n8n.systack.net', url: 'https://n8n.systack.net/healthz' },
  { name: 'systack.net', url: 'https://systack.net' },
  { name: 'utopia-deli.com', url: 'https://www.utopia-deli.com' },
  { name: 'webhook', url: 'https://n8n.systack.net/webhook-test' }
]
```

---

## TEMPLATE 3: Personal Life Manager (AI Agent Blueprint)

**Original:** https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/
**Creator:** Derek Cheung

**What it does:**
- Telegram bot interface
- Voice → OpenAI Whisper → text
- AI agent (OpenRouter) with memory
- Tools: Gmail, Calendar, Tasks, Notes
- Responds via Telegram

**Architecture:**
```
Telegram Trigger → If (voice/text?) → Voice Download → Whisper API → AI Agent → Tool Call → Response → Telegram
```

**Tools the agent has access to:**
- **Get Email** — Gmail API, fetch unread
- **Google Calendar** — Get events for date
- **Google Tasks** — Create/list tasks
- **Current Date** — Time context

**For Systack Personal Agent:**
- Same architecture, add more tools:
  - Browser automation (search, check prices)
  - Local files (Obsidian, notes)
  - n8n integration (run workflows)
  - SMS/Phone (Twilio)

---

## TEMPLATE 4: Lead Generation (Google Maps)

**Original:** https://n8n.io/workflows/2605-generate-leads-with-google-maps/
**Nodes:** Google Sheets + HTTP Request + If + 13 more

**What it does:**
- Scrapes Google Maps for business listings
- Extracts: name, address, phone, website, category
- Saves to Google Sheets
- Can be filtered by location/type

**For Systack:**
- Find restaurants in Little Rock that need ordering systems
- Find businesses still doing manual invoice processing
- Prospecting for Systack services

---

## TEMPLATE 5: Local Business Discovery + Enrichment

**Original:** https://n8n.io/workflows/15411-local-business-lead-discovery-and-enrichment-agent/
**Nodes:** Postgres + Gmail + Sticky Note + 5 more

**What it does:**
- Discovers local businesses
- Enriches with contact data, social profiles
- Stores in Postgres database
- Sends outreach emails via Gmail

**For Systack:**
- Automated CRM pipeline
- Store leads in database
- Auto-send personalized outreach
- Track responses

---

## TEMPLATE 6: Personalized Sales Email Generator

**Original:** https://n8n.io/workflows/5691-generate-personalized-sales-emails-with-linkedin-data-and-claude-37-via-openrouter/
**Nodes:** Google Sheets + HTTP Request + If + Claude + 10 more

**What it does:**
- Scrapes LinkedIn profile
- Generates personalized cold email with Claude
- Tracks in Google Sheets

**For Systack:**
- Cold outreach for Systack services
- LinkedIn account already configured (plowe@systack.net)
- Personalize per prospect

---

## TEMPLATE 7: Score + Route Website Leads

**Original:** https://n8n.io/workflows/16067-score-and-route-website-leads-with-google-sheets-and-gmail/
**Nodes:** Google Sheets + If + Edit Fields + 4 more

**What it does:**
- Receives lead data from web form
- Scores based on criteria (budget, timeline, need)
- Routes high-value to fast track
- Logs everything

**For Systack:**
- Website contact form scoring
- Invoice parser inquiry → fast track
- General inquiry → nurture sequence

---

## TEMPLATE 8: PDF to Markdown (Invoice Parser Enhancement)

**Original:** https://n8n.io/workflows/11811-pdf-to-markdown-converter-with-llamacloud-parser/
**Nodes:** HTTP Request + If + Google Drive + 2 more

**What it does:**
- Sends PDF to LlamaCloud API
- Gets structured markdown back
- Stores in Google Drive

**For Systack Invoice Parser:**
- Alternative to custom Python parser
- Better extraction for complex PDFs
- Image-based invoices

---

## TEMPLATE 9: AI-Powered Gmail Email Labelling

**Original:** https://n8n.io/workflows/2740-basic-automatic-gmail-email-labelling-with-openai-and-gmail-api/
**Nodes:** Wait + Sticky Note + Gmail Trigger + 3 more

**What it does:**
- Watches Gmail inbox
- AI classifies incoming emails
- Auto-labels: Invoice, Support, Sales, Spam

**For Systack:**
- Invoice parser email trigger
- Auto-classify client emails
- Route to right workflow

---

## TEMPLATE 10: RAG Chatbot (Company Documents)

**Original:** https://n8n.io/workflows/2753-rag-chatbot-for-company-documents-using-google-drive-and-gemini/
**Nodes:** Google Drive + Google Drive Trigger + Sticky Note + 9 more

**What it does:**
- Indexes company documents from Google Drive
- User asks questions
- AI retrieves relevant docs, answers question

**For Systack:**
- Client knowledge bases
- Internal documentation search
- Training material Q&A

---

## TEMPLATE 11: Talk to Google Sheets with AI

**Original:** https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/
**Nodes:** Sticky Note + AI Agent + OpenAI + 2 more

**What it does:**
- Natural language questions about spreadsheet data
- "How many orders today?"
- "Which product sold most this week?"

**For Systack:**
- Deli owner asks about sales
- Invoice analytics without SQL
- Simple reporting interface

---

## TEMPLATE 12: Schedule X Posts with Webhooks

**Original:** https://n8n.io/workflows/16066-schedule-x-posts-threads-images-and-polls-with-webhooks/
**Nodes:** HTTP Request + If + Edit Fields + Webhook + 7 more

**What it does:**
- Schedule social media posts
- Thread creation
- Image/poll support
- Webhook API for external triggers

**For Systack:**
- Social media management
- Content calendar automation
- Cross-posting

---

## TEMPLATE 13: Generate SEO Blog Posts

**Original:** https://n8n.io/workflows/16062-generate-and-publish-seo-blog-posts-to-wordpress-with-gemini-and-dall-e-3/
**Nodes:** HTTP Request + Edit Fields + Webhook + 5 more

**What it does:**
- AI generates blog content with Gemini
- Creates images with DALL-E 3
- Publishes to WordPress
- Webhook trigger

**For Systack:**
- Blog automation
- Case study generation
- Content marketing

---

## Quick Reference: Node Types You Need

| Purpose | Node Type | Version |
|---------|-----------|---------|
| Webhook trigger | `n8n-nodes-base.webhook` | 1.1 |
| Schedule/cron | `n8n-nodes-base.scheduleTrigger` | 1.2 |
| HTTP request | `n8n-nodes-base.httpRequest` | 4.2 |
| Code/JavaScript | `n8n-nodes-base.code` | 2 |
| Function (legacy) | `n8n-nodes-base.function` | 1 |
| Google Sheets | `n8n-nodes-base.googleSheets` | 4 |
| Email (SMTP) | `n8n-nodes-base.emailSend` | 2.1 |
| Gmail | `n8n-nodes-base.gmail` | 2 |
| If/Else | `n8n-nodes-base.if` | 2 |
| Merge | `n8n-nodes-base.merge` | 3 |
| Telegram | `n8n-nodes-base.telegram` | 2 |
| Slack | `n8n-nodes-base.slack` | 2.1 |
| Respond to webhook | `n8n-nodes-base.respondToWebhook` | 1 |
| AI Agent | `n8n-nodes-base.agent` | 1 |
| Split in batches | `n8n-nodes-base.splitInBatches` | 3 |

---

## Critical n8n Rules

1. **Every node MUST have `id`** — UUID string
2. **Every node MUST have `position`** — [x, y] with positive values
3. **Every node MUST have `typeVersion`** — use latest stable
4. **Connections use node NAMES** — not IDs in the JSON
5. **ES5 in Code nodes** — no spread `...`, no template literals with nested quotes
6. **Update both tables** — `workflow_entity` AND `workflow_history`
7. **Set activeVersionId** — must match versionId

---

## Files Location

```
~/systack-n8n-workflows/
├── workflows/deli/          # Active workflows
├── workflows/systack/         # Inactive/archived
├── workflows/monitoring/      # Monitoring workflow
├── architecture/              # Personal Agent spec
├── scripts/                 # Backup script
└── all-templates/           # This file
```

**GitHub:** https://github.com/Phillip-Lowe/systack-n8n-workflows

---

## Copilot Prompts You Can Use

**Build deli V2:**
> "Build an n8n workflow that: receives JSON webhook with order data, validates fields, writes to Google Sheets CART_STATE, creates Square payment link via HTTP Request, sends branded HTML email via SMTP, returns order_id and payment_url. Use the Order Received workflow pattern."

**Build monitoring:**
> "Build an n8n workflow that runs every hour, checks 4 website URLs, logs status to Google Sheets, sends email alert if any are down. Use schedule trigger + split in batches + http request + if node."

**Build Personal Agent:**
> "Build an n8n AI agent with Telegram interface, voice input via Whisper, memory, and tools for Gmail/Calendar/Tasks. Use the Personal Life Manager template pattern."

---

**All templates researched and documented. Ready for Copilot-assisted building.**
