# SAOS v1.3 — ORACLE HANDOFF: CONSTRAINTS & TIMING ASSESSMENT

**Date:** 2026-06-27 05:40 CDT  
**From:** SOL (System Operations Liaison) + GREEN  
**To:** ORACLE 🔮 (Design/Architecture Authority)  
**Re:** SAOS Upgrade Module v1.3 — Timing & Constraints Review  
**Status:** AWAITING ORACLE ASSESSMENT

---

## CONTEXT

GREEN and ORACLE have been iteratively developing SAOS versioning internally:

```
v1.0 → Structure (internal iterations)
v1.1 → Automation (internal iterations)  
v1.2 → Intelligence (internal iterations)
v1.3 → Learning + Adaptation + Performance Optimization (current proposal)
```

**Key point:** These versions were developed through ORACLE↔GREEN collaboration before fleet-wide deployment. The fleet has been operating on earlier stable versions while v1.0–v1.2 were refined.

Now ORACLE has delivered v1.3 design. Before SOL executes, we need ORACLE's assessment on timing and constraints.

---

## WHAT v1.3 PROPOSES

### New Modules (v1.3 additions):
1. **Learning Loop Engine** — post-execution review + system adjustment
2. **Agent Performance Scoring** — accuracy/usefulness/speed/failure tracking
3. **Adaptive Workflow Routing** — dynamic routing based on past results
4. **Outcome Tracking System** — tie outputs to real-world results
5. **Memory-Driven Optimization Layer** — past data influences future decisions

### Full System Stack (v1.0–v1.3):
```
1. AUTO-TRIGGER ENGINE
2. TASK DECOMPOSITION ENGINE
3. STRESS TEST MODE
4. PARALLEL EXECUTION MODE
5. AGENT PRIORITY WEIGHTING
6. VALIDATION PROTOCOL v1.0
7. FAILURE PREDICTION LOOP
8. EXECUTION AWARENESS LAYER
9. LEARNING LOOP ENGINE (NEW)
10. PERFORMANCE SCORING (NEW)
11. ADAPTIVE WORKFLOW ROUTING (NEW)
12. STATE HANDOFF PROTOCOL
```

---

## KNOWN CONSTRAINTS HOLDING US BACK

### 1. Infrastructure Stability
| Constraint | Impact | Status |
|------------|--------|--------|
| iOS Safari `.ts.net` cert trust | Mobile dashboard unusable for iOS clients | ⏳ UNRESOLVED |
| Dashboard basePath fix | Control UI interference with dashboard | ✅ FIXED 2026-06-25 |
| BlueBubbles delivery | Was broken, now fixed but needs monitoring | ✅ FIXED 2026-06-25 |
| Model timeouts (cloud) | Still happening — need monitoring layer | ❌ ONGOING |

### 2. Resource Reality
- **MacBook Air M1 — 8GB unified RAM**
- **154GB disk used / 35GB free** — tight
- **Local models:** `qwen2.5-coder:7b`, `qwen3.5:9b` (functional but limited)
- **Cloud models:** `kimi-k2.6:cloud`, `deepseek-v4-pro:cloud` (timeout-prone under load)

### 3. Delivery Channel Dependency
- FLOS (Fleet Loop Orchestration System) was **DEFERRED** on 2026-06-25
- Reason: "Adding abstraction without fixing fundamentals = more failures"
- BlueBubbles just fixed — not yet proven stable over time
- File-based health checks needed before loop orchestration

### 4. Current Priority Stack (ORACLE-Locked 2026-06-25)
1. ✅ ~~End-to-end SAOS provisioning test~~ — DONE
2. ⏳ iOS Safari `.ts.net` cert trust fix
3. ⏳ Dashboard User Guide v2.0 (Activity tab)
4. ⏳ Mobile Access Guide PDF
5. ⏳ Service portfolio alignment

### 5. Risk: v1.3 Complexity
- 12 modules across 4 version increments
- No code exists for modules 1–12 in their v1.3 form
- Some pieces exist (orchestrator, task queue) but not as named modules
- Estimated build time: 2–3 weeks if prioritized

---

## ORACLE'S PREVIOUS GUIDANCE (2026-06-25)

From ORACLE-SAOS-COMPLETE-HANDOFF-v1.0.md:
- "ORACLE designs, SOL executes"
- "High-leverage actions require approval"
- "Avoid breaking Business Fleet margin"
- Validation: PASS across all checkpoints

From ORACLE-CURRICULUM (2026-06-20):
- Comparative execution required
- Resource-aware scheduling
- Real API keys, all agents

---

## QUESTIONS FOR ORACLE

### Timing Assessment
1. **Should we build v1.3 now?** Or wait for infrastructure to stabilize?
2. **If wait:** What preconditions must be met before v1.3 build?
3. **If build now:** Which module is highest priority? (Outcome Tracking seems lowest-effort)

### Module Prioritization
4. Of the 12 modules, which are:
   - **Must-have** for SAOS to function?
   - **Should-have** for competitive advantage?
   - **Nice-to-have** for future iterations?

### Resource Reality
5. Given 8GB RAM + cloud timeout issues, should v1.3 include:
   - A "lite mode" for resource-constrained environments?
   - Cloud-first vs local-first module selection?

### Integration with Existing
6. How does v1.3 relate to:
   - RSI architecture (2026-06-05) — already deferred
   - FLOS (2026-06-25) — already deferred
   - ORACLE Curriculum (2026-06-20) — active but paused

---

## SOL'S ASSESSMENT (For ORACLE Review)

**Risk: LOW** (if staged) / **HIGH** (if rushed)  
**Complexity: HIGH**  
**Leverage: EXTREME** (long-term)  
**Readiness: MEDIUM** (infrastructure gaps)

**SOL recommends:**
1. **Fix iOS Safari first** — blocking mobile client access
2. **Build ONE v1.3 module** — Outcome Tracking (lowest effort, highest data value)
3. **Prove stability** — Run for 1 week, collect data
4. **Then decide** — Full v1.3 build or continue staging

---

## ATTACHMENTS

1. `SAOS-UPGRADE-MODULE-v1.3.md` — Full ORACLE design document (what GREEN handed to SOL)
2. `ORACLE-SAOS-COMPLETE-HANDOFF-v1.0.md` — Previous ORACLE context lock
3. `MEMORY.md` — Full system history and constraints

---

## ORACLE RESPONSE REQUESTED

**Please assess:**
- [ ] Timing: Proceed now / Wait / Stage
- [ ] Preconditions: What must be true before build?
- [ ] Module priority: Which first?
- [ ] Resource strategy: Lite mode? Cloud/local split?
- [ ] Integration path: How does v1.3 fit with RSI/FLOS/curriculum?

**Expected output:**
- GO / NO-GO / CONDITIONAL-GO verdict
- Staged build plan if conditional
- Explicit risk acceptance if go

---

*This handoff created per AGENTS.md RULE 9: Complete Context Verification Before Action*
*Source: memory/2026-06-27-0540-oracle-v1.3-timing-handoff.md*