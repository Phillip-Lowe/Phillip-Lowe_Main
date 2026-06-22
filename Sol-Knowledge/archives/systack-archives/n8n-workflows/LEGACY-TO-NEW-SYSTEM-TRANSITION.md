# Legacy → New System Transition Document

**Date:** 2026-06-01 16:30 CDT
**Author:** SOL
**Status:** ACTIVE

---

## Background

Utopia Deli ordering system is being rebuilt with a new HTML-based pipeline by another fleet agent. The legacy n8n workflows have been imported from backup for reference but are NOT the active production system.

---

## Legacy Workflows (Imported 2026-06-01)

**Status:** ARCHIVED — Do Not Activate
**Purpose:** Reference, rollback safety, node reuse

| Workflow | Legacy Role | New System Replacement |
|----------|-------------|----------------------|
| Utopia-Deli-Simple-Checkout-v4 | Basic order flow | **New HTML pipeline** |
| Utopia Deli — Minimal Checkout | Minimal version | **New HTML pipeline** |
| Utopia Deli — HTML Checkout v3 | Local API checkout | **New HTML pipeline** |
| Utopia Deli — HTML Webhook Checkout v2 | Webhook-based | **New HTML pipeline** |
| Utopia Deli — Full Checkout (Modifiers) | Complex modifiers | **New HTML pipeline** |
| Utopia Deli – Google Forms Intake | Order intake trigger | **New HTML form** |
| Utopia Deli – Menu Form Only | Menu display | **New HTML page** |
| Utopia Deli – Full Order Flow | Sheets logging | **PostgreSQL logging** |
| Order Received | Confirmation | **New notification system** |
| Utopia Deli — Unused Payment Link Deletion | Cleanup | **TBD in new system** |
| Square Refund/Void Confirmation | Financial alerts | **TBD in new system** |
| Disable Payment Link on Complete | Square sync | **TBD in new system** |

### Legacy Support Workflows (Still Relevant)

| Workflow | Status | Notes |
|----------|--------|-------|
| Cart Renderer + Router | DORMANT | May reuse components |
| Contact + Item + Cart | DORMANT | May reuse components |
| Add Another Item | DORMANT | May reuse components |

---

## Active Workflows (Keep Running)

| Workflow | Role | Status |
|----------|------|--------|
| **Error Catcher — Master v2** | System-wide error monitoring | ✅ CONFIGURING |
| **Error Catcher — Master (v1)** | Backup error monitoring | DORMANT |
| Green Systems — Lead Scraper (Little Rock) | Lead generation | DORMANT — Needs PostgreSQL |
| Green Systems — Service Business Lead Scraper | Lead generation | DORMANT — Needs PostgreSQL |
| Systack Lead Scraper — PostgreSQL CRM | CRM pipeline | DORMANT — Needs PostgreSQL |
| Green Systems — Outreach Sequencer | Outreach automation | DORMANT — Needs setup |
| SOL Morning Briefing | Daily operations | DORMANT — Needs email |
| MOD 1 — Streetwear Daily (RSS Aggregator) | Content automation | DORMANT |
| SAOS Lead Capture + Score + Log | SAOS pipeline | ACTIVE (pre-existing) |

---

## Transition Plan

### Phase 1: New System Build (IN PROGRESS)
- **Agent:** Another fleet agent (HTML pipeline)
- **Deliverable:** New HTML-based checkout for Utopia Deli
- **Database:** PostgreSQL (local)
- **No Google Sheets dependency**

### Phase 2: Error Monitoring (CONFIGURING NOW)
- **Error Catcher v2** monitoring all workflows
- **Alerts to:** sol.liaison@gmail.com
- **Scope:** Both legacy (if activated) and new system

### Phase 3: Lead Generation Reactivation (FUTURE)
- Reconnect PostgreSQL CRM
- Reactivate lead scrapers when pipeline needs filling

### Phase 4: Legacy Cleanup (AFTER NEW SYSTEM STABLE)
- Delete or archive legacy deli workflows
- Keep error catcher, lead scrapers, morning briefing

---

## Credential Matrix

| Credential | Legacy Workflows | New System | Priority |
|-----------|------------------|------------|----------|
| Square API | Required | Likely required | TBD with agent |
| PostgreSQL | CRM only | Primary database | CONFIGURE |
| SOL Email | Error alerts | Error alerts | CONFIGURING |
| Google Forms | Intake trigger | Not used | DEPRECATED |
| Google Sheets | Order logging | Not used | DEPRECATED |

---

## Decision Log

| Date | Decision | By | Reason |
|------|----------|-----|--------|
| 2026-06-01 | Legacy workflows imported but not activated | SOL + Green | New system in development |
| 2026-06-01 | No credential setup for legacy workflows | Green | New system replaces them |
| 2026-06-01 | Error Catcher v2 being configured | SOL | System-wide monitoring needed |
| 2026-06-01 | PostgreSQL is local database | Green | No cloud dependency |
| 2026-06-01 | No Google Sheets | Green | Simplified stack |

---

## Files Reference

| File | Purpose |
|------|---------|
| `n8n-workflows/extracted/` | All legacy workflow JSON files |
| `n8n-workflows/error-catcher-master-v2.json` | Enhanced error catcher |
| `memory/plans/PLAN-n8n-RESTORE-2026-06-01.md` | Restore plan |
| `scripts/extract-n8n-workflows.py` | Extraction tool |

---

## Next Actions

1. ✅ Extract workflows from backup
2. ✅ Import all workflows to n8n
3. 🔄 Configure Error Catcher v2 with SOL email
4. ⏳ Wait for new HTML system from other agent
5. ⏳ Test Error Catcher with new system failures
6. ⏳ Reactivate lead scrapers when needed
7. ⏳ Clean up legacy workflows after new system stable

---

*Document created: 2026-06-01 16:30 CDT*
*Updated: 2026-06-01 16:30 CDT*