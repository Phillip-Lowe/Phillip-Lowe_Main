# TODO — Current State (Updated 2026-07-08 03:33 CDT)

---

## 🔴 HIGH PRIORITY — Next Actions

### 1. Partner Program Page
**Status:** Not started
**File:** `systack.net/partners`
**Needs:** 20% recurring commission pitch, reseller agreement, onboarding flow
**Impact:** Referral channel for recurring revenue

### 2. Service Business OS Vertical Offer
**Status:** Not started
**Price:** $499 setup + $299/mo
**Outcome:** "Never miss another customer inquiry"
**Impact:** Packaged vertical landing page for specific niche

### 3. Finish Dashboard "Try It" UI
**Status:** API endpoints ready, frontend pending
**Endpoints:** `try-lead-score`, `try-doc-classify`
**Impact:** Live demos convert visitors to leads

### 4. Fix Onboarding Wizard
**Status:** Has duplicate `finishOnboarding` assignment
**Impact:** Clean first-time user experience

### 5. Scale Cold Email to 100+ Prospects
**Status:** 20 active, need 80 more
**Impact:** More at-bats = more meetings

---

## ✅ COMPLETED — SAOS Enterprise Readiness

All Oracle priorities P1-P5 complete. Command Center v2.0 live. 65/65 tests passing. 16 PDFs generated. Full endpoint test suite. Client onboarding script verified. Daily backup cron active.

### ✅ ALSO COMPLETED — Distribution Pipeline (2026-07-08)
- Invoice parser fixed (all fields extracting correctly)
- Free Automation Audit lead magnet live at systack.net/audit/
- Cold email workflow activated (20 prospects, Tuesday 9 AM CT)
- Customer dashboard enhanced (process flows, Try It demos, pricing banner, onboarding wizard)
- n8n database cleaned (770 orphaned records removed)
- Git committed & pushed

## ✅ COMPLETED — Fleet Sales-Validation Sprint

All 8 fleet agents delivered:
- ATLAS: Prospect research (5 niches, 27KB)
- CHATTY: Outreach assets (emails, SMS, LinkedIn, scripts, 409 lines)
- JURIS: Business infrastructure pack (6 legal docs, 16.9KB)
- PESSI: Pre-mortem (12 risks, 10 mitigations, 14.5KB)
- VALI: Acceptance standards (PASS/FAIL for 6 services, 382 lines)
- CODY: Internal standards (onboarding, deployment, DB, credentials, backup, docs, 11.9KB)
- ASSEMBLY: Standard launch kit (welcome, implementation, FAQ, support, training, pricing, 18.9KB)
- SOL: Operating system (lead→renewal, 10 sections, 21.5KB)

## ✅ COMPLETED — Sales Pipeline Tracker

`Systack/sales/pipeline-tracker.md` — operational CRM for tracking leads through the pipeline.

## ✅ COMPLETED — Fleet Health Monitor

`Systack/operations/fleet-health-check.py` — 15-minute cron, iMessage alerts on critical service failure.

---

## 🟡 MEDIUM PRIORITY — Backlog

### 6. Referral Engine
**Status:** Conceptual
**Trigger:** After successful service delivery
**Reward:** 1 free month per referral
**Impact:** Organic growth via happy customers

### 7. Monitoring Dashboard Enhancement
- Agent health metrics in Command Center
- Task queue depth visualization
- Error rate tracking over time
- Response time percentiles

### 8. Client Onboarding Flow Testing
- Script works (verified 2026-07-06)
- Needs real-world test with actual client
- Email delivery of credentials
- 15-day implementation timeline validation

### 9. Systack Website Updates
- Service portfolio alignment with SAOS tiers
- Case studies / testimonials section
- Blog / content section
- SEO optimization

### 10. Training Video Production
- 6 video outlines ready (in Standard Launch Kit)
- Needs screen recording, editing, upload
- YouTube unlisted or Loom

---

## ⏸️ BLOCKED — Waiting on Green

| Item | Blocked By | Impact |
|------|-----------|--------|
| First outreach batch | Target approval + email setup | Revenue |
| Partner program | Decision to build page | Referral revenue |
| Service Business OS page | Decision to verticalize | Niche revenue |
| Stripe billing | Stripe account setup | Automated revenue |

---

## 🟢 LOW PRIORITY — Nice to Have

### 11. AI Video Ad Service
- "There's a [Business] for that" campaign series
- $500-1500/video, $2-5K/month retainer
- Concept validated, needs first client

### 12. Voice Agent (SOL Talk Mode)
- Research complete, architecture defined
- Blocked by: Custom OpenClaw provider adapter
- Alternative: Voicebox MCP integration

### 13. Utopia Deli Enhancements
- Weekly menu rotation automation
- Customer notification system
- **Note:** Do not touch deli repo without explicit permission