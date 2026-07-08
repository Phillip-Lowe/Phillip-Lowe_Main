# SAOS Distribution Pipeline Plan
**Created:** 2026-07-08 00:40 CDT
**Author:** Green (strategic directive) + SOL (assessment)
**Status:** Approved framework — prioritization in progress

---

## The Shift

Stop thinking like an automation builder. Start thinking like an operator.

- Businesses don't buy "we build workflows"
- Businesses buy "we solve expensive problems"
- The bottleneck is **distribution**, not product capability

---

## 10 Acquisition Channels (Ranked by Priority for SyStack)

### Tier 1 — Build First (Highest Leverage)

| # | Channel | What It Is | What We Have | What We Need | Est. Time to First Customer |
|---|---------|-----------|-------------|-------------|---------------------------|
| 1 | **Free Automation Audit** | Lead magnet: business submits website/email/industry → SAOS generates a report showing lost revenue opportunities → book strategy call | SAOS dashboard API, lead capture webhook, n8n workflows, discovery.html | Audit form page, audit generation logic, report template, booking CTA | 2-3 days build |
| 2 | **Strategic Partnerships** | Recruit agencies/web designers/MSPs/accountants as resellers at 20% recurring commission | Partner outreach templates in asset library | Partner program page, reseller agreement, commission tracking | 3-5 days build |
| 3 | **Productized Vertical Offer** | Sell "Restaurant OS" / "Service Business OS" not "automation" | Industry playbooks (10 total), case studies, Utopia Deli as proof | Vertical landing pages, packaged pricing per industry | 2-3 days build |

### Tier 2 — Build Second (Medium Leverage)

| # | Channel | What It Is | What We Have | What We Need | Est. Time |
|---|---------|-----------|-------------|-------------|-----------|
| 4 | **Website Automation Score** | 2-minute quiz → score → recommendations → book consultation | discovery.html (8-step questionnaire exists) | Score calculation logic, results page, shareable URL | 1-2 days |
| 5 | **Local Authority Pipeline** | Workshops at Chambers of Commerce, SBDCs, networking groups | Nothing yet | Slide deck, workshop outline, outreach script to event organizers | 3-5 days |
| 6 | **Referral Engine** | Automated referral asks after successful delivery, 1 free month per referral | SAOS dashboard has chat + task system | Referral tracking in dashboard, automated ask workflow, tracking page | 2-3 days |

### Tier 3 — Build Third (Compounding / Long-term)

| # | Channel | What It Is | What We Have | What We Need | Est. Time |
|---|---------|-----------|-------------|-------------|-----------|
| 7 | **Content Engine** | Practical articles ("How a Restaurant Lost $37K From Missed Follow-Ups") → free audit CTA | green-content-calendar skill, blog infrastructure possible | 5-10 articles, blog section on systack.net, SEO basics | 1-2 weeks |
| 8 | **SaaS Trial Funnel** | SAOS Lite free tier → upgrade to paid | Full dashboard already built | Free tier limits, signup flow, downgrade logic | 1-2 weeks |
| 9 | **Marketplace Funnel** | Sell industry-specific packages (Roofing OS, Restaurant OS, Medical OS) | Industry playbooks exist | Per-industry landing pages, industry-specific demo instances | 1-2 weeks |
| 10 | **Existing Customer Expansion** | Upsell current customers through the value ladder | Utopia Deli relationship | Upsell playbook, expansion workflow | Ongoing |

### Cold Email (Already Built)

| # | Channel | Status | Notes |
|---|---------|--------|-------|
| 0 | **Cold Email Sequence** | ✅ Ready (20 prospects loaded) | Activate Tuesday 9 AM. Low per-prospect but compounds at scale. |

---

## What I Would Do First (Green's Directive)

### Month 1: Build the 3 highest-leverage channels

**Week 1-2:**
1. **Free Automation Audit** — lead magnet page + audit generation + report
2. **Partner Program** — partner page + outreach to 10-20 agencies/MSPs
3. **One Vertical Package** — "Service Business OS" landing page with packaged offer

**Week 3-4:**
4. Launch Chamber of Commerce outreach (workshops)
5. Activate cold email (20 prospects)
6. Start referral program

### Month 2: Scale what works

- Content engine (5 articles)
- SAOS Lite trial
- Second vertical package

### Month 3: Compound

- Case studies from first customers
- Authority content
- Scale prospect list to 200+

---

## Validation

**Highest leverage path for SyStack right now:**
Partner Program + Automation Audit + 1 Verticalized Offer

These three together will likely produce customers faster than building more technology, because the current bottleneck is distribution, not product capability.

---

## Infrastructure We Already Have (Don't Rebuild)

| Asset | Location | Reusable For |
|-------|----------|-------------|
| SAOS Customer Portal | port 8768, api.py | Audit delivery, partner dashboard |
| Command Center | port 8770 | Internal pipeline management |
| Lead Capture Webhook | n8n workflow | Audit form submission → CRM |
| Discovery Questionnaire | discovery.html | Pre-call qualification |
| n8n Email Workflows | Cold Email Sequence + Pipeline Sync | Partner outreach, referral emails |
| SMTP Credential | support@systack.net (verified) | All outbound email |
| Cloudflare Tunnels | portal.systack.net, command.systack.net | Public-facing pages |
| Industry Playbooks (10) | Systack/sales/ | Vertical landing page content |
| Case Studies | Systack/sales/case-studies.md | Audit reports, partner materials |
| Outreach Asset Library | 625 lines of templates | Partner outreach, workshop follow-up |
| Target Account Database | 20 prospects | Partner prospecting, warm intros |
| Utopia Deli Email Campaign | Live in n8n | Proof of concept, case study material |

---

*This plan shifts SyStack from "what can we build?" to "who can we help and how do they find us?"*