# SAOS Customer Journey Map

**SOL 🛰️ | Strategic Systems Operator**
**Version:** 1.0 | **Date:** 2026-07-06

---

## Overview

This document maps every stage of the SAOS customer lifecycle from initial contact through renewal. Each stage includes: who is involved (Green vs SOL/Fleet), what happens, what tools are used, and what the exit criteria are.

---

## Stage 1: Lead Arrives

### Entry Trigger
- Website form submission
- Referral
- Cold outreach response
- Inbound call
- Event/networking

### Process
1. **Lead enters pipeline** → `Systack/sales/pipeline-tracker.md`
2. **ATLAS research** — industry, company size, pain points (if B2B)
3. **Lead qualification** — CHATTY or Green assesses fit
4. **Score:** Hot / Warm / Cold

### Exit Criteria
- Qualified lead with identified need and decision-maker
- OR Disqualified and documented why

### Tools
- Sales pipeline tracker
- ATLAS industry playbooks
- CHATTY outreach templates

### SLA
- First response within 24 hours (business day)

---

## Stage 2: Discovery Call

### Entry Trigger
- Qualified lead agrees to call

### Process
1. **CHATTY sends calendar link** (or Green handles directly)
2. **Green conducts discovery call** using CHATTY discovery script
3. **Key questions asked:**
   - What tools do you currently use?
   - What's your biggest operational pain point?
   - What's your team size and budget?
   - What does "success" look like in 6 months?
   - Who else needs to approve this?
4. **Notes logged** in pipeline tracker
5. **ATLAS builds custom playbook** if niche not covered

### Exit Criteria
- Pain points documented
- Budget range confirmed
- Decision timeline established
- Technical requirements understood

### Tools
- CHATTY discovery scripts
- ATLAS industry playbooks
- Pipeline tracker

### SLA
- Call within 48 hours of lead qualification

---

## Stage 3: Proposal

### Entry Trigger
- Discovery call complete with qualified opportunity

### Process
1. **SOL drafts proposal** using JURIS templates
2. **Proposal includes:**
   - Executive summary
   - Pain point analysis
   - Recommended SAOS tier and services
   - Scope of work
   - Timeline
   - Pricing
   - ROI projections
   - Case studies (if available)
3. **Green reviews and personalizes**
4. **JURIS reviews legal compliance**
5. **CHATTY sends proposal** with follow-up sequence

### Exit Criteria
- Proposal sent with clear next steps
- Follow-up sequence active

### Tools
- JURIS contract templates
- CHATTY proposal email templates
- SAOS pricing sheet

### SLA
- Proposal delivered within 3 business days of discovery call

---

## Stage 4: Agreement

### Entry Trigger
- Client accepts proposal

### Process
1. **JURIS generates agreements:**
   - Master Service Agreement (MSA)
   - Statement of Work (SOW)
   - Data Processing Agreement (DPA) if applicable
2. **Green signs / countersigns**
3. **Stripe checkout link sent** for first payment
4. **Payment confirmed** → `saos_clients` record created
5. **Onboarding initiated** → status = "pending"

### Exit Criteria
- Signed agreement(s) in client file
- First payment received
- Client record in DB
- Onboarding sequence triggered

### Tools
- JURIS MSA/SOW/DPA templates
- Stripe checkout links
- `scripts/onboard_client.py`

### SLA
- Agreements sent within 24 hours of verbal commitment
- Payment link active within 1 hour of agreement

---

## Stage 5: Onboarding

### Entry Trigger
- Payment confirmed
- Client record created

### Process
1. **SOL runs `scripts/onboard_client.py`:**
   - Creates `saos_clients` record
   - Generates temp PIN
   - Creates welcome chat conversation
   - Creates service setup tasks
   - Logs to audit_log
2. **Client receives:**
   - Welcome email (CHATTY template)
   - Portal login instructions
   - Temp PIN + setup instructions
   - ASSEMBLY welcome guide
   - Quick start guide (PDF)
3. **Client completes onboarding wizard:**
   - Sets permanent PIN
   - Enrolls MFA (optional, recommended)
   - Selects services
   - Reviews documentation
4. **VALI runs pre-launch checklist**
5. **Onboarding status = "active"**

### Exit Criteria
- Client logged in with permanent PIN
- MFA enrolled (optional)
- Services selected
- VALI pre-launch checklist complete

### Tools
- `scripts/onboard_client.py`
- Customer Portal (port 8768)
- ASSEMBLY welcome guide
- VALI launch checklists
- CHATTY welcome emails

### SLA
- Onboarding initiated within 2 hours of payment
- Client fully onboarded within 5 business days

---

## Stage 6: Deployment

### Entry Trigger
- Onboarding complete
- VALI pre-launch checklist passed

### Process
1. **SOL provisions environment:**
   - VPS (if needed)
   - DNS records
   - SSL certificates
   - Database setup
   - Service configuration
2. **ASSETS deployed:**
   - Customer Portal
   - Command Center (admin only)
   - n8n workflows
   - Any custom integrations
3. **VALI runs launch checklist**
4. **DNS switched to production**
5. **Services started**
6. **Health checks passing**
7. **Client notified of go-live**
8. **Monitoring activated**

### Exit Criteria
- All services healthy
- Client can log into portal
- First automated workflow triggered
- Monitoring active
- Backup completed

### Tools
- ASSEMBLY deployment kit
- VALI launch checklists
- Fleet health monitor
- Cloudflare Tunnel
- n8n

### SLA
- Deployment within 2 business days of onboarding completion
- Go-live within 48 hours of deployment start

---

## Stage 7: Support

### Entry Trigger
- Go-live complete
- Client is active user

### Process
1. **Client accesses support via:**
   - Portal chat (real-time)
   - Email → support@systack.net
   - Scheduled check-in calls
2. **Support tiers:**
   - **Tier 1 (L0):** Self-service via portal docs, FAQ
   - **Tier 2 (L1):** Automated responses, chatbot
   - **Tier 3 (L2):** SOL/PESSI investigation
   - **Tier 4 (L3):** Green escalation
3. **Incident tracking:**
   - P1-P4 severity
   - Automatic logging to `incident_log`
   - Root cause analysis
   - Post-mortem documentation
4. **Monthly check-ins** (Green or SOL)
5. **Usage metrics review** (SOL)

### Exit Criteria
- Client satisfied (CSAT ≥ 8/10)
- All P1/P2 incidents resolved
- Monthly review completed

### Tools
- Customer Portal chat
- Command Center monitoring
- PESSI incident tracking
- VALI QA standards

### SLA
- P1 response: 1 hour
- P2 response: 4 hours
- P3 response: 1 business day
- P4 response: 2 business days

---

## Stage 8: Renewal

### Entry Trigger
- 30 days before subscription anniversary
- OR Client requests changes

### Process
1. **SOL reviews:**
   - Usage metrics
   - Support ticket history
   - Client satisfaction
   - Upsell opportunities
2. **Green conducts quarterly review call**
3. **SOL prepares renewal proposal:**
   - Same tier continuation
   - OR tier upgrade recommendation
   - OR additional service recommendation
4. **JURIS generates renewal agreement** (if terms change)
5. **Stripe auto-renews** subscription (if no changes)
6. **Client notified** of renewal success

### Exit Criteria
- Subscription renewed OR
- Upgrade/downgrade processed OR
- Graceful offboarding initiated

### Tools
- Stripe subscription management
- JURIS renewal templates
- Usage metrics dashboard
- ATLAS competitive analysis (if at-risk)

### SLA
- Renewal outreach begins 30 days before expiry
- Client decision obtained 7 days before expiry

---

## Stage 9: Offboarding / Churn

### Entry Trigger
- Client cancels
- Payment fails and no resolution
- Contract term ends without renewal

### Process
1. **PESSI analyzes churn reason**
2. **SOL initiates data export:**
   - `POST /api/export/data` → ZIP of all client data
   - Verify completeness
   - SHA-256 checksum
3. **Client receives data package**
4. **SOL deprovisions:**
   - Revoke tokens
   - Disable accounts
   - Archive data (retention period)
   - Remove from monitoring
5. **JURIS archives agreements** per retention policy
6. **ATLAS adds to churn analysis**
7. **Green conducts exit interview** (if possible)

### Exit Criteria
- Client data delivered
- Environment deprovisioned
- Archive complete
- Churn reason documented

### Tools
- Data export API
- `saos_clients` record archived
- JURIS retention policy
- ATLAS churn analysis

### SLA
- Data export within 48 hours of request
- Environment deprovisioned within 7 days

---

## Escalation Matrix

| Stage | Normal | Escalate When | Escalates To |
|-------|--------|---------------|--------------|
| Lead | SOL/CHATTY | Budget >$10K, complex requirements | Green |
| Discovery | Green | Legal/compliance questions | JURIS |
| Proposal | SOL | Custom pricing, multi-year | Green |
| Agreement | JURIS | Negotiation, redlines | Green |
| Onboarding | SOL | Client stuck, technical issues | CODY/ASSEMBLY |
| Deployment | SOL/ASSEMBLY | Infrastructure failure | PESSI |
| Support | SOL | P1 incident, security breach | Green + PESSI |
| Renewal | SOL | At-risk client, competitive threat | Green + ATLAS |
| Offboarding | SOL | Data dispute, legal concern | JURIS + Green |

---

## Metrics Dashboard

See `Systack/operations/weekly-metrics-dashboard.md` for live tracking.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-06 | SOL | Initial customer journey map |

---

*This is a living document. Update as processes evolve.*
