# ORACLE Strategic Thesis Review — SYSTACK-NOSHOW-30D-001

**Status:** COMPLETE_OR_SUPERSEDED_BY_GREEN_CANONICAL_PACKET
**Disposition:** This review was produced before GREEN supplied the canonical initiative packet. The strategic insights are preserved as evidence, but the canonical mission charter and packet in `memory/2026-08-02-systack-noshow-30d-001.md` and `initiatives/SYSTACK-NOSHOW-30D-001.md` are authoritative.

# SyStack No-Show Reduction Pilot — Strategic Thesis

**Mission ID:** SYSTACK-NOSHOW-30D-001  
**Status:** EVIDENCE_COLLECTION / THESIS_FORMALIZED  
**Date:** 2026-08-02  
**Reference:** `memory/2026-08-02-builder-level-assessment.md`; `memory/2026-08-02-systack-noshow-30d-001.md`; `templates/one-page-initiative-packet-SYSTACK-NOSHOW-30D-001.md`

---

## 1. Falsifiable Prediction

> For owner-operated service businesses with scheduled appointments, a 30-day SyStack-managed confirmation-and-recovery intervention will reduce the **preventable no-show rate** by at least 20% relative to the measured baseline, because the dominant failure mode is not reminder absence but **response-state ambiguity**: customers who neither confirm, cancel, nor reschedule leave openings that staff do not have time to backfill. Resolving that ambiguity before the appointment window closes is the highest-leverage intervention.

### What would falsify this
- Baseline preventable no-show rate is below 5% (too little headroom for a 20% relative reduction).
- Customers respond to reminders but still no-show at the same rate (problem is not confirmation-state ambiguity).
- Businesses cannot or will not provide reliable appointment-outcome data (baseline cannot be established).
- Prospects consistently value lead generation or new bookings more than recovering existing appointments (pain hierarchy differs from hypothesis).

---

## 2. Recommended First Subsegment: Barbershops and Hair Salons

### Why this subsegment first
1. **High appointment density with predictable slot economics.** A single chair or station generates revenue in discrete, identifiable slots. One missed appointment is immediately visible as lost revenue and idle staff time.
2. **Owner-operated, local decision making.** The owner is typically on-site and can approve a pilot quickly without enterprise procurement, legal review, or IT gatekeepers.
3. **Existing booking habits and data availability.** Most use consumer booking platforms (Square, Fresha, Schedulicity, Booksy) or simple calendars and can export or share appointment data without custom integration.
4. **Visible, repeatable problem.** The no-show rate in this segment is widely reported as 10–20%, high enough to matter but not so high that it implies a deeper service-quality issue.
5. **Fast feedback loop.** Daily appointment volume means a 30-day pilot produces enough events to measure directionally, even if statistical power is limited.

### Why not the others first
- **Consultants / solo professionals:** Lower appointment volume, more variable slot value, and the buyer is also the operator — harder to separate emotional attachment from measured outcomes.
- **Scheduled-service trades (HVAC, plumbing, etc.):** Appointments are often larger, higher-variance jobs with dispatch complexity; the no-show pattern is different and integration cost is higher.
- **Beauty professionals as a broad category:** Includes mobile, rental-booth, and spa structures that fragment the booking data source; better to test after proving the narrower barbershop/salon pattern.

---

## 3. Three Risks That Could Invalidate the Mission

### Risk 1: The economic pain is too small to motivate payment
- **What it means:** Even if no-shows are annoying, the monthly dollar loss may not justify a paid service to a cost-conscious small business.
- **Early signal:** Prospects agree the problem exists but refuse to pay for a pilot, ask for a free trial with no commitment, or redirect the conversation to cheaper tools.
- **Evidence to watch:** Average appointment value × monthly no-show count vs. proposed pilot price.
- **Threshold:** Pilot cost should be recoverable by protecting 2–3 appointments per month.

### Risk 2: Existing booking platforms already solve this adequately
- **What it means:** Square, Fresha, Booksy, or other incumbent platforms already provide reminders, confirmations, and cancellation flows that are "good enough" for the segment.
- **Early signal:** Prospects say they already use platform reminders and do not see a gap; interviews repeatedly surface "we use [platform] for that."
- **Evidence to watch:** What percentage of target businesses are on a platform with robust two-way confirmation / release logic; whether they are still manually following up despite the platform.
- **Threshold:** If >50% of interviewed prospects report no manual follow-up and no material loss, the differentiator is weak.

### Risk 3: Businesses cannot provide reliable outcome data
- **What it means:** Without a credible baseline and consistent outcome recording, the pilot cannot prove or disprove the prediction.
- **Early signal:** Owners cannot quote their no-show rate, do not track whether no-shows were preventable, or record appointment outcomes inconsistently.
- **Evidence to watch:** Percentage of prospects who can supply 30 days of historical appointment data with status (showed / no-show / cancelled / rescheduled) and average appointment value.
- **Threshold:** At least one willing pilot business must be able to provide baseline data and commit to recording outcomes during the test.

---

## 4. Existing SyStack Components: Demonstrate vs. Blocked-Pending-Evidence

### Use for demonstrations and discovery
These components are already live and should be shown to prospects to make the pilot concrete, but demonstrations are not implementation commitments:

| Component | Current State | Demonstration Use |
|---|---|---|
| `systack_noshow` Postgres DB | ✅ Exists with `bookings` and `booking_settings` tables | Show that appointment state is recorded and isolated by customer. |
| Booking creation workflow | ✅ Live with confirmation token | Show intake + immediate confirmation flow. |
| Confirmation page / email | ✅ Implemented with branded template | Show customer-facing confirmation experience. |
| T-24h reminder scheduler | ✅ Active in n8n | Show automated reminder cadence. |
| T-2h urgent reminder | ✅ Active, flags `at_risk` | Show escalation for unconfirmed appointments. |
| Booking dashboard (port 8772) | ✅ Live, Tailscale-only, PIN-locked | Show owner-facing status view (during discovery/demo only). |

### Remain blocked until evidence
Do not build, configure, or promise these until the evidence gate is satisfied and a specific pilot business is signed:

| Component | Status | Why It Stays Blocked |
|---|---|---|
| Auto-release unconfirmed slots | 📋 Queued | Timing and policy depend on the specific business's refill behavior and booking platform. |
| Smart rebooking engine | 📋 Queued | Requires validated demand for automated rescheduling; adds complexity and maintenance. |
| Customer dashboard | ❌ Excluded | Pilot offer explicitly excludes a new dashboard unless a live customer proves it is required. |
| AI voice calling | ❌ Excluded | Higher cost, compliance surface, and operational risk; not justified before text/email proof. |
| Multichannel campaigns | ❌ Excluded | Scope expansion; prove one channel works first. |
| Deposit / payment enforcement | ❌ Excluded | Changes the value proposition from recovery to enforcement; separate risk profile. |
| General-purpose CRM | ❌ Excluded | Platform creep; pilot must stay bounded to appointment recovery. |
| New fleet agents | ❌ Excluded | 30-day mission constraint: no new agents. |
| Custom integrations without pilot evidence | ❌ Excluded | Integration cost must be tied to a signed pilot, not built speculatively. |

---

## Decision Gate

**Architecture remains BLOCKED_PENDING_EVIDENCE until:**
- At least 10 customer interviews are completed,
- At least 5 businesses demonstrate measurable no-show exposure,
- At least 3 describe the problem as recurring and economically meaningful, and
- At least 1 commits to providing baseline data or running a controlled 30-day pilot.

Once that threshold is met, ORACLE may convert the thesis into a bounded pilot design; CLAUDE may implement only the confirmed, narrow scope; and SOL may coordinate live operations and evidence preservation.
