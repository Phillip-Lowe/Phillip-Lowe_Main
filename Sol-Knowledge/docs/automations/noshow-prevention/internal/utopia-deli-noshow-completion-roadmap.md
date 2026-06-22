# Utopia Deli — No-Show Prevention System
## Completion Roadmap

**Document ID:** `UD-NSHOW-ROADMAP-001`  
**Version:** 1.0  
**Status:** Internal — Systack Only  
**Source System:** Utopia Deli (Partial — Phase 1 complete)  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Primary | Deep Burgundy | `#590B3F` |
| Primary Light | Burgundy Light | `#7a1a55` |
| Accent | Rust Red | `#AF3D4B` |
| Accent Hover | Rust Light | `#c44d5b` |
| Secondary | Purple | `#754681` |
| Gold | Warm Gold | `#D59F5C` |
| Gold Light | Cream | `#f5e6d0` |
| Background | Off-White | `#FBFCFE` |
| Card | White | `#FFFFFF` |
| Text | Dark Gray | `#1F2937` |
| Text Light | Medium Gray | `#6B7280` |
| Border | Light Gray | `#E5E7EB` |
| Success | Green | `#22c55e` |
| Error | Red | `#dc2626` |

---

## 1. Current Status Summary

| Component | Status |
|-----------|--------|
| Deposit collection via Square | ✅ Complete |
| Booking → database insert | ✅ Complete |
| Confirmation email with token | ✅ Complete |
| Confirmation webhook handler | ✅ Complete |
| T-24h reminder scheduler | ✅ Complete |
| T-2h reminder scheduler | 📋 Built, needs test |
| Auto-release unconfirmed slots | 🚧 NOT BUILT |
| Frontend booking form | 🚧 NOT BUILT |
| Test/prod environment separation | 🚧 NOT BUILT |

**Overall:** 5/9 components complete (56%)

---

## 2. Phase Breakdown

### Phase 1: Deposit + Confirmation Core ✅ COMPLETE

**Completed:** 2026-06-03 to 2026-06-11

| Task | Status |
|------|--------|
| Square deposit integration | ✅ |
| Database schema (`bookings` table) | ✅ |
| Booking INSERT workflow | ✅ |
| Confirmation email with token link | ✅ |
| Token validation webhook | ✅ |

---

### Phase 2: Reminder System 🚧 IN PROGRESS

**Started:** 2026-06-11

| Task | Status | Est. Effort |
|------|--------|-------------|
| T-24h reminder scheduler | ✅ Complete | — |
| T-2h reminder scheduler | 📋 Needs test | 1 hour |
| Reminder email templates | ✅ Complete | — |
| Confirm/Cancel button handling | ✅ Complete | — |

**Remaining work:** Test T-2h reminder with real booking window (set booking 1h 55m out, verify reminder fires).

---

### Phase 3: Auto-Release + Waitlist 📋 QUEUED

**Not started.**

| Task | Est. Effort | Dependencies |
|------|-------------|--------------|
| Auto-release logic (T-30min check) | 3 hours | Phase 2 complete |
| Slot status update on release | 1 hour | Auto-release logic |
| Waitlist notification (if exists) | 2 hours | Waitlist system |
| Follow-up flag for unconfirmed | 1 hour | Auto-release logic |

**Total Phase 3 effort:** ~7 hours

---

### Phase 4: Frontend Booking Form 📋 QUEUED

**Not started.**

| Task | Est. Effort | Dependencies |
|------|-------------|--------------|
| Test booking form (`/test-book`) | 2 hours | None |
| Production booking form (`/book`) | 3 hours | Test form validated |
| Deposit notice UI | 1 hour | Square integration |
| Test/prod workflow separation | 2 hours | Both forms built |

**Total Phase 4 effort:** ~8 hours

---

### Phase 5: Production Hardening 📋 QUEUED

**Not started.**

| Task | Est. Effort | Dependencies |
|------|-------------|--------------|
| Move cron from 5-min test to real schedule | 1 hour | All phases tested |
| Production database migration | 2 hours | Test data separated |
| Monitoring + alerting setup | 2 hours | Production live |
| Client handoff documentation | 2 hours | All phases complete |

**Total Phase 5 effort:** ~7 hours

---

## 3. Timeline Estimate

| Phase | Tasks | Est. Hours | Target |
|-------|-------|------------|--------|
| Phase 2 (complete reminders) | 1 | 1 | Week 1 |
| Phase 3 (auto-release) | 4 | 7 | Week 1–2 |
| Phase 4 (frontend) | 4 | 8 | Week 2–3 |
| Phase 5 (harden) | 4 | 7 | Week 3–4 |
| **Total** | **13** | **~23 hours** | **~4 weeks** |

---

## 4. Immediate Next Actions

1. **Test T-2h reminder** — set test booking for 1h 55m window, verify email fires
2. **Build auto-release** — Code node checking confirmation status at T-30min
3. **Build test booking form** — `systack.net/test-book` with deposit flow
4. **Separate test/prod** — `systack_test` DB + demo workflows

---

## 5. Dependencies

| Dependency | Needed For | Status |
|------------|-----------|--------|
| Square API credential | Deposit collection | ✅ Configured |
| PostgreSQL (localhost) | Booking storage | ✅ Running |
| Gmail SMTP | Email delivery | ✅ Working |
| Waitlist system | Auto-release notification | ❌ Not built |
| Frontend hosting (systack.net) | Booking form | ✅ Available |

---

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| T-2h timing unreliable | Medium | Medium | Test with multiple windows |
| Auto-release releases wrong slot | Low | High | Thorough testing, confirmation check |
| Customers ignore reminders | Medium | Medium | SMS fallback (Phase 6 enhancement) |
| Deposit conversion drop | Low | Medium | A/B test deposit percentages |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
