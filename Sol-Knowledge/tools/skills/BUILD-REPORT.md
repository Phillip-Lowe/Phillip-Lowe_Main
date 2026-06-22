# Green Custom Skills — Build Report

**Session:** BUILD-CUSTOM-SKILLS-1AM  
**Time:** Friday, June 5th, 2026 - 1:00 AM (America/Chicago)  
**Duration:** ~22 minutes  
**Status:** ✅ COMPLETE — All 4 skills built and committed

---

## Skills Delivered

### 1. green-lead-scraper ✅
**Purpose:** Scrape business leads from websites/directories, enrich contacts, deduplicate

**Files:**
- `SKILL.md` — Usage guide and pipeline overview
- `scripts/scrape.py` — Main scraper (fetch, parse, enrich via Hunter/Apollo)
- `scripts/dedup.py` — Deduplication by domain/phone/name with merge strategies
- `scripts/config.json` — Configurable selectors, rate limits, API keys
- `references/selectors.md` — Pre-built CSS selectors for Yelp, Yellow Pages, BBB
- `references/robots-policy.md` — robots.txt compliance rules

**Usage:**
```bash
python scripts/scrape.py --source urls.csv --format csv --output leads.json
python scripts/scrape.py --source leads.json --enrich hunter --output enriched.json
python scripts/dedup.py --input enriched.json --key domain --output final.json
```

### 2. green-email-outreach ✅
**Purpose:** Systack-branded email outreach with drip follow-ups, tracking, reporting

**Files:**
- `SKILL.md` — Usage guide, template variables, compliance notes
- `scripts/outreach.js` — Main send engine with drip support
- `scripts/report.js` — Campaign analytics and stats
- `scripts/config.json` — Rate limits, suppression, tracking
- `templates/systack-intro.txt` — Initial outreach template
- `templates/systack-followup.txt` — Day 3 follow-up
- `templates/systack-final.txt` — Day 7 final touch
- `references/deliverability.md` — Domain warmup, SPF/DKIM/DMARC

**Usage:**
```bash
export RESEND_API_KEY=re_xxx
node scripts/outreach.js --source leads.csv --template templates/systack-intro.txt
node scripts/outreach.js --drip --days 3 --template templates/systack-followup.txt
node scripts/report.js --log send-log.csv
```

### 3. green-n8n-monitor ✅
**Purpose:** Monitor n8n workflows for failures and alert Green

**Files:**
- `SKILL.md` — Usage guide, alert channels, output format
- `scripts/monitor.js` — Pings n8n API, filters failures, sends alerts
- `scripts/config.json` — n8n URL, API key, alert settings
- `references/n8n-api.md` — n8n API endpoint documentation

**Usage:**
```bash
export N8N_API_KEY=n8n_api_xxx
export N8N_URL=https://n8n.systack.net
node scripts/monitor.js
node scripts/monitor.js --webhook https://hooks.slack.com/xxx
node scripts/monitor.js --dashboard dashboard.html --interval 300000
```

### 4. green-content-calendar ✅
**Purpose:** Auto-generate content calendar from pipeline/lead data

**Files:**
- `SKILL.md` — Usage guide, input/output formats
- `scripts/generate.py` — Analyzes data, suggests topics, schedules content
- `scripts/config.json` — Frequency, content types, output format
- `references/content-types.md` — Guidelines for blog, social, email, video
- `references/topic-ideas.md` — Pre-built topic templates by category

**Usage:**
```bash
python scripts/generate.py --input leads.json --output calendar.md
python scripts/generate.py --input leads.json --frequency weekly --weeks 4 --format csv
python scripts/generate.py --input pipeline.json --analyze-only
```

---

## Commit Details

```
commit 5da1a94
Author: Phillip Lowe
Date:   Fri Jun 5 01:22:00 2026 -0500

feat(skills): add Green custom skills for business automation

- green-lead-scraper: Python scraper with enrichment, dedup, CSV/JSON export
- green-email-outreach: Systack-branded outreach with drip, tracking, reporting
- green-n8n-monitor: n8n workflow failure alerts via email/webhook/dashboard
- green-content-calendar: Auto-generate content calendar from pipeline data

All skills include SKILL.md, scripts, config, and reference docs.
Built in ~22 minutes, 4/4 complete.
```

**Files changed:** 23 new files, 2,038 insertions

---

## Time Breakdown

| Phase | Time | Details |
|-------|------|---------|
| Research | 3 min | Reviewed cold-email-engine, linkedin-lead-gen-outreach, n8n-workflow-automation, productivity-automation-kit patterns |
| Lead Scraper | 5 min | scrape.py, dedup.py, config.json, references |
| Email Outreach | 5 min | outreach.js, report.js, 3 templates, references |
| n8n Monitor | 4 min | monitor.js, dashboard gen, config.json, references |
| Content Calendar | 4 min | generate.py, topic analysis, scheduling, references |
| Commit | 1 min | Git add, commit with detailed message |

**Total: ~22 minutes** (well within 30-minute limit)

---

## Next Steps / Enhancements

1. **Playwright Integration** — Add JS-rendered site support to lead scraper
2. **Google Sheets Export** — Connect content calendar to Sheets API
3. **Slack Notifications** — Add Slack block format to n8n monitor alerts
4. **A/B Testing** — Add variant tracking to email outreach
5. **Integration Testing** — Verify all 4 skills work together end-to-end

---

## Notes

- All skills follow the ClawHub skill structure: `SKILL.md`, `scripts/`, `references/`
- Configurable via JSON config files + environment variables
- Built on top of existing patterns (cold-email-engine, n8n-workflow-automation)
- Tailored for Green's Systack business automation workflow
