# Google Reviews Monitor — Setup Guide

**Client ID:** 1  
**Prepared by:** SOL (System Operations Liaison)  
**Date:** 2026-06-23  
**Status:** 📋 READY TO BUILD

---

## What You Get

An automated system that:

1. **Monitors** your Google Business Profile for new reviews
2. **Alerts** you instantly (email/Slack/SMS) when a review is posted
3. **Categorizes** reviews by star rating (5★, 4★, 3★, 2★, 1★)
4. **Tracks** response status (replied vs unanswered)
5. **Reports** weekly summary of review activity

**Never miss a review again.**

---

## How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Google Maps    │────▶│  API Polling     │────▶│  New Review?    │
│  (New Review)   │     │  (Every 15 min)  │     │  Alert Trigger  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                              ┌───────────────────────────┼───────────┐
                              ▼                           ▼           ▼
                        ┌──────────┐               ┌──────────┐  ┌──────────┐
                        │  1-3★    │               │  4-5★    │  │  Weekly  │
                        │  (Alert) │               │  (Log)   │  │  Report  │
                        └──────────┘               └──────────┘  └──────────┘
```

---

## Architecture Options

### Option A: n8n Automation (Recommended)

**Pros:** No-code, visual workflow, easy to modify  
**Cons:** Requires n8n instance

**Components:**
- **Schedule Trigger** — Every 15 minutes
- **HTTP Request** — Call Google Business API
- **If Node** — New reviews since last check?
- **Switch Node** — Route by star rating
- **Email/Slack** — Alert for 1-3★ reviews
- **Google Sheets** — Log all reviews

### Option B: Python Script + Cron

**Pros:** Lightweight, no dependencies  
**Cons:** Requires server, manual setup

**Components:**
- Python script using `google-api-python-client`
- OAuth 2.0 authentication
- SQLite database for tracking
- Email notifications via SMTP
- Systemd timer or cron for scheduling

### Option C: Third-Party Service Integration

**Pros:** Zero maintenance  
**Cons:** Monthly cost, less control

**Options:**
- **BrightLocal** — Review monitoring + alerts
- **ReviewTrackers** — Multi-location dashboards
- **Grade.us** — Automated review requests + monitoring

---

## Google Business Profile API Setup

### Step 1: Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project (or select existing)
3. Note your **Project ID**

### Step 2: Enable APIs

1. Navigate to **APIs & Services > Library**
2. Enable:
   - **My Business API** (v4) — `mybusiness.googleapis.com`
   - **My Business Account Management API** (v1)
3. Wait 5-10 minutes for propagation

### Step 3: OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Select **Desktop app** (for scripts) or **Web application** (for dashboards)
4. Download the JSON credentials file
5. **Save securely** — never commit to git

### Step 4: API Key (Alternative)

For read-only operations, an API key is simpler:
1. **Create Credentials > API key**
2. Restrict key to My Business API only
3. Add HTTP referrer restrictions (for web apps)

---

## n8n Workflow Design

### Nodes Required

| # | Node | Purpose | Config |
|---|------|---------|--------|
| 1 | **Schedule Trigger** | Every 15 min | Interval: 15 minutes |
| 2 | **HTTP Request** | Fetch reviews | Method: GET, URL: `mybusiness.googleapis.com/v4/...` |
| 3 | **Function** | Parse response | Extract review array |
| 4 | **If** | New reviews? | Check `reviewUpdateTime > lastCheckTime` |
| 5 | **Switch** | Route by rating | Cases: 1★, 2★, 3★, 4★, 5★ |
| 6 | **Email** | Alert for 1-3★ | SMTP credential, urgent subject |
| 7 | **Slack** | Alert for 1-3★ | Webhook URL, @mention owner |
| 8 | **Google Sheets** | Log all reviews | Append row: date, rating, comment, replied? |

### Workflow JSON (Skeleton)

```json
{
  "name": "Google Reviews Monitor",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "rule": {
          "interval": [{"field": "minutes", "minutesInterval": 15}]
        }
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "method": "GET",
        "url": "https://mybusiness.googleapis.com/v4/accounts/{accountId}/locations/{locationId}/reviews",
        "authentication": "genericCredentialType",
        "genericAuthType": "googleAuth"
      }
    }
  ]
}
```

---

## API Endpoints Reference

### List Reviews

```
GET https://mybusiness.googleapis.com/v4/accounts/{accountId}/locations/{locationId}/reviews
```

**Query Parameters:**
- `pageSize` — Max 50 per request
- `pageToken` — For pagination

**Response Fields:**
- `name` — Review ID
- `reviewId` — Unique identifier
- `reviewer` — Display name, profile photo
- `starRating` — FIVE, FOUR, THREE, TWO, ONE
- `comment` — Review text
- `createTime` — When posted
- `updateTime` — Last modified
- `reviewReply` — Your response (if any)

### Reply to Review

```
PUT https://mybusiness.googleapis.com/v4/accounts/{accountId}/locations/{locationId}/reviews/{reviewId}/reply
```

**Body:**
```json
{
  "comment": "Thank you for your feedback! We appreciate your business."
}
```

---

## Alert Logic

### Immediate Alerts (Send within 5 minutes)

| Rating | Action | Channels |
|--------|--------|----------|
| 1★ | 🚨 URGENT — Owner alert | Email + SMS + Slack |
| 2★ | ⚠️ Alert — Check promptly | Email + Slack |
| 3★ | ℹ️ Notice — Review today | Email (daily digest) |
| 4★ | ✅ Good — Log only | Weekly report |
| 5★ | 🌟 Great — Thank them | Weekly report + reply prompt |

### Reply SLA Targets

| Rating | Target Response Time |
|--------|---------------------|
| 1-2★ | Within 2 hours |
| 3★ | Within 24 hours |
| 4-5★ | Within 48 hours |

---

## Dashboard Metrics

Track these KPIs in your dashboard:

| Metric | Formula | Target |
|--------|---------|--------|
| **Average Rating** | Sum(stars) / Count | ≥ 4.2 |
| **Response Rate** | Replied / Total | 100% |
| **Avg Response Time** | Time to reply | < 24h |
| **Review Velocity** | Reviews / month | Growing |
| **Sentiment Ratio** | 4-5★ / Total | ≥ 80% |

---

## Pricing

### Build-It-Yourself (Systack)

| Component | Cost |
|-----------|------|
| n8n workflow setup | $500 one-time |
| Google Cloud API | Free (10,000 requests/day) |
| Email/Slack alerts | Free |
| **Total** | **$500 setup** |

### Third-Party Alternatives

| Service | Price | Best For |
|---------|-------|----------|
| **BrightLocal** | $29-79/mo | Multi-location chains |
| **ReviewTrackers** | Custom quote | Enterprise |
| **Grade.us** | $25-40/mo | Small business |

---

## Setup Checklist

### Phase 1: API Access (Day 1)
- [ ] Create Google Cloud project
- [ ] Enable My Business API
- [ ] Create OAuth credentials
- [ ] Authenticate and get access token
- [ ] Test API call: list reviews

### Phase 2: Automation (Day 2-3)
- [ ] Build n8n workflow OR Python script
- [ ] Configure polling schedule (15 min)
- [ ] Set up alert routing (email/Slack)
- [ ] Create Google Sheets log
- [ ] Test with sample review

### Phase 3: Monitoring (Day 4-7)
- [ ] Verify alerts fire correctly
- [ ] Check response time tracking
- [ ] Build weekly report
- [ ] Train team on reply workflow
- [ ] Document escalation process

---

## Recommended Reply Templates

### 5★ Review
```
Thank you so much for the kind words, [Name]! We're thrilled you had a 
great experience. We look forward to serving you again soon!
```

### 4★ Review
```
Thanks for the feedback, [Name]! We're glad you enjoyed [specific thing]. 
If there's anything we can do to earn that 5th star next time, please let us know!
```

### 3★ Review
```
Hi [Name], thank you for taking the time to share your experience. We'd 
love to understand what we could have done better. Please reach out to 
[email] so we can make it right.
```

### 1-2★ Review
```
Hi [Name], we're truly sorry your experience didn't meet expectations. 
This isn't the standard we hold ourselves to. Please contact us directly 
at [phone/email] so we can address this personally and make it right.
```

---

## Next Steps

1. **Choose architecture** — n8n (recommended), Python, or third-party
2. **Get Google API access** — Follow Step 1-3 above
3. **Build workflow** — Use n8n or deploy Python script
4. **Test alerts** — Submit test review, verify notification
5. **Train team** — Reply templates, SLA targets, escalation

---

*Generated by SOL | Systack Automation Systems*
