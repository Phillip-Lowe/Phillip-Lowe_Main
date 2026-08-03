# SYSTACK-NOSHOW-30D-001 — Appointment Recovery Pilot

**Status:** 🔴 EVIDENCE_COLLECTION  
**Mission:** Prove SyStack can measurably reduce preventable appointment no-shows for one narrowly defined service-business segment.  
**Deadline:** 2026-09-01  
**Decided:** 2026-08-02 22:38 CDT by GREEN  
**Reference:** `memory/2026-08-02-builder-level-assessment.md`; `templates/one-page-initiative-packet.md`

---

## Charter

**Buyer:** Owner-operated appointment businesses where one missed appointment creates meaningful lost revenue and staff downtime.  
**Initial subsegments (unranked):** barbershops, salons, beauty professionals, consultants, scheduled-service trades.  
**Excluded initially:** regulated healthcare (privacy/compliance complexity).

**Problem:** Customers forget appointments, ignore generic reminders, or fail to confirm/cancel/reschedule without staff follow-up — leaving the business with too little time to refill the opening.

**Out of scope for pilot:** Pricing problems, customer dissatisfaction, transportation, poor service quality, payment enforcement, reputation management, lead nurturing.

---

## Primary Metric

**Preventable No-Show Rate = Preventable No-Shows / Eligible Scheduled Appointments**

**Supporting metrics:**
- Baseline no-show rate
- Pilot-period no-show rate
- Confirmation rate
- Cancellation rate
- Rescheduling rate
- Unresponsive booking rate
- Appointments recovered
- Revenue protected
- Staff follow-up minutes avoided
- Reminder delivery failures
- Customer opt-outs or complaints

**Target:** 20% relative reduction in preventable no-shows (test target, not promised customer result).  
**Example:** 10% → 8% = 20% relative reduction, 2 percentage points absolute.

---

## Pilot Offer

> **SyStack Appointment Recovery Pilot**  
> A 30-day managed system that confirms appointments, identifies unresponsive customers, facilitates cancellation or rescheduling, and helps the business recover openings before they become lost revenue.

**Included:**
- Booking intake from one supported source
- Initial booking confirmation
- Scheduled reminder sequence
- Confirm, cancel, and reschedule actions
- Unresponsive-customer classification
- Staff escalation for defined exceptions
- Appointment outcome recording
- Weekly outcome report
- End-of-pilot comparison against baseline

**Excluded during pilot:**
- General-purpose CRM
- New customer dashboard unless required
- AI voice calling
- Complex multichannel campaigns
- Deposits and payment enforcement
- Reputation management
- Lead nurturing
- Broad customer support automation
- Additional fleet agents
- Custom integrations without pilot evidence

---

## Evidence Threshold

**Before substantial new architecture:**
- 10 customer interviews
- At least 5 businesses with measurable no-show exposure
- At least 3 reporting the problem as recurring and economically meaningful
- At least 1 willing to provide baseline data or run a controlled pilot

**Architecture authorization:** existing SyStack components only for demonstrations and discovery.  
**New build authorization:** BLOCKED_PENDING_EVIDENCE.

---

## Success Criteria

**Commercial proof:**
- At least 1 paid pilot

**Operational proof:**
- Live booking-to-outcome execution
- Reconciled appointment status records
- No cross-customer data leakage
- Defined exception and recovery path

**Outcome proof (any of):**
- Demonstrated reduction in preventable no-shows
- Documented recovered revenue exceeding pilot cost
- Strong leading result when sample is too small (confirmed appointments, timely cancellations, recovered openings)

**Replication proof:**
- A case study
- A reusable deployment checklist
- A clearly bounded second-customer implementation path

---

## Stop Rules

Pause or retire if:
- No-show loss is too small to motivate payment
- Businesses cannot provide reliable booking outcomes
- Existing booking platforms already solve it adequately
- Integration cost exceeds realistic customer value
- Prospects consistently want lead generation rather than appointment recovery
- Operational burden cannot support the current SyStack price structure
- Pilot cannot establish a credible baseline
- Segment requires regulated-data controls beyond pilot scope

**Rejection of the initial segment is not rejection of the thesis.** It may indicate another appointment category has stronger economics.

---

## 30-Day Sequence

### Days 1–5: Evidence
- [ ] Select 25 qualified interview targets
- [ ] Conduct first 10 interviews
- [ ] Record exact customer language
- [ ] Quantify missed appointments and average appointment value
- [ ] Document current reminder/recovery practices
- [ ] Identify booking platforms and integration constraints
- [ ] Rank subsegments by pain, accessibility, data quality, willingness to pay

### Days 6–10: Offer
- [ ] Select one subsegment
- [ ] Establish baseline measurement method
- [ ] Finalize fixed pilot scope
- [ ] Produce one concise demonstration
- [ ] Create outreach and pilot materials
- [ ] Define data-handling and customer responsibilities
- [ ] Begin direct pilot acquisition

### Days 11–15: Controlled implementation
- [ ] Connect one booking source
- [ ] Configure confirmation and reminder timing
- [ ] Implement response states
- [ ] Configure cancellation, rescheduling, escalation
- [ ] Validate customer isolation and webhook protection
- [ ] Run deterministic test appointments
- [ ] Obtain pilot approval before live activation

### Days 16–27: Live operation
- [ ] Monitor delivery and response events
- [ ] Reconcile scheduled appointments against outcomes
- [ ] Record exceptions without silently patching them
- [ ] Run weekly outcome comparisons
- [ ] Avoid expanding scope during live test
- [ ] Capture staff and customer feedback

### Days 28–30: Decision
- [ ] Calculate operational and commercial results
- [ ] Produce case study
- [ ] Document implementation time and maintenance burden
- [ ] Decide: scale, modify, change segment, or retire
- [ ] Open lead follow-up as next mission only if this validates the acquisition path

---

## Existing Assets

| Asset | Status | Notes |
|---|---|---|
| `systack_noshow` Postgres DB | ✅ Exists | `bookings` table, `booking_settings` table |
| Booking creation workflow | ✅ Live | n8n, confirmation token |
| Confirmation email/workflow | ✅ Live | Token validation, HTML page |
| T-24h reminder scheduler | ✅ Active | n8n, every 5 min |
| T-2h urgent reminder | ✅ Active | n8n, every 5 min, flags at_risk |
| Auto-release unconfirmed | 📋 Queued | Next build, post-evidence |
| Smart rebooking engine | 📋 Queued | Future build |
| Booking dashboard | ✅ Port 8772 | Tailscale-only, PIN-locked |
| Branded email template | ✅ Implemented | `memory/2026-06-11-systack-email-template-fleet-reference.md` |

---

## Fleet Assignment

| Agent | Responsibility |
|---|---|
| GREEN | Select segment, participate in decisive interviews, approve pilot terms, final scale/retire decision |
| SOL | Own mission board, sequence execution, enforce scope, coordinate live operations |
| ORACLE | Complete initiative packet, formalize thesis, design pilot, evaluate strategic evidence |
| ATLAS | Build prospect list, prepare account context, structure interview evidence |
| CHATTY | Create interview outreach, pilot messaging, follow-ups, case study |
| CLAUDE | Implement only confirmed pilot requirements |
| CODY | Review booking-state architecture, integration correctness, data boundaries |
| VALI | Validate technical execution and measurable business outcomes |
| PESSI | Review webhook security, customer isolation, failure handling, maintenance burden, opportunity cost |
| JURIS | Review pilot terms, consent language, messaging obligations, data-processing exposure |
| ASSEMBLY | Prepare controlled test and production deployment procedures |

---

## First Actions

1. [x] GREEN commits to no-show reduction mission
2. [ ] SOL creates canonical mission packet
3. [ ] ORACLE formalizes one-page initiative packet
4. [ ] ATLAS builds 25-target prospect list for first subsegment
5. [ ] CHATTY drafts interview outreach and script
6. [ ] SOL schedules first 3 customer interviews with GREEN
