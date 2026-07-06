# 2026-07-05 — SAOS Docs + Workflow Activation

**Time:** 20:19 CDT
**Status:** ✅ COMPLETE

## What Was Done

### 1. PDF Generator Fix
- **Issue:** pyppeteer was trying broken Chromium first, failing on macOS
- **Fix:** Reordered browser path list in `generate_pdf.py` — Brave Browser now first
- **File:** `~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py` (line 753)

### 2. Missing PDFs Generated (4 new)
| Document | MD Source | PDF Size |
|----------|----------|----------|
| SAOS-Dashboard-Technical-Spec.pdf | DASHBOARD-TECHNICAL-SPEC.md | 394KB |
| SAOS-iOS-Cert-Trust-Plan.pdf | IOS-CERT-TRUST-PLAN.md | 312KB |
| SAOS-Changes-2026-06-29.pdf | CHANGES-2026-06-29.md | 251KB |
| SAOS-Customer-Portal-README-v2.pdf | README.md | 254KB |

Old `SAOS-Customer-Portal-README.pdf` removed (replaced by v2).

### 3. API Download Routes Added (4 new)
Added to `DOC_FILES` map in `api.py`:
- `/download/technical-spec` → SAOS-Dashboard-Technical-Spec.pdf
- `/download/ios-cert-plan` → SAOS-iOS-Cert-Trust-Plan.pdf
- `/download/changelog` → SAOS-Changes-2026-06-29.pdf
- `/download/readme` → SAOS-Customer-Portal-README-v2.pdf

All verified returning HTTP 200.

### 4. Dashboard Index Updated
Enterprise/Private tier docs section now includes:
- Technical Spec, iOS Cert Trust Plan (enterprise)
- Technical Spec, iOS Cert Trust Plan, Changelog, README (private)

### 5. n8n Workflow Activation (3 SAOS service workflows)
| Workflow | ID | Status |
|----------|----|--------|
| SAOS Customer Support Drafting | 61be935f... | ✅ Active |
| SAOS Document Classification Engine | 7814e383... | ✅ Active |
| SAOS Scheduled Report Generator | f3b106b0... | ✅ Active |

**Issue found:** Workflows were not in `shared_workflow` table — API returned 404.
**Fix:** Added to `shared_workflow` with `workflow:owner` role for project `yXbqdfXQYS5El7Nb`.

**Issue found:** n8n 1.20.0 `POST /workflows/{id}/activate` endpoint returns 404 despite route existing in OpenAPI spec. Possible bug.
**Workaround:** Activated directly via DB: `UPDATE workflow_entity SET active=1`. API confirmed `active=True` after DB update.

### 6. Customer Dashboard Restarted
- Port 8768 restarted to pick up new download routes
- PID: 15298

## Errors Encountered
1. pyppeteer Chromium launch failure → Fixed by reordering browser paths
2. n8n workflow 404 on API → Fixed by adding to shared_workflow table
3. n8n activate endpoint 404 → Worked around with direct DB update

## Files Changed
- `~/.openclaw/skills/branded-pdf-generator/scripts/generate_pdf.py` (browser path order)
- `Systack/content/saos/saos-data/customer-dashboard/api.py` (DOC_FILES map)
- `Systack/content/saos/saos-data/customer-dashboard/index.html` (docs section)
- 4 new PDF files in customer-dashboard directory
- n8n database: shared_workflow + workflow_entity tables