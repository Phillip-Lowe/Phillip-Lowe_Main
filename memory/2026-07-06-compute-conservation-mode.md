# Session — 2026-07-06 05:52 CDT

## Compute Conservation Mode Activated

**Trigger:** Fleet compute audit — continuous agent burn unjustified for current SAOS stage.

**Decision:** Run agents on-demand, not continuously.

### Why

Ollama Cloud Pro gives 3 concurrent models, ~50× Free usage, rolling reset windows (5-hour sessions, 7-day usage). SAOS is built and validated but has **no paying customer base** yet. Continuous 24/7 fleet burn is waste.

### Actions Taken

1. **Updated `AGENTS.md`** with on-demand fleet schedule
   - Added "Compute Conservation Mode" section
   - Documented weekly compute target (50/20/15/10/3/2 split)
   - Specified background jobs (cron, no agent burn)
   - Changed VALI to local `qwen3.5:9b`

2. **Verified no cloud models running**
   - `ollama ps` — clean, no cloud instances loaded

3. **Confirmed cron jobs remain active**
   - Fleet health monitor — every 15 min (LOKI)
   - Daily backup — 3 AM CDT (LOKI)
   - Backup verification — weekly (LOKI)

4. **Set agent schedule:**
   - **SOL** — Daily (cloud)
   - **ATLAS ↔ CHATTY** — Rotating weekly (cloud)
   - **CODY** — Default rotating (cloud)
   - **PESSI ↔ JURIS** — Event-driven (cloud)
   - **ASSEMBLY** — On-demand architecture (cloud)
   - **DOOBY, LOKI, VALI** — On-demand/local (qwen3.5:9b)
   - **GENI** — On-demand creative (cloud)

### What NOT to Burn Compute On

- ❌ Continuous monitoring (use cron)
- ❌ 24/7 research (burst ATLAS instead)
- ❌ Always-on multi-agent discussions
- ❌ Autonomous planning loops
- ❌ Self-reflection loops
- ❌ GENI unless specific creative task

### Scale-Up Triggers

Activate continuous fleet when:
- 3+ paying SAOS clients
- Active customer support load
- Large deployment pipeline
- 24/7 monitoring requirements

### Review Date

**2026-08-06** (30 days) — reassess if paying customer threshold met.

---

## Files Changed

| File | Change |
|------|--------|
| `AGENTS.md` | Added Compute Conservation Mode section, updated VALI to local, added activation record |
| `memory/2026-07-06-compute-conservation-mode.md` | This log |

