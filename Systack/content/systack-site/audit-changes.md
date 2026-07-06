# Systack Site Audit & Update Plan
**Date:** 2026-07-06
**Status:** SAOS production-ready, going live soon

---

## AUDIT FINDINGS

### 1. ✅ What's Correct (Don't Touch)
- **Nav structure** — Links to /services, /saos/, /work/, /pricing, /contact — all good
- **Home page** — Messaging is clean, focuses on business pain points
- **SAOS page** — Agent fleet descriptions are current and accurate
- **Utopia Deli case study** — Real, verified, keep as primary proof
- **Footer** — Consistent across pages
- **Contact info** — support@systack.net, (501) 274-6231 — correct

### 2. ⚠️ What's Outdated or Missing (Must Fix)

#### services.html
- **"Workflow Automation (n8n)"** — Shows $1,500 + $149/mo. This is NOT a standalone product anymore. It's included in SAOS/Accelerate.
- **"SAOS Agent Fleet"** — Shows $2,500 + $299/mo. Price is wrong. Should be $299/mo (no setup) for Business Fleet, or clarify it's a SAOS product.
- **Missing:** Invoice Extractor as a standalone service
- **Missing:** Lead Qualification System
- **Missing:** Document Classification
- **Missing:** Any mention of Customer Portal, Command Center, or the SAOS infrastructure

#### pricing.html
- **"What We Handle For You"** section lists "OpenClaw installation" and "SOUL.md configuration" — too technical for prospects, sounds like self-managed
- **"What We Handle"** vs "You Handle" — This is framed for SAOS self-managed, but we also offer done-for-you
- **Missing:** No clear distinction between "We build & manage" (Systack services) vs "You subscribe" (SAOS self-managed)
- **Missing:** No mention of Customer Portal, Command Center, compliance features
- **Missing:** Enterprise compliance / trust center references

#### index.html
- **"AI Assistants" card** — Too vague. Should mention SAOS specifically.
- **"Workflow Automation" card** — Same issue. These are SAOS features now, not standalone.
- **Missing:** Customer Portal demo link (portal.systack.net)
- **Missing:** Command Center mention for enterprise
- **Missing:** Any reference to compliance, security architecture, or enterprise readiness

#### work/index.html
- **"More Coming Soon"** — Still placeholder photography/salon. Should add SAOS deployments.
- **Missing:** SAOS Customer Portal as a case study
- **Missing:** Command Center / enterprise readiness showcase

### 3. ❌ What's WRONG (Must Remove/Fix)

- **services.html** "Workflow Automation (n8n)" at $149/mo — This tier doesn't exist as standalone
- **services.html** "SAOS Agent Fleet" pricing is confusing — $2,500 setup? For SAOS? No.
- **pricing.html** — Mixes managed service pricing with self-managed framing
- **Personal Agent redirect** — Already redirects to /saos/, that's fine

---

## UPDATE PLAN

### Phase 1: services.html (Highest Priority)
1. Replace "Workflow Automation (n8n)" card with actual SAOS service modules
2. Fix SAOS Agent Fleet pricing and description
3. Add Invoice Extractor as standalone service
4. Add Document Processing & Classification
5. Add Lead Qualification
6. Mention Customer Portal + Command Center infrastructure

### Phase 2: pricing.html (Clarity)
1. Restructure: TWO clear sections — "Systack Done-For-You" vs "SAOS Self-Managed"
2. Update "What We Handle" to reflect managed service
3. Add compliance/trust center badges
4. Add Customer Portal screenshot or mention

### Phase 3: index.html (Polish)
1. Update "AI Assistants" → "SAOS AI Agent Fleet"
2. Update "Workflow Automation" → "Business Process Automation"
3. Add Customer Portal link
4. Add enterprise readiness badge

### Phase 4: work/index.html (Proof)
1. Add SAOS Customer Portal case study
2. Update "More Coming Soon" with real pipeline
3. Add metrics from actual deployments

---

## CURRENT PRODUCT LINES (Source of Truth)

### Systack Done-For-You (Custom Build + Manage)
| Service | Price | What It Is |
|---------|-------|-----------|
| Automated Booking System | $2,500 + $299/mo | Custom booking with payments, reminders |
| Online Ordering System | $2,500 + $299/mo | Mobile ordering, Square/Stripe, kitchen sync |
| Invoice Processing | $1,500 + $149/mo | PDF extraction, routing, approval |
| Lead Qualification | $1,500 + $149/mo | Scraping, scoring, morning briefs |
| Document Classification | $1,500 + $149/mo | Auto-categorize, route, archive |

### SAOS Self-Managed (Subscribe & Use)
| Tier | Price | What It Is |
|------|-------|-----------|
| Business Fleet | $299/mo | 7 agents, 16GB VPS, portal access |
| Enterprise Fleet | $799/mo | 10 agents, 32GB, dedicated support |
| Accelerate | $249/mo | Cloud workflows, 10K runs |
| Private | $799/mo | On-premise, air-gapped |
