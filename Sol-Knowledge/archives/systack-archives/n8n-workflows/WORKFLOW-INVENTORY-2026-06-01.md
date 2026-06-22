# n8n Workflow Recovery Package — 2026-06-01

## CRITICAL: Error Catcher v2 Created

**File:** `n8n-workflows/error-catcher-master-v2.json`
**Status:** ✅ Ready to import
**Enhancements over v1:**
- Automatic severity classification (CRITICAL for client workflows, HIGH for leads, MEDIUM for others)
- Dual output: Email alert + SQLite audit log
- Structured severity tagging
- Execution ID tracking
- Resolution tracking fields

---

## Complete Workflow Inventory

### Production Workflows (IMPORT THESE)

#### P0 — CRITICAL: Client Revenue
| Workflow | Backup ID | Template File | Status |
|----------|-----------|---------------|--------|
| Error Catcher — Master v2 | NEW | `error-catcher-master-v2.json` | ✅ Ready |
| Utopia-Deli-Simple-Checkout-v4 | 9e21e791 / u3ye4WCL | — | Extract from DB |
| Utopia Deli — Full Checkout | 2073ed99 | — | Extract from DB |
| Utopia Deli — Google Forms Intake | huvnkfK7 | TEMPLATE_PzeO8JaOMYddUVhh | ✅ Template |
| Utopia Deli — HTML Webhook Checkout v2 | 752408b1 | — | Extract from DB |
| Utopia Deli — HTML Checkout v3 | 61c97348 | — | Extract from DB |
| Utopia Deli — Minimal Checkout | 885d9b40 | — | Extract from DB |
| Order Received | cd315760 | TEMPLATE_dxwgUzvDS6gKRPDT | ✅ Template |
| Utopia Deli — Full Order Flow | 1ab90e66 | TEMPLATE_gBItIwXpSWYxHypO | ✅ Template |
| Deli Menu Order Online Confirmation | — | TEMPLATE_C6YvvukSlsF17vAd | ✅ Template |

#### P1 — HIGH: Lead Generation
| Workflow | Backup ID | Template File | Status |
|----------|-----------|---------------|--------|
| Green Systems — Lead Scraper (Little Rock) | B0XmnaAd | — | Extract from DB |
| Green Systems — Service Business Lead Scraper | O5pskm9G | — | Extract from DB |
| Systack Lead Scraper — PostgreSQL CRM | zFYCzAQh | — | Extract from DB |
| Green Systems — Outreach Sequencer | gdQQYtAz | — | Extract from DB |

#### P2 — MEDIUM: Operations
| Workflow | Backup ID | Template File | Status |
|----------|-----------|---------------|--------|
| SOL Morning Briefing | 9bzytwXl | — | Extract from DB |
| Cart Renderer + Router | c6a983d4 | TEMPLATE_4ba2FW9qIxgY9IlX | ✅ Template |
| Contact + Item + Cart | FAGmGNVz | TEMPLATE_oTqq6CSTJMdQVUsn | ✅ Template |
| Add Another Item | DDIlSP2i | TEMPLATE_TVaENeHwGa104htx | ✅ Template |

#### P3 — LOW: Content/Experimental
| Workflow | Backup ID | Template File | Status |
|----------|-----------|---------------|--------|
| MOD 1 — RSS Aggregator v1 | Gob4kpwj | TEMPLATE_3hqhIFImRessX6Xm | ✅ Template |
| MOD 1 — AI Daily News v2 | — | TEMPLATE_KRHXRZ4FfRijMMtT | ✅ Template |
| Daily Check-in Email | — | TEMPLATE_INkEomw9WefBKen8 | ✅ Template |

---

### Support/Admin Workflows (IMPORT IF NEEDED)
| Workflow | Backup ID | Purpose |
|----------|-----------|---------|
| Utopia Deli — Unused Payment Link Deletion | krNiXIrp | Cleanup |
| Square Refund/Void Confirmation | YFeegOW7 | Financial |
| Disable Payment Link on Complete | H7bUyLse | Square sync |

---

### DO NOT IMPORT (Tests/Experiments)
- All `Test-*` workflows (15+ experiments)
- All `My workflow` variants (5 blank/development)
- All `Sol Test*` variants (4 debug flows)
- All `SOL-Test*` variants (2 sqlite tests)
- `SOL-Checkout-Proxy` (development)
- `Build Your First AI Agent` (tutorial)
- Constraint Evaluator workflows (deprecated — 4 variants)

---

## Database Structure

**Backup file:** `n8n-backup-20260530-202509/database.sqlite`
**Schema:** workflow_entity table with columns:
- `id` (varchar 36, PK)
- `name` (varchar 128)
- `active` (boolean)
- `nodes` (text — JSON node definitions)
- `connections` (text — JSON connection map)
- `settings` (text — JSON settings)
- `staticData` (text)
- `versionId` (varchar 36)
- `triggerCount` (integer)
- `meta` (text)
- `createdAt` / `updatedAt` (datetime)
- `isArchived` (boolean)
- `versionCounter` (integer)
- `description` (text)
- `activeVersionId` (varchar 36)

**Note:** Full workflow JSON must be reconstructed from `nodes` + `connections` + `settings` columns.

---

## Import Strategy

### Phase 1: Error Catcher (5 minutes)
1. Import `error-catcher-master-v2.json`
2. Configure email credentials (SOL email)
3. Create SQLite error_logs table
4. Set as instance error workflow in n8n settings
5. Test with deliberate failure

### Phase 2: Utopia Deli (30 minutes)
1. Extract checkout workflows from backup DB
2. Reconstruct full JSON (nodes + connections + settings)
3. Import one by one, test each
4. Activate after verification

### Phase 3: Lead Generation (15 minutes)
1. Import lead scraper workflows
2. Reconnect PostgreSQL CRM credentials
3. Test data flow

### Phase 4: Operations (10 minutes)
1. Import SOL Morning Briefing
2. Import support/admin workflows
3. Test notification channels

---

## Next Actions

1. **ASSEMBLY or CODY:** Extract workflows from SQLite backup using Python script
2. **SOL:** Coordinate import sequence, verify each workflow post-import
3. **Green:** Re-enter credentials for Square, PostgreSQL, email when prompted

---

*Inventory created: 2026-06-01 16:18 CDT*
*Ready for import execution*