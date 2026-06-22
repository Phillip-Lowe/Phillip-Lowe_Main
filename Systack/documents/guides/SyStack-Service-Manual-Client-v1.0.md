---
title: "SyStack Service Manual"
subtitle: "Digital Operations Layer — Client Overview"
version: "1.0"
date: "2026-06-19"
status: "CLIENT-FACING"
classification: "CLIENT DELIVERABLE"
author: "SyStack Operations"
website: "https://systack.net"
---

# SyStack Service Manual

## Document Metadata

| Field | Value |
|-------|-------|
| **Document** | SYS-CLIENT-MANUAL-v1.0 |
| **For** | Current & Prospective Clients |
| **Classification** | Client Deliverable |
| **Last Updated** | 2026-06-19 |
| **Website** | https://systack.net |
| **Support** | support@systack.net |

---

# Part I: About SyStack

## Who We Are

**SyStack builds autonomous operations infrastructure for businesses that refuse to operate at human speed.**

Every business has repetitive work that shouldn't require a human. We build the infrastructure — intelligent agents, workflow automations, and orchestration layers — that removes the friction between "need it done" and "it's done."

### Our Mission
By 2028, every business operating at fewer than 50 employees will have a digital operations layer as standard as a website. SyStack defines what that layer looks like, how it integrates, and how it scales.

### What We Believe

| Value | What It Means |
|-------|---------------|
| **Ship Over Slides** | Working systems, not presentations. Every deliverable is tested end-to-end. |
| **Remove Drudge, Not People** | Our systems don't replace your team. They remove the parts of the job that waste human attention. |
| **Your Data, Your Control** | Information stays with you. We build, you own. |
| **No Black Boxes** | You see what we built, how it works, and how to maintain it. Transparency in everything. |
| **Earned Trust** | We don't promise what we can't deliver. We document what we delivered so it lasts. |

---

# Part II: The Digital Operations Layer

## What Is SAOS?

**SAOS** (SyStack Autonomous Operations Stack) is a fully managed AI-powered operations layer deployed to a dedicated cloud environment. It includes:

- **Intelligent Agents** — Specialized AI assistants for different business functions
- **Workflow Automation** — n8n-powered automations connecting your tools
- **Secure Networking** — Zero-configuration VPN access via Tailscale
- **Local AI Inference** — Private, self-hosted AI model for document processing and analysis
- **Database & Storage** — Managed PostgreSQL and SQLite
- **Email Integration** — SMTP/IMAP connections for invoice capture and communication
- **Monitoring & Backups** — Automated health checks and hourly snapshots

Think of SAOS as your business's digital nervous system: it observes, processes, and responds — automatically.

## How It Works

```
Your Business Data
        │
        ▼
┌─────────────────────────────────────┐
│          AI Agents Layer             │
│  • Invoice Reader (auto-extracts)    │
│  • Booking Manager (auto-schedules)  │
│  • Communication Hub (auto-notifies) │
│  • Document Processor (auto-files)   │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│       Workflow Automation            │
│  • n8n orchestration engine          │
│  • Trigger-based pipelines           │
│  • API integrations                  │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│        Secure Infrastructure         │
│  • Encrypted VPN tunnel              │
│  • Firewall + intrusion protection   │
│  • Automated backups                 │
│  • Health monitoring                 │
└─────────────────────────────────────┘
```

---

# Part III: Service Plans

## SAOS Subscription Tiers

Choose the plan that fits your business size and automation needs.

| Feature | **Starter** | **Professional** | **Business** | **Enterprise** |
|---------|-------------|------------------|--------------|----------------|
| **Monthly Price** | $49 | $149 | $299 | Custom |
| **VPS Resources** | 1 vCPU / 1GB RAM | 2 vCPU / 4GB RAM | 4 vCPU / 16GB RAM | 8 vCPU / 32GB+ |
| **AI Model** | — | qwen2.5:7b | qwen2.5:7b + Whisper | Multi-model cluster |
| **Included Agents** | 3 core | 7 core | Full fleet (10) | Custom agents |
| **Workflow Limit** | 5 | 20 | Unlimited | Unlimited |
| **Storage** | 25 GB SSD | 80 GB SSD | 160 GB NVMe | 320 GB NVMe |
| **Data Transfer** | 1 TB/mo | 3 TB/mo | 6 TB/mo | Unmetered |
| **Backups** | Weekly snapshots | Daily snapshots | Hourly snapshots | Continuous replication |
| **Support** | Email (24h) | Email + Chat (24h) | Priority + Phone (24h) | Dedicated + SLA |
| **Typical Setup** | 5 minutes | 10 minutes | 8 minutes | 15 minutes |

### What's Included in All Plans

- **Zero-Config VPN** — Tailscale provides secure access from any device
- **Firewall Protection** — UFW + fail2ban blocks unauthorized access
- **Security Updates** — Automated patching and vulnerability management
- **PostgreSQL Database** — Relational data storage for your applications
- **Email Processing** — SMTP/IMAP integration for invoice and order capture
- **Webhook Endpoints** — Receive events from Stripe, Square, and custom sources
- **Agent Memory** — Persistent context across conversations and workflows

### What's Not Included (Available Separately)

- **Custom Domain** — Your vanity URL for white-label deployments
- **Multi-Location Replication** — Geographically distributed backups
- **Advanced Compliance** — HIPAA, SOC 2, or custom audit frameworks
- **Custom AI Training** — Fine-tuned models on your proprietary data

---

# Part IV: Products & Integrations

## Invoice Automation

**What it does:** Reads incoming invoices via email, extracts data automatically (vendor, amounts, line items), stores in a searchable database, presents in a web dashboard.

**Supported formats:** PDF (native + scanned with OCR), images (PNG/JPG), email body text  
**Accuracy:** 95%+ on structured invoices, 85%+ on scanned documents  
**Demo:** Available upon request

## Online Ordering System

**What it does:** White-label food ordering with integrated payment processing, kitchen display, and customer notifications.

**Features:** Menu builder, real-time order tracking, Square payment integration, SMS/Email confirmations  
**Live example:** Utopia Deli (https://order.theutopiadeli.com)  
**Setup time:** 2-4 weeks for custom branding

## No-Show Prevention

**What it does:** Booking system with automated reminders (SMS + email) and one-click reschedule.

**Features:** T-24h, T-2h, and T-15min reminders, calendar integration, waitlist management  
**Typical result:** 40-60% reduction in no-shows  
**Integration:** Works with Square, Google Calendar, and custom booking forms

## VPS Provisioning Pipeline

**What it does:** Automated cloud infrastructure deployment for businesses needing dedicated environments.

**Use case:** Franchises needing identical systems across locations, agencies managing client infrastructure  
**Deployment time:** Under 10 minutes from order to ready  
**Management:** Fully managed with automated updates

---

# Part V: Security & Compliance

## Security Standards

| Layer | Protection |
|-------|------------|
| **Network** | WireGuard VPN (Tailscale), firewall rules, intrusion detection |
| **Transport** | TLS 1.3 encryption for all connections |
| **Storage** | AES-256 encryption at rest |
| **Access** | Role-based permissions, no shared credentials |
| **Updates** | Automated security patches, tested before deployment |
| **Backups** | Encrypted snapshots with configurable retention |
| **Monitoring** | 24/7 automated health checks with alerting |

## Compliance Framework

SyStack maintains compliance documentation for:

| Standard | Status | Notes |
|----------|--------|-------|
| **GDPR** | ✅ Implemented | Data residency options available |
| **CCPA** | ✅ Implemented | Consumer rights management built-in |
| **SOC 2 Type I** | 🟡 In Progress | Estimated Q3 2026 |
| **HIPAA** | 🟡 Available** | Enterprise tier only; requires assessment |
| **PCI DSS** | 🟡 Partial | Stripe handles card data; we don't store it |

** Additional compliance frameworks available on Enterprise tier with custom assessment.

## Data Handling

| Question | Answer |
|----------|--------|
| Where is my data stored? | On your dedicated VPS (US-based by default). EU hosting available. |
| Who has access? | You control access. No SyStack staff access without explicit authorization. |
| Can I export my data? | Yes — full database dumps available anytime via support. |
| How long is data retained? | Configurable. Default: 7 years for business records, 90 days for logs. |
| What happens if I cancel? | 30-day grace period for data export, then secure deletion. |

---

# Part VI: Getting Started

## Onboarding Process

| Step | What Happens | Timeline |
|------|--------------|----------|
| **1. Discovery** | We discuss your operations, pain points, and goals. | 30-60 min call |
| **2. Proposal** | Custom implementation plan with timeline and pricing. | 24-48 hours |
| **3. Agreement** | Signed SOW and initial payment. | Your pace |
| **4. Deployment** | We provision your SAOS instance. | 10 minutes |
| **5. Configuration** | Integrate your tools (Square, email, calendar, etc.). | 1-3 days |
| **6. Training** | Walkthrough of your system with documentation. | 1 hour |
| **7. Go-Live** | Monitor first week closely, adjust as needed. | Ongoing |

## Support Expectations

| Issue Type | Response Time | Resolution Target |
|------------|--------------|-------------------|
| **Service Down** | Under 30 minutes | 2-4 hours |
| **Feature Broken** | Under 2 hours | Same day |
| **Performance Slow** | Under 4 hours | 24 hours |
| **General Question** | Under 24 hours | 72 hours |
| **Feature Request** | Under 48 hours | Roadmap discussion |

**Critical issues:** Call the emergency line (provided after signup)  
**Non-critical:** support@systack.net or in-app chat

---

# Part VII: Frequently Asked Questions

**Q: Is my data safe with AI processing?**  
A: Yes. For Business and Enterprise tiers, AI runs entirely on your dedicated VPS. No data is sent to third-party AI services. Documents are processed locally and never leave your environment.

**Q: Can I cancel anytime?**  
A: Yes. All plans are month-to-month. Cancel before your renewal date and receive a prorated refund for unused days.

**Q: What if I outgrow my plan?**  
A: Upgrades are instant — we resize your VPS or provision a larger one with zero downtime. Your data transfers seamlessly.

**Q: Do you offer refunds?**  
A: Yes. 30-day money-back guarantee for all plans. If SAOS doesn't measurably improve your operations, we'll refund 100%.

**Q: Can you integrate with our existing tools?**  
A: Almost certainly. We connect with 400+ apps via n8n integrations, custom APIs, and webhook endpoints. During discovery, we'll map your full tool stack.

**Q: What kind of businesses benefit most?**  
A: Businesses with repeatable processes: appointment booking, invoice processing, order management, customer communication. Typically 5-50 employees.

**Q: Is there a trial?**  
A: Yes. 14-day free trial on Professional and Business tiers. No credit card required. Full feature access.

---

# Appendix: Glossary

| Term | Definition |
|------|------------|
| **SAOS** | SyStack Autonomous Operations Stack — our managed operations layer |
| **Agent** | Specialized AI assistant for a specific business function |
| **Workflow** | Automated sequence of steps triggered by an event |
| **n8n** | Open-source workflow automation engine we use |
| **Tailscale** | Zero-configuration VPN for secure remote access |
| **Ollama** | Local AI model server for private document processing |
| **VPS** | Virtual Private Server — your dedicated cloud instance |
| **Webhook** | HTTP callback that notifies your system of external events |
| **OCR** | Optical Character Recognition — reading text from images/scans |

---

*SyStack Service Manual — Client Edition v1.0*
*© 2026 SyStack LLC. All rights reserved.*
*For the latest version: https://systack.net/docs*
*Questions: support@systack.net*
