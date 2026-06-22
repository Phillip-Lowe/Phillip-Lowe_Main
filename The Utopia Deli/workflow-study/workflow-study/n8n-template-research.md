# n8n Template Library Research — Systack & Utopia Deli

**Date:** 2026-06-05
**Source:** https://n8n.io/workflows/
**Templates Found:** 9,875 total
**Researcher:** SOL

---

## Executive Summary

The n8n template library has **no restaurant/food-specific workflows** and **no Square payment integrations**. However, several templates provide **proven architectural patterns** we can adapt for:

1. **Utopia Deli** — Order validation, payment lifecycle, audit trails
2. **Systack** — Lead generation, invoice processing, client onboarding, AI agents
3. **Personal Agent** — AI agent patterns, memory systems, webhook APIs

---

## PART 1: Templates Directly Relevant to Utopia Deli

### 🎫 #13453 — Concert Ticket Booking Validation
**URL:** https://n8n.io/workflows/13453-validate-concert-ticket-bookings-and-orchestrate-fan-experience-with-gpt-4o-gmail-slack-and-google-sheets/

**Nodes:** Google Sheets + HTTP Request + Merge + 9 more
**Creator:** Cheng Siong Chin

**What it does:**
- Webhook receives booking request
- Fetches inventory data
- AI Agent validates booking, payment, pricing tier rules, fraud signals
- Routes: auto-approve / conditional handling / escalation
- Fan Experience Agent manages confirmations, waitlist, refunds
- Merge node combines outcomes
- Google Sheets audit trail
- SLA escalation to Slack

**How it maps to Deli:**
| Concert Template | Deli Equivalent |
|------------------|----------------|
| Ticket Validation Agent | CART_STATE builder + total validation |
| Inventory check | Menu/item availability |
| Risk classification | Payment link creation decision |
| Fan Experience Agent | Email composer + confirmation sender |
| Audit trail | CART_STATE + ONLINE_ORDERS sheets |
| SLA escalation | Kitchen notification (future) |

**What we can borrow:**
- Pattern: Webhook → validate → route → email → log
- Merge node usage for parallel branches
- Structured validation with guard conditions
- Google Sheets audit trail pattern

---

### 📦 #13503 — WooCommerce Store Operations via Telegram Bot
**URL:** https://n8n.io/workflows/13503-manage-woocommerce-store-operations-via-ai-telegram-bot-with-openrouter/

**Nodes:** Telegram + Telegram Trigger + Sticky Note + 3 more
**Creator:** Nid Academy

**What it does:**
- Telegram bot interface for e-commerce
- AI agent with memory understands store requests
- Retrieves orders, products, updates info
- Google Sheets logging
- Gmail notifications

**How it maps to Deli:**
- **Kitchen interface:** Telegram bot for kitchen staff to check orders, mark items out of stock
- **Order lookup:** Search CART_STATE by order ID
- **Notification:** Alert kitchen when new orders arrive

**What we can borrow:**
- Telegram bot as secondary interface
- AI agent with memory pattern
- Google Sheets logging integration

---

### 📊 #13840 — WooCommerce Sales Analysis
**URL:** https://n8n.io/workflows/13840-analyze-woocommerce-category-sales-over-time-with-airtable-and-slack/

**Nodes:** Airtable + Merge + Edit Fields (Set) + 5 more
**Creator:** WeblineIndia

**What it does:**
- Analyzes e-commerce sales over time
- Reports to Airtable + Slack

**How it maps to Deli:**
- Daily/weekly sales reporting for deli owner
- Popular items tracking
- Revenue analytics

---

## PART 2: Templates for Systack Business

### 🔍 #2605 — Generate Leads with Google Maps
**URL:** https://n8n.io/workflows/2605-generate-leads-with-google-maps/

**Nodes:** Google Sheets + HTTP Request + If + 13 more
**Creator:** Alex Kim

**What it does:**
- Scrapes Google Maps for business listings
- Extracts contact info, ratings, categories
- Saves to Google Sheets
- Enriches with additional data

**Systack Use Case:**
- **Local business prospecting:** Find businesses in Little Rock that need automation
- **Restaurant outreach:** Identify new restaurants to pitch Utopia-style ordering systems
- **Invoice parser prospects:** Find businesses still doing manual invoice processing

---

### 💼 #15411 — Local Business Lead Discovery and Enrichment Agent
**URL:** https://n8n.io/workflows/15411-local-business-lead-discovery-and-enrichment-agent/

**Nodes:** Postgres + Gmail + Sticky Note + 5 more
**Creator:** Naz Akgül

**What it does:**
- Discovers local businesses
- Enriches with contact data, social profiles
- Stores in Postgres database
- Sends outreach emails via Gmail

**Systack Use Case:**
- **Automated lead gen pipeline:** Replace manual prospecting
- **CRM integration:** Store leads in structured database
- **Drip campaigns:** Automated follow-up sequences

---

### 📧 #5691 — Personalized Sales Emails with LinkedIn Data
**URL:** https://n8n.io/workflows/5691-generate-personalized-sales-emails-with-linkedin-data-and-claude-37-via-openrouter/

**Nodes:** Google Sheets + HTTP Request + If + 10 more
**Creator:** Adam Janes

**What it does:**
- Scrapes LinkedIn profile data
- Generates personalized sales emails with Claude
- Tracks responses in Google Sheets

**Systack Use Case:**
- **Cold outreach personalization:** For Systack services pitches
- **LinkedIn integration:** Already have Systack business account credentials
- **Template-based but personalized:** Scale without losing human touch

---

### 📧 #16067 — Score and Route Website Leads
**URL:** https://n8n.io/workflows/16067-score-and-route-website-leads-with-google-sheets-and-gmail/

**Nodes:** Google Sheets + If + Edit Fields (Set) + 4 more
**Creator:** TinyOps Studio

**What it does:**
- Receives lead data (likely from web form)
- Scores leads based on criteria
- Routes high-value leads to appropriate team member
- Logs everything in Sheets

**Systack Use Case:**
- **Systack website contact form:** Score inquiries (invoice parser vs. personal agent vs. custom)
- **Auto-routing:** Invoice inquiries → fast track; general → nurture sequence
- **Integration with V2 pattern:** Same webhook → Sheets → routing logic

---

## PART 3: Templates for Invoice Parser (Systack Product)

### 📄 #11811 — PDF to Markdown Converter with LlamaCloud
**URL:** https://n8n.io/workflows/11811-pdf-to-markdown-converter-with-llamacloud-parser/

**Nodes:** HTTP Request + If + Google Drive + 2 more
**Creator:** Patrick Campbell

**What it does:**
- Parses PDF documents using LlamaCloud API
- Converts to structured markdown
- Stores in Google Drive

**Systack Use Case:**
- **Invoice parsing enhancement:** Alternative to our custom Python parser
- **Multi-format support:** PDF + image invoices
- **Better extraction:** LlamaCloud specializes in document understanding

---

### 📄 #10650 — Generate and Email PDF Payslips from Google Sheets
**URL:** https://n8n.io/workflows/10650-generate-and-email-pdf-payslips-from-google-sheets-with-gmail/

**Nodes:** Google Sheets + Edit Fields (Set) + Loop Over Items + 7 more
**Creator:** Khairul Muhtadin

**What it does:**
- Reads payroll data from Sheets
- Generates PDF payslips
- Emails to employees
- Batch processing with loops

**Systack Use Case:**
- **Invoice report generation:** Take extracted invoice data → generate PDF reports
- **Client deliverables:** Send processed invoice summaries to clients
- **Batch processing pattern:** Handle multiple invoices in one run

---

### 📧 #14267 — AI Job Application Auto-Replies
**URL:** https://n8n.io/workflows/14267-send-ai-job-application-auto-replies-with-gmail-openai-gpt-4o-and-smtp/

**Nodes:** Send Email + If + No Operation + 6 more
**Creator:** Md Abdullah Al Noman

**What it does:**
- Receives emails (job applications)
- AI classifies and generates personalized replies
- Sends via Gmail or SMTP

**Systack Use Case:**
- **Invoice parser email trigger:** Receive invoices via email → AI classifies → processes
- **Auto-acknowledgment:** Confirm receipt to clients
- **SMTP fallback:** Same as our deli gmail setup

---

## PART 4: Templates for AI Agent / Personal Agent

### 🤖 #6270 — Build Your First AI Agent
**URL:** https://n8n.io/workflows/6270-build-your-first-ai-agent/

**Nodes:** Sticky Note + AI Agent + Simple Memory + 2 more
**Creator:** Lucas Peyrin

**What it does:**
- Basic AI agent with memory
- Processes requests and maintains context

**Systack Use Case:**
- **Personal Agent foundation:** The core pattern we're building for clients
- **Memory system:** Learn how n8n Simple Memory works
- **Tool integration:** Pattern for adding capabilities (calendar, email, notes)

---

### 🤖 #2462 — Angie, Personal AI Assistant with Telegram Voice
**URL:** https://n8n.io/workflows/2462-angie-personal-ai-assistant-with-telegram-voice-and-text/

**Nodes:** If + Edit Fields (Set) + Telegram + 5 more
**Creator:** Derek Cheung

**What it does:**
- Personal AI assistant via Telegram
- Voice and text input
- Integrates with multiple services
- Persistent memory

**Systack Use Case:**
- **Personal Agent interface:** Telegram as one of many interfaces
- **Voice input:** Future capability for hands-free interaction
- **Memory + context:** How to build persistent agent identity

---

### 🤖 #8237 — Personal Life Manager with Telegram, Google Services & AI
**URL:** https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/

**Nodes:** If + Edit Fields (Set) + Telegram + 6 more
**Creator:** Derek Cheung

**What it does:**
- Comprehensive personal manager
- Calendar, tasks, notes, reminders
- Google services integration
- Voice-enabled AI

**Systack Use Case:**
- **Full Personal Agent blueprint:** Exactly what Systack wants to offer clients
- **Google integration:** Gmail, Calendar, Drive, Sheets
- **Multi-modal:** Text + voice interface

---

### 🤖 #5407 — Learn Code Node (JavaScript) Interactive Tutorial
**URL:** https://n8n.io/workflows/5407-learn-code-node-javascript-with-an-interactive-hands-on-tutorial/

**Nodes:** Edit Fields (Set) + Sticky Note + Code + 2 more
**Creator:** Lucas Peyrin

**What it does:**
- Interactive tutorial for n8n Code nodes
- Teaches JavaScript within n8n sandbox

**Systack Use Case:**
- **Team training:** Teach new team members n8n Code node patterns
- **Reference:** ES5-safe code patterns (no spread, no template literals)
- **Best practices:** Proper error handling, data normalization

---

## PART 5: Templates for Operations / DevOps

### 🔄 #1750 — Creating an API Endpoint
**URL:** https://n8n.io/workflows/1750-creating-an-api-endpoint/

**Nodes:** (Basic webhook pattern)
**Creator:** n8n Team

**What it does:**
- Best practices for webhook/API endpoints
- Request validation
- Response formatting
- Error handling

**Systack Use Case:**
- **All our webhook workflows:** Deli HTML V2, Invoice Parser, etc.
- **Pattern reference:** How to structure robust API endpoints

---

### 🔄 #1534 — Back Up Your n8n Workflows To Github
**URL:** https://n8n.io/workflows/1534-back-up-your-n8n-workflows-to-github/

**Nodes:** (GitHub integration)
**Creator:** n8n Team

**What it does:**
- Automatically backs up workflow JSON to GitHub
- Version control for workflows
- Disaster recovery

**Systack Use Case:**
- **URGENT:** We should implement this immediately
- **Backup strategy:** All deli + Systack workflows
- **Version history:** Track changes, rollback capability

---

### 🔄 #1747 — Joining Different Datasets
**URL:** https://n8n.io/workflows/1747-joining-different-datasets/

**Nodes:** (Merge node patterns)
**Creator:** n8n Team

**What it does:**
- How to properly use Merge nodes
- Different join types (append, merge, pass-through)
- Data combination patterns

**Systack Use Case:**
- **Deli workflow parallel branches:** Normalize → [Write Sheets + Create Payment] → Merge
- **Invoice processing:** Multiple data sources (email, upload, API)

---

### 🔔 #11763 — Website Downtime Monitoring
**URL:** https://n8n.io/workflows/11763-website-downtime-monitoring-with-smart-alerts-via-telegram-and-email/

**Nodes:** Send Email + HTTP Request + Merge + 7 more
**Creator:** Muntasir Mubin

**What it does:**
- Monitors website uptime
- Sends alerts via Telegram + Email
- Smart alerting (avoids spam)

**Systack Use Case:**
- **Service monitoring:** Monitor n8n.systack.net, utopia-deli.com, etc.
- **Client SLA monitoring:** Alert if client services go down
- **Multi-channel alerts:** Email + Telegram

---

### 🔔 #16061 — Send Crypto Price Alerts (Cron + Sheets + Telegram)
**URL:** https://n8n.io/workflows/16061-send-crypto-price-alerts-daily-digests-and-price-replies-with-coingecko-telegram-and-sheets/

**Nodes:** Google Sheets + HTTP Request + If + 6 more
**Creator:** Cybernative Technologies

**What it does:**
- Scheduled monitoring (cron)
- Fetches external data
- Logs to Sheets
- Sends alerts

**Systack Use Case:**
- **Daily reporting:** Revenue, orders, system health
- **Scheduled tasks:** Invoice cleanup, link deletion (like our existing deli cleanup)
- **Health checks:** Service status monitoring

---

## PART 6: Templates for Content / Marketing

### 📝 #16062 — Generate SEO Blog Posts with Gemini and DALL-E 3
**URL:** https://n8n.io/workflows/16062-generate-and-publish-seo-blog-posts-to-wordpress-with-gemini-and-dall-e-3/

**Nodes:** HTTP Request + Edit Fields (Set) + Webhook + 5 more
**Creator:** Muhammad Adeel

**What it does:**
- AI generates blog content
- Creates images
- Publishes to WordPress
- Webhook trigger

**Systack Use Case:**
- **Systack blog automation:** Generate case studies, tech articles
- **Client content:** Help clients with content marketing
- **SEO pipeline:** Keyword research → content → publish

---

### 📱 #16066 — Schedule X Posts, Threads, Images with Webhooks
**URL:** https://n8n.io/workflows/16066-schedule-x-posts-threads-images-and-polls-with-webhooks/

**Nodes:** HTTP Request + If + Edit Fields (Set) + 7 more
**Creator:** Jesse Lane

**What it does:**
- Social media scheduling
- Thread creation
- Image/poll support
- Webhook API

**Systack Use Case:**
- **Systack social media:** Automated posting for Systack and client accounts
- **Content calendar:** Schedule posts in advance
- **Cross-posting:** X, LinkedIn, etc.

---

## PART 7: Integration-Specific Templates

### 📊 #7639 — Talk to Your Google Sheets Using ChatGPT-5
**URL:** https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/

**Nodes:** Sticky Note + AI Agent + OpenAI Chat Model + 2 more
**Creator:** Robert Breen

**What it does:**
- Natural language interface to Google Sheets
- Query data with AI
- Get insights without SQL

**Systack Use Case:**
- **Deli reporting:** "How many orders today?" → AI queries CART_STATE
- **Invoice analytics:** "Which client has the most invoices?"
- **No-code reporting:** Owner asks questions, gets answers

---

### 📊 #2090 — Chat with a Database Using AI
**URL:** https://n8n.io/workflows/2090-chat-with-a-database-using-ai/

**Nodes:** Sticky Note + AI Agent + OpenAI Chat Model + 1 more
**Creator:** David Roberts

**What it does:**
- AI agent connects to database
- Natural language queries
- SQL generation

**Systack Use Case:**
- **n8n SQLite queries:** "Show me failed workflows from yesterday"
- **Invoice database:** "Find all unpaid invoices over $1000"
- **Analytics without SQL:** Natural language to data

---

## Summary: What We Should Implement

### Immediate (This Week)

| Priority | Template | Use Case | Effort |
|----------|----------|----------|--------|
| 🔴 HIGH | #1534 — Backup to GitHub | Version control all workflows | 1 hour |
| 🔴 HIGH | #1750 — API Endpoint Best Practices | Improve webhook robustness | 2 hours |
| 🟡 MEDIUM | #13453 — Concert Booking Pattern | Reference for deli V3 improvements | Reference only |
| 🟡 MEDIUM | #11763 — Downtime Monitoring | Monitor all Systack services | 2 hours |

### Short Term (This Month)

| Priority | Template | Use Case | Effort |
|----------|----------|----------|--------|
| 🟡 MEDIUM | #2605 — Google Maps Lead Gen | Find local prospects | 4 hours |
| 🟡 MEDIUM | #16067 — Score and Route Leads | Systack website form | 3 hours |
| 🟢 LOW | #11811 — PDF to Markdown | Invoice parser enhancement | 8 hours |
| 🟢 LOW | #8237 — Personal Life Manager | Personal Agent blueprint | 1-2 weeks |

### Long Term (Next Quarter)

| Priority | Template | Use Case | Effort |
|----------|----------|----------|--------|
| 🟢 LOW | #2462 — Telegram Voice Assistant | Kitchen interface | 1 week |
| 🟢 LOW | #16062 — SEO Blog Automation | Systack content marketing | 1 week |
| 🟢 LOW | #16066 — Social Media Scheduling | Systack social presence | 3 days |
| 🟢 LOW | #2090 — Chat with Database | AI-powered reporting | 1 week |

---

## Key Patterns Learned

### 1. **Webhook → Validate → Route → Act → Log**
This pattern appears in 80% of useful templates. Our deli V2 already follows this.

### 2. **Merge Node is Critical for Parallel Branches**
Templates show proper Merge usage after parallel execution paths. We should audit our workflows for missing Merge nodes.

### 3. **Google Sheets as Universal Audit Trail**
Almost every template uses Sheets for logging. Our CART_STATE approach is standard.

### 4. **AI Agent + Memory = Future of n8n**
2025-2026 templates heavily feature AI agents with memory. This is where Systack should focus.

### 5. **Multi-Channel Alerts (Email + Telegram + Slack)**
Templates use multiple channels for different urgency levels. We should add Telegram/Slack for kitchen alerts.

---

## Files

- Source: `~/utopia-deli-revamp/workflow-study/n8n-template-research.md`
- Related: `~/utopia-deli-revamp/workflow-study/DELI-SYSTEM-ARCHITECTURE.md`
- Related: `~/utopia-deli-revamp/workflow-study/HTML-TO-DELI-SYSTEM-ALIGNMENT-PLAN.md`

---

**Next Action:**
1. Implement #1534 (GitHub backup) for all Systack workflows
2. Use #13453 patterns to design deli V3 kitchen notification
3. Study #8237 for Personal Agent architecture
4. Deploy #2605 for Systack lead generation
