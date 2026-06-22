# Systack — Two-Tier AI Automation Service Packages

> **Not AI consulting. Specific, named automations that run your business.**

---

## PREMIUM TIER — Systack Private

### Tagline
**"100% Private AI Automation. Your Data Never Leaves Your Building."**

### Target Client Profile

- **Industries:** Law firms, medical clinics, dental practices, accounting offices, financial advisors, insurance agencies, government contractors
- **Pain point:** Handles sensitive client data (PHI, PII, financial records, legal docs). Cannot use ChatGPT, Claude, or any cloud AI. Compliance mandates (HIPAA, GDPR, PCI, attorney-client privilege) make cloud AI a non-starter.
- **Current reality:** Staff manually typing invoices, extracting data from PDFs, responding to routine emails, entering data across systems. Hours lost daily.
- **Ideal size:** 5–100 employees. Has volume to justify dedicated hardware.

### The Pitch
Your data never touches the internet. Every model, every document, every automation runs on a dedicated machine inside your office — behind your firewall. Zero exposure to OpenAI, Anthropic, Google, or any third-party AI provider. You get the automation. They get nothing.

### Infrastructure
- **Hardware:** Dedicated Mac Studio or Linux workstation with NVIDIA RTX 4090 (24 GB VRAM) — installed on-premises
- **Network:** Fully air-gapped or firewalled to your internal LAN. No outbound AI traffic. Ever.
- **Models:**
  - `llama3-70b-instruct` (4-bit quantized) — High-capability reasoning for document understanding, email drafting, data extraction
  - `command-r` or `command-r-plus` — Optimized for RAG, tool use, and multi-step workflows
  - `nomic-embed-text` — Private vector embeddings for document search
- **Management:** Systack handles all model updates, quantization tuning, and hardware maintenance remotely via secure Tailscale tunnel (outbound management only; AI data stays local)

### Included Automations

| Automation | What It Does | Notifications | File Storage |
|---|---|---|---|
| **Private Document Extraction Pipeline** | Ingest scanned PDFs, contracts, invoices, medical records. Extract names, dates, amounts, CPT codes, line items. Output structured data to your system. | SMS to owner | Local filesystem |
| **Automated Invoice Processing System** | Receive invoices via email or scan. Classify, extract totals/vendors/line items, route for approval, push to QuickBooks/Xero. | SMS to owner | Local filesystem (`/data/invoices/`) |
| **Self-Hosted Customer Support Automations** | Auto-draft responses to routine client emails (appointment confirmations, document requests, status updates). Human reviews before send. | Email to client | Local email (SMTP) |
| **Local Data Entry Elimination System** | Watch designated folders or email inboxes. Extract data from PDFs, forms, emails. Populate your CRM, EHR, or practice management software. | SMS to owner | Local filesystem |
| **Private Knowledge Base Search** | Index your internal documents (policies, procedures, case files). Staff asks questions in natural language. Answers sourced exclusively from your documents. | In-app only | Local filesystem |
| **Automated Compliance Audit Trail** | Every AI action logged. Full chain of custody for every document touched. Audit-ready at any moment. | SMS to admin | Postgres on-premise |

### Zero Cloud Apps

| What Others Use | What Systack Private Uses |
|-----------------|---------------------------|
| Slack notifications | **SMS via Twilio** (client account) |
| Google Drive | **Local filesystem** (`/data/clients/`, `/data/invoices/`) |
| Google Calendar | **Email-based scheduling** or local CalDAV |
| Google Sheets | **PostgreSQL on-premise** |
| OpenAI/Claude API | **Local Ollama models** (llama3, command-r) |
| Cloud n8n | **Self-hosted n8n** on local hardware |

**Your data never touches:** Slack, Google, OpenAI, Anthropic, Microsoft, or any cloud AI provider.

### Service & Support

- **Onboarding:** White-glove hardware install + network configuration + model setup (1–2 weeks)
- **Training:** 2 half-day sessions with your team — what the system does, how to review outputs, what to watch for
- **Support:** Priority Slack/phone support, 4-hour response SLA during business hours
- **Maintenance:** Quarterly model updates, hardware health checks, prompt tuning
- **Uptime SLA:** 99.5% (excludes hardware failure beyond Systack's control; replacement hardware sourced within 48 hours)

### Pricing

| Item | Cost |
|---|---|
| **Hardware (one-time)** | $6,500 – $9,500 (Mac Studio or Linux + RTX 4090 — client owns hardware) |
| **Setup & Deployment** | $4,500 one-time (includes install, configuration, model setup, initial training) |
| **Monthly Retainer** | **$799/mo** (maintenance, support, model updates, prompt tuning) |
| **Annual Contract** | **$699/mo** (saves $1,200/year) |
| **Subscribe** | <stripe-buy-button buy-button-id="buy_btn_1TfVnF1WicviTxiiQnuePKHa" publishable-key="pk_live_51Tckdx1WicviTxii6uKLsxzQENJqWDNxt8Zqmst9YKBQ4F0KSn7VpuR7PZTGRQXJMv42NwimR1kcIdOxElznzIsM000DBc6pKp"></stripe-buy-button> |

### Why This Price?

- Enterprise-grade privacy isn't cheap. The hardware alone is $7K+.
- Competitors selling "private AI" charge $2,000–$5,000/month for managed deployments.
- This is a managed appliance, not SaaS. You own the box. We keep it running.

---

## STANDARD TIER — Systack Accelerate

### Tagline
**"High-Speed AI Automation. Managed Infrastructure. Scale on Demand."**

### Target Client Profile

- **Industries:** E-commerce stores, real estate agencies, marketing firms, property management, small law firms (non-litigation), insurance brokerages, dental offices (non-surgical), boutique accounting firms
- **Pain point:** Manual, repetitive tasks eating hours. Staff doing data entry instead of revenue work. Customer inquiries piling up. Need automation now, at a price that makes immediate sense.
- **Current reality:** Copy-pasting between systems. Manually responding to the same 20 questions. Hand-entering orders, listings, or invoices.
- **Ideal size:** 2–50 employees. Fast-moving, growth-oriented.

### The Pitch
Your automations run on secure cloud GPU instances behind an encrypted VPN tunnel. Sub-2-second inference on every task. Pay for what you use. No hardware to buy. No IT overhead. The same private models, cloud-hosted.

### Infrastructure
- **Compute:** Secure cloud GPU instances (RunPod / Lambda Labs) in US data centers
- **Network:** WireGuard VPN tunnel (Tailscale) — encrypted point-to-point. Your data is encrypted in transit and at rest.
- **Models:**
  - `llama3-8b-instruct` (full precision) — Sub-2s inference for high-volume tasks
  - `mistral-7b` or `mixtral-8x7b` — Efficient routing, classification, extraction
  - `nomic-embed-text` — Embedded search and retrieval
- **Scaling:** Auto-scaling GPU instances. Spikes in volume? Capacity adjusts automatically. No queueing. No waiting.
- **Management:** Fully managed by Systack. You never touch a server.

### Included Automations

| Automation | What It Does | Notifications | File Storage |
|---|---|---|---|
| **Automated Invoice Processing System** | Ingest invoices (PDF, email, scan). Extract vendor, total, line items, due date. Push to your accounting system. Flag exceptions for human review. | Slack + email | Google Drive (client account) |
| **Self-Hosted Customer Support Automations** | Auto-classify incoming emails/support tickets. Draft responses for common inquiries (order status, return policy, hours, pricing). Human reviews and sends. | Slack + email | Google Drive |
| **Local Data Entry Elimination System** | Monitor designated sources (email, webhooks, spreadsheets). Extract structured data. Populate your CRM, ERP, or database automatically. | Slack alert | Google Sheets |
| **Automated Lead Qualification Pipeline** | Incoming leads scored and routed based on your criteria. High-intent leads flagged. Tire-kickers get automated nurture. | Slack + email | Google Sheets |
| **Document Classification & Routing Engine** | Incoming documents auto-sorted by type (contract, invoice, application, form). Routed to correct department or folder. | Slack | Google Drive |
| **Scheduled Report Generator** | Auto-generate daily/weekly summary reports from your data. Delivered to Slack, email, or Google Sheets. | Slack/email | Google Sheets |

### Cloud Apps Used (Client-Owned Accounts)

| App | What We Use It For | Who Owns It |
|-----|-------------------|-------------|
| **Stripe** | Payment processing | Client |
| **Slack** | Team notifications | Client |
| **Google Workspace** | Drive, Sheets, Calendar | Client |
| **PostgreSQL** | Data storage | Systack (cloud VPS) |
| **n8n** | Workflow engine | Systack (self-hosted) |
| **AI Models** | Local Ollama | Systack (local, not cloud) |

**Your AI never touches:** OpenAI, Anthropic, Google AI, or any foundation model API. All inference is local.

### Service & Support

- **Onboarding:** Remote setup + integration configuration (3–5 business days)
- **Training:** 1 live training session + video library + documented playbooks
- **Support:** Email + Slack support, same-business-day response
- **Maintenance:** Continuous model tuning, prompt optimization, usage monitoring
- **Uptime SLA:** 99.9%

### Pricing

| Item | Cost |
|---|---|
| **Setup & Integration** | $2,500 one-time |
| **Monthly Retainer** | **$249/mo** (up to 10,000 automation runs/month) |
| **Volume Add-on** | **$349/mo** (up to 25,000 automation runs/month) |
| **Annual Contract** | **$199/mo** (saves $600/year — 10K tier) |
| **Subscribe** | <stripe-buy-button buy-button-id="buy_btn_1TfW2x1WicviTxiiXf2rPcot" publishable-key="pk_live_51Tckdx1WicviTxii6uKLsxzQENJqWDNxt8Zqmst9YKBQ4F0KSn7VpuR7PZTGRQXJMv42NwimR1kcIdOxElznzIsM000DBc6pKp"></stripe-buy-button> |

### Why This Price?

- Less than the cost of a part-time admin ($1,500+/month).
- Competitors charge $500–$1,500/month for similar managed AI automation.
- You're paying for managed infrastructure + ongoing optimization, not per-seat SaaS licensing.

---

## Comparison Table

| Feature | Systack Private (Premium) | Systack Accelerate (Standard) |
|---|---|---|
| **Data Location** | On-premises, air-gapped | Secure cloud VPS, encrypted |
| **Privacy Level** | Absolute — zero external exposure | High — no cloud AI, client owns app accounts |
| **Notifications** | SMS (Twilio) | Slack |
| **File Storage** | Local filesystem (`/data/...`) | Google Drive (client account) |
| **Calendar** | Email-based or CalDAV | Google Calendar (client account) |
| **Database** | PostgreSQL on-premise | PostgreSQL cloud VPS (Systack managed) |
| **AI Models** | Local Ollama (llama3, command-r) | Local Ollama (llama3, mistral) |
| **Cloud Apps Used** | **ZERO** — Stripe only (client account) | **Slack, Google Workspace** — client accounts |
| **Compliance** | HIPAA, PCI, attorney-client ready | SOC 2 compliant infrastructure |
| **Hardware** | Client-owned dedicated server | Systack-managed cloud VPS |
| **Hardware Cost** | $6,500–$9,500 (client-owned) | $0 |
| **Setup Fee** | $4,500 | $2,500 |
| **Monthly Fee** | $799/mo | $249/mo |
| **Support Response** | 4-hour SLA (business hours) | Same business day |
| **Onboarding** | 1–2 weeks (white-glove) | 3–5 business days (remote) |
| **Scaling** | Hardware-limited (upgradable) | Auto-scaling cloud |
| **Best For** | Regulated industries, sensitive data | Growth businesses, cost-conscious |

### Both Tiers Share:
- **Local AI models** (Ollama) — never OpenAI/Claude
- **Client-owned Stripe** — we never touch your money
- **Self-hosted n8n** — we manage the engine
- **PostgreSQL database** — robust, structured data storage
- **Human-in-the-loop review** — no fully autonomous customer-facing actions

---

## FAQ

### "Is this AI consulting?"
**No.** Systack does not sell "AI strategy," "AI readiness assessments," or "AI roadmaps." We sell **named, deployed automations** that process invoices, extract data, classify documents, and respond to customers. You get working systems, not slide decks.

### "What's the difference between this and ChatGPT/Claude?"
ChatGPT and Claude are cloud-hosted general-purpose chatbots. Your data goes to OpenAI or Anthropic's servers. Systack Private runs entirely on your hardware with zero external data transmission. Systack Accelerate runs on private cloud instances behind encrypted tunnels. Neither shares your data with foundation model companies. And neither is a chatbot — they're purpose-built automation pipelines.

### "Do I need technical staff to run this?"
No. Systack manages everything. For Private tier, we install the hardware, configure the network, and maintain the models remotely. For Accelerate, there's nothing on-site. You interact with outputs — reviewed emails, extracted data, classified documents — not with models or servers.

### "What if the hardware fails? (Private tier)"
Hardware is client-owned and under manufacturer warranty. Systack maintains a replacement parts pipeline with 48-hour turnaround. Critical clients can opt for redundant hardware (+$3,500 one-time).

### "Can I switch between tiers?"
Yes. Start with Accelerate, prove ROI, then move to Private when privacy requirements or volume justifies it. Setup fees are credited toward upgrade if done within 6 months.

### "What's the real difference between Private and Accelerate?"
**Accelerate** uses your Slack and Google accounts for convenience. **Private** replaces those with SMS and local storage so your data never touches Slack/Google servers. Both use the same local AI, same Stripe integration, same core automations.

### "Do you offer a 'cloud' tier with OpenAI?"
No. Every Systack tier uses **local AI models** (Ollama). We don't offer a cloud-AI option because that would expose your data to OpenAI/Anthropic. If you want cloud AI, Zapier + ChatGPT is a better fit.

### "What if I don't have Google Workspace or Slack?"
**Accelerate:** We help you create free Slack + Google accounts during onboarding.  
**Private:** You don't need them. We use SMS and local storage instead.

### "What automations are NOT included?"
We don't automate client-facing chat without human review. We don't automate legal advice, medical diagnosis, or financial recommendations. We don't build public-facing AI chatbots (different service). We don't train custom models from scratch.

### "What's an 'automation run'? (Accelerate tier)"
One automation run = one complete task execution (e.g., processing one invoice, classifying one document, drafting one email response). The 10K/mo tier covers most small businesses. We'll show your usage dashboard so there are no surprises.

### "How long until I see results?"
Private tier: 2–3 weeks from contract to live automations. Accelerate tier: 1 week. Most clients report time savings within the first month.

### "Do you work with my existing software?"
We integrate with common platforms: QuickBooks, Xero, Salesforce, HubSpot, Google Workspace, Microsoft 365, Slack, and most CRMs/EHRs with APIs. Custom integrations available at additional cost.

---

---

## SAOS Agent Fleet Subscriptions

### What's SAOS?
SAOS (Systack Agent Operating System) is our managed agent service. Subscribe to get your own team of AI agents that run 24/7.

### Our Minimum Standard

**We don't sell anything below 16GB RAM.** We learned the hard way: 4GB swaps to death, 8GB is tight, 16GB is where agents actually work. Anything less = frustrated users, support tickets, refunds.

### Personal Track — For Individuals

| Tier | Price | RAM | Best For |
|------|-------|-----|----------|
| **SAOS Personal+** | **$199/mo** | **16GB** | Power users who want a working agent |

#### SAOS Personal+ — $199/mo
Your AI sidekick that actually works:
- **16GB dedicated VPS** — not shared, not tight
- **Local models** — qwen2.5:7b or gemma-2-9b (included)
- **32K context** — remembers conversations
- **Email triage and drafting**
- **Calendar management and scheduling**
- **Task reminders and follow-ups**
- **Document summarization**
- **Research assistance**
- **Multi-device sync**
- **Voice interaction** (local Whisper)
- **Local dashboard** — see what your agent is doing
- **n8n workflows** (up to 5,000 runs/mo)
- **Email support**

**Optional cloud LLM:** Want Claude or ChatGPT instead of local? We pass API costs through (no markup). You pay the provider directly.

---

### Business Track — For Teams

| Tier | Price | RAM | Best For |
|------|-------|-----|----------|
| **SAOS Business Fleet** | **$299/mo** | **16GB** | Small team (2-10 people) |
| **SAOS Enterprise Fleet** | **$799/mo** | **On-premise** | Large team (10+), regulated industries |

#### SAOS Business Fleet — $299/mo
Multi-agent team for your business:
- Everything in Personal+
- **Team collaboration** via Slack
- **Invoice processing** pipeline
- **Lead qualification** and routing
- **Customer support drafting**
- Up to 5 team members
- **10,000 n8n runs/mo**

#### SAOS Enterprise Fleet — $799/mo
Full private automation suite:
- Everything in Business Fleet
- **On-premise deployment** — hardware in your building
- **HIPAA-grade privacy** — zero cloud exposure
- **Dedicated hardware** — Mac Studio or Linux + RTX 4090
- **White-glove setup** — we install, configure, train
- **Priority support** — 4-hour SLA
- **Unlimited n8n runs**

---

### Subscribe Now

| Tier | Monthly | What You Get |
|------|---------|--------------|
| **Personal+** | $199/mo | 16GB VPS, local models, dashboard, email support |
| **Business Fleet** | $299/mo | Team features, Slack, 10K runs, 5 members |
| **Enterprise Fleet** | $799/mo | On-premise, HIPAA, dedicated hardware, white-glove |

**[Subscribe to SAOS Personal+](https://buy.stripe.com/7sYcMYfZLagn9wQ7MG87K03)**  
**[Subscribe to SAOS Business](https://buy.stripe.com/dRm9AMcNzgELdN6d7087K0a)**  
**[Subscribe to SAOS Enterprise](https://buy.stripe.com/cNi8wI9Bnbkr5gAc2W87K0b)**

---

## Systack Services (Done-For-You)

For businesses that want us to build and manage everything:

| Tier | Price | Setup | Best For |
|------|-------|-------|----------|
| **Systack Accelerate** | $249/mo | $2,500 | Small business, cloud-hosted |
| **Systack Private** | $799/mo | $4,500 | Regulated industries, on-premise |

[Learn more about Systack Services →](/services)

---

---

## Next Steps

1. **Free Assessment Call** — 30 minutes. We learn your workflows, identify the highest-ROI automation, and recommend a tier.
2. **Scoping Document** — We deliver a written scope with exact automations, integrations, timeline, and price. No commitment required.
3. **Deployment** — We build, you review, we launch.

📞 **Call: (501) 274-6231**  
📧 **Email: support@systack.net**

---

*Systack — Automation that runs your business, not your mouth.*
