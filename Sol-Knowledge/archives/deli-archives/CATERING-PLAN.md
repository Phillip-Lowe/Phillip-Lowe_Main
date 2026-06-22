# Utopia Deli — Catering/Event Lead Scoring System
## Complete Plan & Architecture

**Date:** 2026-06-08
**Status:** PLANNING — Pending Review
**Owner:** Phillip Lowe (Sol/Systack)

---

## 1. OVERVIEW

Build a lead capture + scoring + automated response system for Utopia Deli catering/events. Replaces "call us for catering" with a professional, automated intake that filters good leads from bad ones and responds instantly.

**Two deployment options (decision needed):**
| Option | Pros | Cons |
|--------|------|------|
| **A. Standalone HTML page** (`order.theutopiadeli.com/catering.html`) | Fast to build, independent, easy to iterate | Separate URL, another file to maintain |
| **B. Integrated into main site** (`order.theutopiadeli.com` with Catering tab) | Unified experience, single URL, brand cohesion | More complex, risk of breaking existing order flow |

**Recommendation:** Start with Option A (standalone), then integrate into main site after validation.

---

## 2. FRONTEND — Event Lead Form

### 2.1 Fields Required (Grouped by Section)

**📋 Event Basics**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `event_name` | Text | Yes | Min 2 chars |
| `event_type` | Select | Yes | Dropdown: Corporate, Wedding, Birthday, Graduation, Church/Event, School, Other |
| `event_date` | Date | Yes | Must be ≥ 3 days from today |
| `event_time` | Time | Yes | Must be during business hours or "flexible" |
| `event_duration` | Number (hours) | Yes | 1-12 hours |

**👥 People & Logistics**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `headcount` | Number | Yes | 10-500 (min 10 for catering) |
| `setup_time_needed` | Number (minutes) | Yes | How much earlier than event start |
| `venue_name` | Text | Yes | Venue or address label |
| `venue_address` | Textarea | Yes | Full address for delivery/setup |
| `venue_distance` | Select | No | <5mi, 5-15mi, 15-30mi, >30mi |

**💰 Budget & Payment**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `budget_range` | Select | Yes | <$300, $300-600, $600-1200, $1200-2500, $2500+, "Need quote" |
| `who_pays` | Select | Yes | Event organizer, Attendees (individual), Company/Institution, Unknown yet |
| `payment_timing` | Select | Yes | Pay in full upfront, 50% deposit + balance day-of, Pay day-of, Net 30 (established clients only) |

**👤 Coordinator Contact**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `coordinator_name` | Text | Yes | Full name |
| `coordinator_phone` | Tel | Yes | 10 digits, US format |
| `coordinator_email` | Email | Yes | Valid email, confirmation field |
| `coordinator_role` | Text | No | Title/role at organization |

**🍽️ Food & Service Details**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `service_style` | Select | Yes | Drop-off (self-serve), Staffed buffet, Plated/service, Undecided |
| `dietary_restrictions` | Multi-select | No | Vegan, Vegetarian, Gluten-free, Nut allergies, Halal, Kosher, None |
| `menu_preferences` | Textarea | No | Specific items wanted, cuisine preferences |
| `equipment_needed` | Multi-select | No | Chafing dishes/warmers, Serving utensils, Plates/napkins, Tables, Tablecloths, None |
| `special_requests` | Textarea | No | Any other details |

**✅ Confirmation**
| Field | Type | Required |
|-------|------|----------|
| `agree_to_terms` | Checkbox | Yes | "I understand this is a request, not a confirmed booking" |
| `how_heard` | Select | No | Website, Instagram, Facebook, Referral, Previous customer, Other |

### 2.2 UI Design (Matching Existing Brand)

- Same color scheme: `#590B3F` primary, `#AF3D4B` accent, `#FBFCFE` background
- Same font: Open Sans
- Same card/radius style: 14px cards, 8px buttons
- Mobile-first: identical responsive approach as current order form
- Progress indicator: Step 1 (Event) → Step 2 (People) → Step 3 (Budget) → Step 4 (Contact) → Step 5 (Food)

### 2.3 UX Flow

```
User lands on catering page
  → Reads intro text: "Tell us about your event and we'll get back to you within 24 hours"
  → Fills 5-step form (or single long form with sections)
  → Client-side validation before submit
  → POST to webhook
  → Show "Thank you — check your email for next steps" page
  → Email arrives within 2 minutes (auto-response based on score)
```

---

## 3. BACKEND — n8n Scoring Workflow

### 3.1 Webhook Endpoint

```
POST https://utopia-api.systack.net/webhook/utopia-deli-catering-v1
Content-Type: application/json
```

### 3.2 Scoring Engine (JavaScript Node — ES5 Compatible)

**Weights (configurable):**

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Headcount | 20% | Linear: 10 people = 0pts, 500 people = 20pts |
| Budget Ratio | 20% | $/person: <$5 = 0pts, $5-10 = 10pts, $10-15 = 15pts, $15+ = 20pts |
| Lead Time | 20% | <1 week = 0pts, 1-2 weeks = 10pts, 2-4 weeks = 15pts, 4+ weeks = 20pts |
| Setup Complexity | 15% | Drop-off only = 15pts, Staffed = 10pts, Plated = 5pts |
| Distance | 10% | <5mi = 10pts, 5-15mi = 7pts, 15-30mi = 4pts, >30mi = 0pts |
| Payment Clarity | 10% | Pay upfront = 10pts, 50/50 = 8pts, Day-of = 5pts, Net 30 = 3pts, Unknown = 0pts |
| Dietary Complexity | 5% | None = 5pts, 1-2 restrictions = 3pts, 3+ restrictions = 0pts |

**Bonus Points:**
- Corporate client: +5 pts
- Previous customer (if we can detect): +10 pts
- Weekend event (higher margin days): +3 pts

**Penalty Points:**
- <48 hours notice: -20 pts (automatic REJECT if score goes below 40)
- Headcount < 10: -15 pts
- >30 miles + no budget specified: -10 pts

**Score Ranges & Actions:**

| Score | Tier | Action | Email Template |
|-------|------|--------|----------------|
| 0-39 | 🔴 REJECT | Auto-send rejection email | "TUD-CATERING-REJECT" |
| 40-69 | 🟡 REVIEW | Auto-send "more info needed" email | "TUD-CATERING-REVIEW" |
| 70-100 | 🟢 ACCEPT | Auto-send acceptance + onboarding | "TUD-CATERING-ACCEPT" |

### 3.3 n8n Node Flow

```
[Webhook Trigger] → [Validate Input] → [Score Lead] → [Log to Sheets] → [Switch on Score]
                                                                     
[Switch] → [REJECT branch] → [Email: Rejection] → [End]
       → [REVIEW branch] → [Email: Needs Info] → [Wait for Reply] → [Manual Review Node]
       → [ACCEPT branch] → [Email: Acceptance] → [Email: Onboarding Info] → [Notify Owner] → [End]
```

### 3.4 Google Sheets Logging

**Sheet Name:** `Utopia Deli Catering Leads`

| Column | Data |
|--------|------|
| A | Timestamp |
| B | Lead ID (UDC-YYYYMMDD-###) |
| C | Score |
| D | Tier (REJECT/REVIEW/ACCEPT) |
| E | Event Name |
| F | Event Type |
| G | Event Date |
| H | Headcount |
| I | Budget Range |
| J | Venue Distance |
| K | Coordinator Name |
| L | Coordinator Email |
| M | Coordinator Phone |
| N | Payment Terms |
| O | Service Style |
| P | Dietary Restrictions |
| Q | Equipment Needed |
| R | Special Requests |
| S | Raw JSON (for debugging) |

---

## 4. EMAIL TEMPLATES

### 4.1 REJECT Email (Score 0-39)

**Subject:** Re: Your Utopia Deli Catering Request — We Need to Decline

**Body:**
```
Hi [coordinator_name],

Thank you for considering Utopia Deli for [event_name] on [event_date].

After reviewing your event details, we unfortunately aren't able to accommodate 
this request. This is usually due to one of the following:

• Short notice (we need at least 48 hours for catering)
• Distance beyond our delivery range
• Headcount below our catering minimum (10 people)
• Date conflicts with existing bookings

We'd love to serve you in the future! For events with more lead time or 
larger groups, please reach out again.

Questions? Call or text us at (501) 551-5944.

— The Utopia Deli Team
```

### 4.2 REVIEW Email (Score 40-69)

**Subject:** Re: Your Utopia Deli Catering Request — We Need a Few Details

**Body:**
```
Hi [coordinator_name],

Thanks for your catering request for [event_name] on [event_date]! 
We're potentially interested but need a bit more information before we can confirm.

Could you please reply with:
1. A more specific headcount (even an estimate)
2. Your preferred budget per person, or total budget
3. Whether the venue has kitchen facilities or power outlets
4. Any flexibility on the event date or time

Once we have these details, we can give you a firm yes/no within 24 hours.

— The Utopia Deli Team
(501) 551-5944
```

### 4.3 ACCEPT Email (Score 70-100)

**Subject:** ✅ Utopia Deli is Available for [event_name]!

**Body:**
```
Hi [coordinator_name],

Great news — we're available for [event_name] on [event_date]!

Here's what happens next:

📋 STEP 1: We'll send you a catering menu with pricing
📋 STEP 2: You select items and confirm headcount
📋 STEP 3: We send an invoice (50% deposit to hold the date)
📋 STEP 4: Final headcount and payment due 3 days before the event

Your event details:
• Date: [event_date] at [event_time]
• Headcount: [headcount] people
• Venue: [venue_name] ([venue_address])
• Setup needed: [setup_time_needed] minutes before event
• Service style: [service_style]

Next email coming within 24 hours with menu options.

Questions? Call or text (501) 551-5944.

— The Utopia Deli Team
```

### 4.4 OWNER NOTIFICATION (Accepts only)

**To:** kitchen@utopiadeli.com + owner phone (SMS via email-to-SMS if needed)

**Subject:** 🔥 HIGH-QUALITY CATERING LEAD: [event_name]

**Body:**
```
NEW CATERING LEAD — Score: [score]/100

Event: [event_name]
Type: [event_type]
Date: [event_date] at [event_time]
Headcount: [headcount]
Budget: [budget_range]
Venue: [venue_name] ([venue_distance])

Coordinator: [coordinator_name]
Phone: [coordinator_phone]
Email: [coordinator_email]

Payment: [who_pays] — [payment_timing]
Service: [service_style]
Dietary: [dietary_restrictions]
Equipment: [equipment_needed]

Special requests: [special_requests]

Full details: [Google Sheets link]
```

---

## 5. CONFLICT CHECK (Phase 2 Enhancement)

After basic scoring is working, add conflict detection:

**Approach A: Simple (Recommended for V1)**
- Read from Google Sheets of existing confirmed bookings
- Check if `event_date` + `event_time` overlaps with any confirmed event
- If overlap → subtract 30 points from score (likely pushes to REJECT or REVIEW)

**Approach B: Calendar Integration (Phase 2)**
- Connect to Google Calendar or n8n calendar node
- Check for events on the same date
- Buffer time: 2 hours before + 1 hour after any existing event

---

## 6. DATA STRUCTURE (JSON Payload)

```json
{
  "lead_source": "catering-web-v1",
  "timestamp": "2026-06-08T14:30:00Z",
  
  "event": {
    "name": "Johnson Corp Lunch",
    "type": "corporate",
    "date": "2026-06-20",
    "time": "12:00",
    "duration_hours": 2,
    "setup_minutes_before": 30
  },
  
  "logistics": {
    "headcount": 45,
    "venue_name": "Johnson Corp Office",
    "venue_address": "123 Main St, Little Rock, AR 72201",
    "venue_distance": "5-15mi",
    "service_style": "drop-off",
    "equipment_needed": ["chafing-dishes", "serving-utensils"]
  },
  
  "budget": {
    "range": "600-1200",
    "who_pays": "company",
    "payment_timing": "50-50"
  },
  
  "coordinator": {
    "name": "Sarah Johnson",
    "phone": "501-555-0199",
    "email": "sarah@johnsoncorp.com",
    "role": "Office Manager"
  },
  
  "food": {
    "dietary_restrictions": ["vegetarian", "gluten-free"],
    "menu_preferences": "Sandwich platter, mostly chicken options",
    "special_requests": "Need vegetarian options clearly labeled"
  },
  
  "meta": {
    "agreed_to_terms": true,
    "how_heard": "referral"
  }
}
```

---

## 7. BUILD PLAN & TASKS

### Phase 1: Foundation (Week 1)
- [ ] **T1.1:** Create `catering-form.html` + `catering-form.js` (standalone page)
- [ ] **T1.2:** Build n8n webhook workflow JSON (scoring engine + email branches)
- [ ] **T1.3:** Create Google Sheets template with headers
- [ ] **T1.4:** Write email HTML templates (reject, review, accept, owner-notify)
- [ ] **T1.5:** Deploy to test URL + validate form POST

### Phase 2: Integration (Week 2)
- [ ] **T2.1:** Add "Catering/Events" tab/button to main order site
- [ ] **T2.2:** Add conflict check (read from Sheets)
- [ ] **T2.3:** Build "manual review" dashboard for REVIEW-tier leads
- [ ] **T2.4:** SMS notifications via Twilio or email-to-SMS
- [ ] **T2.5:** Analytics: lead volume, conversion rates by tier

### Phase 3: Polish (Week 3)
- [ ] **T3.1:** A/B test email copy
- [ ] **T3.2:** Add "save my progress" for long forms
- [ ] **T3.3:** Calendar integration for conflict detection
- [ ] **T3.4:** Auto-generate quote PDF for ACCEPT leads
- [ ] **T3.5:** Public launch + marketing

---

## 8. DECISIONS NEEDED

| # | Decision | Options | Default |
|---|----------|---------|---------|
| 1 | **Deployment** | Standalone page vs integrated | Standalone first |
| 2 | **Form style** | Multi-step wizard vs single long form | Multi-step |
| 3 | **Minimum headcount** | 10, 15, 20, or 25 | 10 |
| 4 | **Score threshold** | REJECT ≤39, REVIEW 40-69, ACCEPT 70+ | As specified |
| 5 | **Conflict check** | Simple (Sheets) vs Calendar (Phase 2) | Simple for V1 |
| 6 | **Notification** | Email only vs Email + SMS | Email only for V1 |
| 7 | **Menu attached** | Auto-send menu in ACCEPT email vs wait for manual | Auto-send |

---

## 9. RISK MITIGATION

| Risk | Mitigation |
|------|------------|
| False rejects (good leads scored low) | Weekly review of rejected leads, adjust weights |
| Spam/bogus submissions | Add honeypot field, rate limiting, email validation |
| Date conflicts after acceptance | Manual confirmation step before deposit invoice |
| Email deliverability | Use n8n Gmail node, not SMTP; monitor bounce rates |
| Over-promising auto-accepts | Acceptance email says "pending final confirmation" |

---

## 10. SUCCESS METRICS

| Metric | Target |
|--------|--------|
| Form completion rate | > 60% |
| Lead-to-response time | < 2 minutes |
| ACCEPT tier accuracy | > 85% (confirmed bookings / total accepts) |
| REVIEW tier conversion | > 50% (review → accept after info gathering) |
| Owner response time for REVIEW | < 24 hours |
| Monthly catering leads | > 10 by Month 3 |

---

## 11. FILES TO CREATE

| File | Purpose |
|------|---------|
| `catering-form.html` | Standalone catering lead page |
| `catering-form.js` | Form logic, validation, POST handler |
| `utopia-deli-catering-v1.json` | n8n workflow (scoring + emails) |
| `catering-email-templates.html` | All email HTML templates |
| `CATERING-PLAN.md` | This document |

---

**Next Step:** Review this plan with Phillip. Once approved, I'll build the frontend form first, then the n8n backend, then connect them.
