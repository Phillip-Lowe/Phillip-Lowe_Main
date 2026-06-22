---
name: green-lead-scraper
description: Scrapes business leads from websites, directories, and APIs. Built for Green's business — wraps existing Python pipeline with CLI, JSON output, and deduplication. Use when sourcing prospects, enriching contact data, or feeding leads into outreach pipelines.
---

# Green Lead Scraper

Scrapes business leads from websites, directories, and APIs. Built for Green's business — wraps existing Python pipeline with CLI, JSON output, and deduplication.

## Pipeline

1. **Source** — Input URLs, directories, or CSV lists of target businesses
2. **Scrape** — Extract contact info, services, location, ratings
3. **Enrich** — Cross-reference with enrichment APIs (Hunter, Apollo)
4. **Deduplicate** — Merge duplicates by domain, phone, or normalized name
5. **Export** — JSON/CSV for downstream tools (CRM, outreach, reports)

## Requirements

- Python 3.10+
- Playwright (for JS-rendered sites)
- `requests`, `beautifulsoup4`, `lxml`
- API keys for enrichment (optional): `HUNTER_API_KEY`, `APOLLO_API_KEY`

## Quick Start

```bash
# Scrape from a directory page
python scripts/scrape.py --source "https://example.com/directory" --output leads.json

# Scrape from CSV list of URLs
python scripts/scrape.py --source urls.csv --format csv --output leads.json

# Enrich with Hunter.io
python scripts/scrape.py --source leads.json --enrich hunter --output enriched.json

# Deduplicate
python scripts/dedup.py --input enriched.json --key domain --output final.json
```

## Configuration

Edit `scripts/config.json`:
- `maxPages`: Max pages per source (default: 50)
- `delayMs`: Delay between requests in ms (default: 1500)
- `userAgent`: Custom user agent string
- `selectors`: Site-specific CSS selectors for name, phone, email, address
- `enrichment`: Enabled enrichers (`hunter`, `apollo`, `none`)

## Input Formats

- `url` — Single URL string
- `csv` — CSV with `url` column
- `json` — JSON array of `{url, name}` objects

## Output Schema

Each lead is a JSON object:
```json
{
  "name": "Green Landscaping",
  "domain": "greenlandscaping.com",
  "phone": "(555) 123-4567",
  "email": "contact@greenlandscaping.com",
  "address": "123 Main St, Springfield",
  "services": ["Lawn Care", "Tree Trimming"],
  "rating": 4.5,
  "review_count": 127,
  "source_url": "https://yelp.com/...",
  "scraped_at": "2026-06-05T06:00:00Z",
  "enriched": false
}
```

## Scripts

- `scripts/scrape.py` — Main scraper engine
- `scripts/dedup.py` — Deduplication by key
- `scripts/enrich.py` — Enrichment API wrapper
- `scripts/config.json` — Configuration

## Safety

- Rate limiting enforced via `delayMs`
- Respect robots.txt (checked before scraping)
- No scraping behind login walls without explicit permission
- Suppression list checked before enrichment

## References

- See `references/selectors.md` for pre-built selectors for popular directories
- See `references/robots-policy.md` for robots.txt handling rules
