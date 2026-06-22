# Systack — Lead Scraper + CRM System
## Internal Implementation Guide

**Automation ID:** `lead-scraper`  
**Version:** 1.0  
**Status:** Live — Service Offered  
**Date:** 2026-06-16  
**Builder:** SOL / Assembly

---

## Brand Reference

| Role | Color | Hex |
|------|-------|-----|
| Headers, CTAs | Navy | `#001a2d` |
| Secondary accents | Teal | `#007da9` |
| Primary buttons, links | Cyan | `#00a1db` |
| Body text | Gray 600 | `#475569` |
| Headings | Gray 800 | `#1e293b` |
| Success | Green | `#22c55e` |
| Error | Red | `#ef4444` |

---

## 1. Overview

Automated lead generation system that scrapes Google Maps for businesses matching target criteria, enriches with website/contact data, and stores in a PostgreSQL CRM database. Used for outbound sales prospecting.

**Workflows:**
- `Green_Systems_—_Lead_Scraper_(Little_Rock_Restaurants).json`
- `Green_Systems_—_Service_Business_Lead_Scraper.json`
- `Systack_Lead_Scraper_—_PostgreSQL_CRM.json`

---

## 2. System Architecture

```
Google Maps API query
  → Search: "restaurants Little Rock" (or configured query)
    → For each result:
      → Extract: name, address, phone, website, place_id, rating
      → Visit website → extract email/contact if available
      → Score lead (completeness + relevance)
      → Upsert to PostgreSQL CRM
    → Generate lead report
    → Feed into Outreach Sequencer
```

---

## 3. Core Components

### Data Sources

| Source | Data Extracted |
|--------|---------------|
| Google Maps API | Name, address, phone, place_id, rating, website |
| Website scraping | Email, contact form, about page text |
| Enrichment | Business category, hours, social links |

### Database Schema

```sql
CREATE TABLE leads (
  id SERIAL PRIMARY KEY,
  place_id TEXT UNIQUE,
  name TEXT,
  address TEXT,
  phone TEXT,
  email TEXT,
  website TEXT,
  rating REAL,
  category TEXT,
  status TEXT DEFAULT 'new',
  notes JSONB,
  scraped_at TIMESTAMP,
  enriched_at TIMESTAMP
);
```

---

## 4. Setup Process

### Step 1 — Configure Google Maps API

- Enable Places API in Google Cloud Console
- Set API key in n8n credential
- Configure search query + radius

### Step 2 — Import Workflows

- Lead Scraper workflow
- PostgreSQL CRM workflow
- Configure database credential

### Step 3 — Set Scraping Schedule

- Cron: daily or weekly
- Rate limit: respect Google API quotas
- Deduplication: check `place_id` before insert

---

## 5. Configuration

| Variable | Purpose |
|----------|---------|
| `GOOGLE_MAPS_API_KEY` | Places API access |
| `SEARCH_QUERY` | What to search for |
| `SEARCH_RADIUS` | Search radius in meters |
| `PG_CONNECTION` | PostgreSQL credential |

---

## 6. Lead Statuses

| Status | Meaning |
|--------|---------|
| `new` | Freshly scraped, not contacted |
| `contacted` | Outreach sent |
| `responded` | Prospect replied |
| `qualified` | Meeting booked or interested |
| `client` | Converted to paying client |
| `dead` | Not interested / bad contact |

---

*Internal document — do not share with clients.*  
*© 2026 Systack. All rights reserved.*
