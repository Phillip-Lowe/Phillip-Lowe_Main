# Google Reviews Monitoring Automation — Design Document

**Author:** GENI (Research/Design)
**Date:** 2026-05-20
**Status:** DRAFT — Awaiting SOL approval
**Task Type:** research/design (NOT implementation)

---

## Executive Summary

This document designs an automated system to monitor Google Reviews for businesses, analyze sentiment, flag negative reviews for human response, generate draft responses for positive reviews, and alert via designated channels.

**Key finding:** The Google Business Profile API (formerly Google My Business API) is the correct API for this use case. It provides review listing, retrieval, reply posting, and deletion — at **zero direct API cost**.

---

## 1. API Capabilities

### 1.1 Correct API: Google Business Profile API (v4)

**Base URL:** `https://mybusiness.googleapis.com/v4/`
**Documentation:** `https://developers.google.com/my-business/reference/rest/v4/`

The **Places API** is the WRONG API for this use case. The Places API can READ review data but CANNOT post replies. The Business Profile API (GBP API) is purpose-built for business owners/managers and supports the full review lifecycle.

### 1.2 Available Review Operations

| Operation | Endpoint | Description |
|-----------|----------|-------------|
| **List reviews** | `GET /v4/{parent=accounts/*/locations/*}/reviews` | Paginated list of all reviews for a location |
| **Get single review** | `GET /v4/{name=accounts/*/locations/*/reviews/*}` | Fetch a specific review by ID |
| **Update reply** | `PUT /v4/{name=accounts/*/locations/*/reviews/*}/reply` | Create or update a reply to a review |
| **Delete reply** | `DELETE /v4/{name=accounts/*/locations/*/reviews/*}/reply` | Remove a reply from a review |
| **List accounts** | `GET /v4/accounts` | List all accounts the authenticated user has access to |
| **List locations** | `GET /v4/{parent=accounts/*}/locations` | List all locations under an account |

### 1.3 Review Object Structure

```json
{
  "reviewId": "string",
  "reviewer": {
    "displayName": "John Doe",
    "profilePhotoUrl": "https://...",
    "isAnonymous": false
  },
  "starRating": "enum: ONE, TWO, THREE, FOUR, FIVE",
  "comment": "string (the review text body)",
  "createTime": "2026-05-19T14:30:00Z",
  "updateTime": "2026-05-19T14:30:00Z",
  "reviewReply": {
    "comment": "string (business owner reply)",
    "updateTime": "2026-05-19T15:00:00Z"
  },
  "name": "accounts/{accountId}/locations/{locationId}/reviews/{reviewId}"
}
```

### 1.4 Key Limitations

1. **Location must be verified** — Only verified locations on Google Business Profile can access their reviews via API
2. **OAuth required** — No API key access; requires authenticated user with `https://www.googleapis.com/auth/business.manage` scope
3. **API access requires approval** — Google must approve your GCP project before you can use the GBP API
4. **Reply length limited** — Google imposes character limits on review replies (typically ~1,500 characters)
5. **Can't reply to all reviews** — Some reviews may have replies disabled (e.g., reviews flagged for policy violations)
6. **No webhook/push notifications** — No native event-based notification for new reviews; polling is required

---

## 2. Authentication & Credentials

### 2.1 Current State

**Status: UNKNOWN — No credentials found in fleet memory or configs.**

The fleet does not currently have Google API credentials configured. This must be created as a prerequisite step.

### 2.2 Required Setup (Prerequisite)

| Step | Description | Owner |
|------|-------------|-------|
| 1 | Create a GCP Project | GREEN or SOL |
| 2 | Enable the Google Business Profile API in GCP Console | GREEN or SOL |
| 3 | Create OAuth 2.0 credentials (Desktop or Web Application type) | GREEN or SOL |
| 4 | Submit API access request to Google for approval | GREEN or SOL |
| 5 | Obtain refresh token with `business.manage` scope | GREEN or SOL |
| 6 | Verify business locations are claimed/verified in GBP | GREEN (business owner) |
| 7 | Store credentials securely (1Password or env vars) | GREEN or SOL |

### 2.3 OAuth Flow

```
1. Open OAuth consent URL in browser (one-time)
2. User (GREEN) authorizes the app to manage GBP
3. Exchange auth code for access token + refresh token
4. Store refresh token securely
5. Use refresh token to obtain new access tokens (they expire every ~1 hour)
```

### 2.4 Required OAuth Scope

```
https://www.googleapis.com/auth/business.manage
```

---

## 3. API Costs

### 3.1 Direct API Cost

**$0.00 — The Google Business Profile API is free.**

From Google's official pricing page:
> "The Google My Business API is available to registered users at no charge."

### 3.2 Infrastructure Costs

| Item | Estimated Cost |
|------|---------------|
| GBP API access | $0/month |
| Compute (running the agent/script) | $0 (runs on fleet host) |
| GCP Project (for OAuth) | $0 (free tier sufficient) |
| **TOTAL** | **$0/month** |

### 3.3 Optional Costs (Not Required)

- Places API for additional place data: $17-40 per 1000 requests (not needed for this use case)
- Sentiment analysis via external API (e.g., Google Natural Language API): ~$1-2 per 1000 reviews if using a cloud service. The fleet can do this locally with LLM-based analysis at zero marginal cost.

---

## 4. Rate Limits / Quotas

### 4.1 Default Quotas (GBP API)

Google enforces quotas per GCP project. The documented defaults:

| Metric | Default Limit |
|--------|---------------|
| Requests per minute (read) | 300 QPM (default) |
| Requests per minute (write/modify) | 300 QPM (default) |
| Requests per day | No hard daily limit for review operations |

For review monitoring (hourly polling, small number of businesses), **quota will never be an issue**.

### 4.2 Error Handling

- `429 Too Many Requests` → Exponential backoff with retry
- `403 Forbidden` → Check OAuth token validity, refresh if expired
- `404 Not Found` → Location or review no longer exists
- `409 Conflict` → Review already has a reply (when attempting to create)

### 4.3 Recommendation

For monitoring 1-10 businesses, hourly polling is safe. Even per-minute polling for a single business would be well within quotas.

---

## 5. Business ID Lookup Method

### 5.1 How to Find Your Account and Location IDs

**Method A: API Discovery (recommended)**

```
1. Call GET /v4/accounts
   → Returns list of {name: "accounts/123456789"}

2. Call GET /v4/{accountName}/locations
   → Returns list of {name: "accounts/123456789/locations/987654321", locationName: "Business Name"}

3. Use the location name as the parent for review list calls
```

**Method B: Google Business Profile Manager (manual)**

1. Go to `https://business.google.com/`
2. Select the business location
3. The URL or page info may contain the location ID
4. Cross-reference with API discovery

**Method C: Google Maps URL extraction**

1. Find the business on Google Maps
2. The Place ID is in the URL (after `place/`)
3. Can use Places API to map Place ID to GBP location (requires Places API)

---

## 6. Automation Workflow Design

### 6.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    SCHEDULER (cron/OpenClaw)              │
│                   Triggers every N hours                   │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              REVIEW FETCHER (GBP API Client)              │
│  - Refresh OAuth token                                    │
│  - List reviews for configured locations                  │
│  - Compare with stored review IDs (deduplication)          │
│  - Identify NEW reviews since last run                    │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              SENTIMENT ANALYZER (LLM-based)               │
│  - Classify: POSITIVE (4-5★) / NEUTRAL (3★) / NEGATIVE (1-2★) │
│  - For negative: flag for human review                   │
│  - Extract key topics/themes mentioned                    │
└──────────────┬──────────────────────────────────────────┘
               │
          ┌────┴────┐
          ▼         ▼
    ┌─────────┐  ┌─────────────────┐
    │NEGATIVE? │  │   POSITIVE?      │
    │1-3 ★    │  │   4-5 ★          │
    └────┬────┘  └────────┬────────┘
         │                │
         ▼                ▼
┌─────────────────┐  ┌─────────────────────┐
│ ALERT + FLAG    │  │ DRAFT RESPONSE GEN  │
│ - War room msg  │  │ - LLM generates     │
│ - Email/iMsg    │  │   draft reply       │
│ - Mark for      │  │ - Queued for human  │
│   human review  │  │   approval before   │
│ - DO NOT auto-  │  │   posting           │
│   reply         │  └──────────┬──────────┘
└─────────────────┘             │
                                ▼
                     ┌─────────────────────┐
                     │  HUMAN REVIEW GATE  │
                     │  (War room / email) │
                     │  Approve/Edit/Reject│
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │  REPLY POSTER       │
                     │  PUT /review/reply  │
                     │  (after approval)   │
                     └─────────────────────┘
```

### 6.2 Detailed Step Breakdown

#### Step 1: Scheduled Trigger
- **Mechanism:** OpenClaw scheduled task, cron job, or TaskFlow job
- **Frequency:** Hourly (0-60 min delay to catch new reviews)
- **Config:** Stored in fleet config (which businesses, how often)

#### Step 2: Fetch New Reviews
- Refresh OAuth access token using stored refresh token
- Call `GET /v4/accounts/{id}/locations/{id}/reviews?pageSize=50`
- Filter to reviews with `createTime > last_run_time`
- Store `last_run_time` and processed review IDs in local state file

#### Step 3: Sentiment Analysis
- **Simple approach (preferred):** Star rating is already provided by Google
  - 1-2★ = NEGATIVE → Flag for human
  - 3★ = NEUTRAL → Flag for human
  - 4-5★ = POSITIVE → Generate draft response
- **Enhanced approach (optional):** LLM-based sentiment on review text for nuance detection (sarcasm, mixed signals)
- **Local LLM analysis:** Zero additional cost; use fleet LLM

#### Step 4: Negative/Negative Review Handling
- Post alert to fleet war room (channel: webchat)
- Optionally send email via Gmail API or iMessage
- Never auto-reply to negative reviews
- Queue for GREEN/SOL human review

#### Step 5: Positive Review Draft Response
- Generate draft using LLM with prompt template:
  ```
  Business: {business_name}
  Review: "{review_text}" (Rating: {stars}★)
  Reviewer: {reviewer_name}
  
  Generate a warm, professional, personalized reply that:
  - Thanks the reviewer by name
  - References something specific from their review
  - Reinforces the business's values
  - Is under 500 characters
  ```
- Draft is queued for human approval, NOT auto-posted

#### Step 6: Human Approval & Posting
- Draft responses displayed in war room
- GREEN/SOL approves → Reply posted via API
- GREEN/SOL edits → Edited version posted
- GREEN/SOL rejects → No reply posted

#### Step 7: State Persistence
- Store in: `~/.openclaw/workspaces/sol/data/google-reviews-state.json`
- Track: `last_check_time`, `processed_review_ids[]`, `pending_replies[]`

### 6.3 Alert Channels

| Alert Type | Channel | Priority |
|-----------|---------|----------|
| New negative review (1-2★) | War room + Email | HIGH |
| New neutral review (3★) | War room | MEDIUM |
| New positive review (4-5★) | War room (with draft) | LOW |
| API error / quota exceeded | War room | HIGH |
| No new reviews | Silent | N/A |

### 6.4 Automation Rules (Hard Constraints)

1. **NEVER auto-post replies** — All replies require explicit human approval
2. **NEVER auto-reply to negative reviews** — Negative reviews always get human-written responses
3. **Maximum one reply per review** — API enforces this; only create replies where `reviewReply` is null
4. **Respect deleted reviews** — Skip reviews with `state != LIVE` (they may be flagged/removed)
5. **Handle API errors gracefully** — Retry with backoff; escalate persistent failures to SOL

---

## 7. Scope Definition

### 7.1 What This System Monitors

- **Configured business locations** — Defined in config (initially: GREEN's businesses, which must be specified)
- **Google Reviews only** — Not Yelp, Trustpilot, etc. (future expansion possible)
- **New reviews** — Reviews created since last check (incremental)

### 7.2 What This System Does NOT Do

- Monitor non-Google review platforms
- Auto-post replies without approval
- Auto-respond to negative reviews
- Delete or flag reviews
- Create or modify business listings
- Handle reviews for unverified locations

### 7.3 Configurable Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `check_interval_minutes` | 60 | How often to poll for new reviews |
| `business_location_ids` | (empty) | List of GBP location IDs to monitor |
| `negative_threshold_stars` | 3 | Reviews ≤ this star rating are flagged |
| `alert_channels` | `["war_room"]` | Where to send alerts |
| `auto_generate_drafts` | `true` | Whether to generate reply drafts for positive reviews |
| `max_draft_length` | 500 | Max characters for draft replies |

---

## 8. Implementation Plan

### 8.1 Prerequisites (Must Complete First)

| # | Task | Dependency | Estimated Effort |
|---|------|------------|-----------------|
| P1 | Create GCP Project | None | 30 min |
| P2 | Enable GBP API | P1 | 5 min |
| P3 | Create OAuth credentials | P1 | 15 min |
| P4 | Submit API access request to Google | P3 | 10 min + wait (~3-7 days) |
| P5 | Obtain refresh token | P4 | 15 min |
| P6 | Verify business locations in GBP | None (GREEN) | 15 min per location |

### 8.2 Implementation Phases

#### Phase 1: API Client (CODY domain, or GENI with CODY pairing)
1. Build GBP API client module (Python or Node.js)
2. Implement OAuth token management with refresh
3. Implement review listing with pagination
4. Test against actual GBP account

#### Phase 2: Sentiment & Drafting
5. Implement star-rating-based sentiment classification
6. Implement LLM-based draft generation for positive reviews
7. Implement state persistence (seen reviews, last check time)

#### Phase 3: Alerting & Integration
8. Post alerts to fleet war room channel
9. Set up email/iMessage alerts (optional enhancement)
10. Build approval workflow (war room interaction)

#### Phase 4: Scheduling & Operations
11. Set up scheduled execution (cron or OpenClaw schedule)
12. Add monitoring and health checks
13. Add error reporting and alerting for API failures

### 8.3 Skill/Agent Assignments

| Component | Best Agent | Notes |
|-----------|-----------|-------|
| API client code | CODY | Code implementation |
| LLM draft generation | GENI | Prompt engineering, response quality |
| Sentiment classification | CODY or GENI | Simple star-based logic |
| Alerting/integration | ASSEMBLY | System integration |
| Scheduling | SOL | Task scheduling |
| Human approval | GREEN | Final decision authority |

---

## 9. Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Google API access denied | HIGH | Have fallback plan (manual monitoring); appeal process exists |
| OAuth token expiration not handled | MEDIUM | Implement token refresh with retry logic; alert on persistent failures |
| Review already has reply (API conflict) | LOW | Check `reviewReply` before attempting; skip if exists |
| False sentiment classification (sarcasm) | LOW | LLM-enhanced classification for edge cases |
| API quota exceeded (unlikely) | LOW | Exponential backoff; rate limit at application level |
| Business location unverified/removed | MEDIUM | Graceful error handling; alert to verify location |

---

## 10. Alternative: Places API (NOT Recommended)

The Places API (New) can read review data via Place Details with `reviews` field mask. However:

- **CANNOT post replies** — Read-only for reviews
- **Costs money** — Place Details (New) with reviews: $0.017-0.04 per request depending on SKU tier
- **Only returns 5 most relevant reviews** — Cannot get all reviews; only top 5
- **Good for:** Discovering review sentiment of competitor businesses (read-only)
- **Not suitable for:** Managing your own business's reviews (reply capability required)

**Verdict: Use GBP API. Do not use Places API for this use case.**

---

## 11. Open Questions for SOL/GREEN

1. **Which business locations need monitoring?** — Need specific GBP location IDs
2. **Is a Google Cloud Platform project already created?** — If yes, which one?
3. **Has GBP API access been previously requested?** — Approval takes 3-7 days
4. **Approval workflow preference** — War room only, or email + war room?
5. **Review response voice/tone guidelines** — Any specific brand voice to follow for draft replies?
6. **Budget for optional NLP API** — If LLM-based classification is insufficient, budget needed for Google Natural Language API (~$1-2/1k reviews)

---

## 12. Next Steps

1. **SOL reviews this design** → Approves or requests changes
2. **GREEN completes prerequisites P1-P6** (GCP setup, OAuth, GBP API access)
3. **SOL issues build mission to CODY** → Implement API client
4. **SOL issues build mission to GENI** → Draft reply generation prompts
5. **ASSEMBLY integrates** → Alerting, scheduling, workflow

---

*This is a DESIGN document. Nothing has been implemented. No files modified. Awaiting SOL approval.*
