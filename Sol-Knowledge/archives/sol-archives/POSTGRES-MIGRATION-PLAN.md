# Postgres Migration Plan — Systack/Sol/Green/Mod 1

**Created:** 2026-06-08 08:40 CDT
**Status:** Postgres created, not yet connected to workflows
**Reminder:** Scheduled for 2026-06-15 (cron job: `6bd74e5b-e4de-4513-83ab-8394fe0fd8a7`)

---

## What's Already Done

### Postgres Server
- **Host:** localhost:5432
- **User:** systack / `Systack2026!CRM`
- **Database:** `crm` (for invoices)
- **Tables:** `invoices`, `invoice_items`
- **Test insert:** ✅ Success
- **GUI:** TablePlus installed

### What Works NOW (SQLite)
- Invoice pipeline: `invoice_data.db` (124+ records)
- Utopia Deli: `utopia-deli-catering.db`
- n8n internal: `database.sqlite` (13MB, 69 workflows)

---

## Current n8n Workflows (Reality Check)

**Claimed:** 69 workflows
**Actually real:** ~10-12
**Most are:** Test drafts, experiments, duplicates

### Known Real Workflows
1. `Ny4kzzf1bN4NODGn` — Invoice Email Pipeline ✅ Active
2. `rnsOGACoyXh0TXFm` — SAOS Lead Capture + Score + Log
3. `T67LTu32k1xENtzd` — Utopia Deli Catering Lead Scoring
4. `utopia-deli-html-order-v1` — Utopia Deli HTML Order Webhook
5. `h840lgwjPI4vhifu` — Utopia Deli Catering v2
6. `qnsBnLIWQ1Sky68D` — Invoice Parser (older version)
7. `9bzytwXlOJjE1g7T` — SOL Morning Briefing

**Action needed:** Clean up the other ~60 workflows. They're clutter.

---

## Migration Plan (Low Risk)

### Phase 1: Invoice Pipeline (Week 1)
**Risk:** Low — single node change
**Steps:**
1. Update n8n Postgres credential `iVuy7e5WTC05Hqwe`
   - Host: `localhost`
   - Port: `5432`
   - Database: `crm`
   - User: `systack`
   - Password: `Systack2026!CRM`
2. Add Postgres node back to invoice workflow
3. Test with one invoice email
4. If works: switch from SQLite to Postgres logging

### Phase 2: Utopia Deli (Week 2-3)
**Risk:** Medium — existing production system
**Decision:** Keep SQLite for orders (it's working), migrate reporting/history to Postgres
**Steps:**
1. Create `utopia_orders` table in Postgres
2. Add dual-write (SQLite + Postgres) to order webhook
3. Run parallel for 1 week
4. If stable: switch reads to Postgres

### Phase 3: n8n Internal Database (Later)
**Risk:** High — could break all workflows
**Decision:** Don't touch unless SQLite causes real problems
**Trigger:** If n8n starts timing out or corrupting

### Phase 4: Mod 1 / Percy / Green (As Needed)
**Risk:** Low — these aren't running yet
**Action:** Use Postgres from the start for new projects

---

## Why Postgres Over SQLite for Future

| Factor | SQLite | Postgres | Impact |
|--------|--------|----------|--------|
| n8n recommendation | Dev only | Production standard | Stability |
| Concurrent access | File locks | Row-level locking | Performance |
| Multiple projects | Separate files | One server, multiple DBs | Organization |
| JSON support | Text | JSONB with indexing | Invoice data |
| Backup | Copy files | pg_dump, replication | Reliability |
| Dashboard queries | Slow at scale | Optimized | User experience |

---

## What NOT to Do

- ❌ Migrate n8n internal DB to Postgres (too risky, not needed)
- ❌ Migrate working Utopia Deli order system (if it ain't broke...)
- ❌ Spend 30 minutes on complex migration scripts
- ❌ Touch anything during active business hours

---

## Next Action

**Scheduled for 2026-06-15:**
1. Check if Postgres still running
2. Review invoice pipeline — switch to Postgres if ready
3. Clean up unused n8n workflows (keep 10-12 real ones)
4. Decide on Utopia Deli migration

**Credentials file:** `credentials/Green/postgres/crm-connection.txt`

---

## One-Liner Summary

> Postgres is ready. Use it for NEW features. Leave working SQLite alone. Migrate only when you need to.
