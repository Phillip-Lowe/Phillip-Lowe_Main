# Systack Automation Templates — Curated from n8n Library

**Date:** 2026-06-05
**Purpose:** Templates Systack can deploy for clients and internal use

---

## CATEGORY 1: Lead Generation & Sales

### 🔍 Google Maps Lead Scraper (#2605)
**Use:** Find businesses needing automation services
**Nodes:** Google Sheets, HTTP Request, If (13 nodes)
**Deploy for:** Systack prospecting, finding restaurant clients
**URL:** https://n8n.io/workflows/2605-generate-leads-with-google-maps/

### 📧 Personalized Sales Email Generator (#5691)
**Use:** Cold outreach with LinkedIn enrichment
**Nodes:** Google Sheets, HTTP Request, If, Claude (10 nodes)
**Deploy for:** Systack service pitches, client acquisition
**URL:** https://n8n.io/workflows/5691-generate-personalized-sales-emails-with-linkedin-data-and-claude-37-via-openrouter/

### 📊 Lead Scoring & Routing (#16067)
**Use:** Score website inquiries, route to right team
**Nodes:** Google Sheets, If, Edit Fields (4 nodes)
**Deploy for:** Systack contact form, client qualification
**URL:** https://n8n.io/workflows/16067-score-and-route-website-leads-with-google-sheets-and-gmail/

### 🏢 Local Business Discovery & Enrichment (#15411)
**Use:** Auto-discover and enrich local business leads
**Nodes:** Postgres, Gmail, Sticky Note (5 nodes)
**Deploy for:** CRM pipeline, automated outreach
**URL:** https://n8n.io/workflows/15411-local-business-lead-discovery-and-enrichment-agent/

---

## CATEGORY 2: Invoice & Document Processing

### 📄 PDF to Markdown Converter (#11811)
**Use:** Extract structured data from PDFs
**Nodes:** HTTP Request, If, Google Drive (2 more)
**Deploy for:** Invoice parser enhancement, document processing
**URL:** https://n8n.io/workflows/11811-pdf-to-markdown-converter-with-llamacloud-parser/

### 📧 Invoice Email Processor (#14267)
**Use:** Receive invoices via email, AI classifies, auto-reply
**Nodes:** Send Email, If, No Operation, GPT-4o (6 nodes)
**Deploy for:** Invoice parser email trigger, client acknowledgment
**URL:** https://n8n.io/workflows/14267-send-ai-job-application-auto-replies-with-gmail-openai-gpt-4o-and-smtp/

### 📊 PDF Report Generator (#10650)
**Use:** Generate PDF reports from Sheets data
**Nodes:** Google Sheets, Edit Fields, Loop, Gmail (7 nodes)
**Deploy for:** Client deliverables, invoice summaries
**URL:** https://n8n.io/workflows/10650-generate-and-email-pdf-payslips-from-google-sheets-with-gmail/

---

## CATEGORY 3: AI Agents & Personal Assistants

### 🤖 Basic AI Agent with Memory (#6270)
**Use:** Foundation for all AI agent projects
**Nodes:** Sticky Note, AI Agent, Simple Memory (2 more)
**Deploy for:** Personal Agent template, client AI assistants
**URL:** https://n8n.io/workflows/6270-build-your-first-ai-agent/

### 🤖 Personal Life Manager (#8237)
**Use:** Full personal assistant with Google services
**Nodes:** If, Edit Fields, Telegram, Google services (6 nodes)
**Deploy for:** Systack Personal Agent product
**URL:** https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/

### 🤖 Telegram Voice Assistant (#2462)
**Use:** Voice + text AI assistant
**Nodes:** If, Edit Fields, Telegram (5 nodes)
**Deploy for:** Hands-free client interfaces
**URL:** https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text/

---

## CATEGORY 4: Operations & Monitoring

### 🔔 Website Downtime Monitor (#11763)
**Use:** Monitor service uptime, alert on issues
**Nodes:** Send Email, HTTP Request, Merge, Telegram (7 nodes)
**Deploy for:** Systack service monitoring, client SLA monitoring
**URL:** https://n8n.io/workflows/11763-website-downtime-monitoring-with-smart-alerts-via-telegram-and-email/

### 📅 Daily Reporting & Alerts (#16061)
**Use:** Scheduled monitoring with Sheets logging
**Nodes:** Google Sheets, HTTP Request, If, Telegram (6 nodes)
**Deploy for:** Daily revenue reports, system health, cleanup tasks
**URL:** https://n8n.io/workflows/16061-send-crypto-price-alerts-daily-digests-and-price-replies-with-coingecko-telegram-and-sheets/

### 💾 GitHub Backup for Workflows (#1534)
**Use:** Version control all n8n workflows
**Nodes:** GitHub integration
**Deploy for:** All Systack workflows — URGENT
**URL:** https://n8n.io/workflows/1534-back-up-your-n8n-workflows-to-github/

---

## CATEGORY 5: Content & Marketing

### 📝 SEO Blog Generator (#16062)
**Use:** AI generates blog posts with images
**Nodes:** HTTP Request, Edit Fields, Webhook, WordPress (5 nodes)
**Deploy for:** Systack blog, client content marketing
**URL:** https://n8n.io/workflows/16062-generate-and-publish-seo-blog-posts-to-wordpress-with-gemini-and-dall-e-3/

### 📱 Social Media Scheduler (#16066)
**Use:** Schedule posts, threads, images, polls
**Nodes:** HTTP Request, If, Edit Fields, Webhook (7 nodes)
**Deploy for:** Systack social presence, client social media
**URL:** https://n8n.io/workflows/16066-schedule-x-posts-threads-images-and-polls-with-webhooks/

---

## CATEGORY 6: Data & Analytics

### 📊 Natural Language to Sheets (#7639)
**Use:** Ask questions, get data from Google Sheets
**Nodes:** Sticky Note, AI Agent, OpenAI (2 more)
**Deploy for:** Client reporting without SQL knowledge
**URL:** https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/

### 🗄️ Natural Language to Database (#2090)
**Use:** Chat with database using AI
**Nodes:** Sticky Note, AI Agent, OpenAI (1 more)
**Deploy for:** Analytics, reporting, debugging
**URL:** https://n8n.io/workflows/2090-chat-with-a-database-using-ai/

---

## CATEGORY 7: E-commerce & Ordering (Deli-Specific)

### 🎫 Concert Ticket Booking Validation (#13453)
**Use:** Order validation, payment, confirmation, audit trail
**Nodes:** Google Sheets, HTTP Request, Merge, GPT-4o (9 more)
**Deploy for:** Deli order system reference, client ordering systems
**URL:** https://n8n.io/workflows/13453-validate-concert-ticket-bookings-and-orchestrate-fan-experience-with-gpt-4o-gmail-slack-and-google-sheets/

### 📦 WooCommerce Store Bot (#13503)
**Use:** Telegram bot for store management
**Nodes:** Telegram, Telegram Trigger, Sticky Note, OpenRouter (3 more)
**Deploy for:** Kitchen interface, order lookup, inventory check
**URL:** https://n8n.io/workflows/13503-manage-woocommerce-store-operations-via-ai-telegram-bot-with-openrouter/

### 📊 E-commerce Sales Analysis (#13840)
**Use:** Sales tracking and reporting
**Nodes:** Airtable, Merge, Edit Fields, Slack (5 more)
**Deploy for:** Deli analytics, client e-commerce reporting
**URL:** https://n8n.io/workflows/13840-analyze-woocommerce-category-sales-over-time-with-airtable-and-slack/

---

## Deployment Priority Matrix

| Template | Client Value | Internal Value | Effort | Priority |
|----------|-------------|---------------|--------|----------|
| #1534 GitHub Backup | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Low | 🔴 NOW |
| #11763 Downtime Monitor | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Low | 🔴 NOW |
| #16067 Lead Scoring | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Low | 🔴 NOW |
| #2605 Maps Lead Gen | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Medium | 🟡 SOON |
| #11811 PDF Parser | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Medium | 🟡 SOON |
| #8237 Personal Manager | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | High | 🟡 SOON |
| #6270 AI Agent | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Medium | 🟡 SOON |
| #16062 Blog Generator | ⭐⭐⭐ | ⭐⭐ | Medium | 🟢 LATER |
| #16066 Social Scheduler | ⭐⭐⭐ | ⭐⭐ | Medium | 🟢 LATER |

---

## Integration Checklist

Before deploying any template:

- [ ] Check credential requirements (OAuth, API keys)
- [ ] Verify n8n node versions match our instance (2.20.7-exp)
- [ ] Test in isolated workflow first
- [ ] Document any modifications needed
- [ ] Add to GitHub backup once working

---

## Notes

- **No Square integration templates exist** in n8n library — our deli Square integration is custom
- **No restaurant-specific templates** — we're building category-defining automation
- **AI Agent templates are 2025-2026 trend** — Systack is positioned well here
- **Webhook + Sheets + Email is universal pattern** — applies to almost every client

---

**Next Actions:**
1. Deploy #1534 (GitHub backup) immediately
2. Deploy #11763 (monitoring) for systack.net services
3. Adapt #13453 patterns for deli V3
4. Study #8237 for Personal Agent product spec
