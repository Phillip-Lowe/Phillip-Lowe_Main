---
name: green-content-calendar
description: Auto-generate a content calendar from Green's pipeline data. Reads lead/prospect data, suggests content topics, assigns publish dates, and outputs a structured calendar in Markdown or CSV. Integrates with lead scraper output.
---

# Green Content Calendar

Auto-generate a content calendar from Green's pipeline data. Reads lead/prospect data, suggests content topics, assigns publish dates, and outputs a structured calendar in Markdown or CSV.

## Pipeline

1. **Load data** — Read leads, prospects, or pipeline data (JSON/CSV)
2. **Analyze** — Identify common pain points, industries, and signals
3. **Generate topics** — Suggest content based on lead data trends
4. **Schedule** — Assign publish dates based on frequency and urgency
5. **Output** — Markdown calendar, CSV, or JSON for integration

## Requirements

- Python 3.10+
- Input data from Green lead scraper or manual CSV
- Optional: OpenAI API key for topic generation

## Quick Start

```bash
# Generate from lead data
python scripts/generate.py --input leads.json --output calendar.md

# Generate with specific frequency
python scripts/generate.py --input leads.json --frequency weekly --weeks 4 --output calendar.md

# Export as CSV
python scripts/generate.py --input leads.json --format csv --output calendar.csv

# Generate topics from pipeline trends
python scripts/generate.py --input pipeline.json --analyze-only
```

## Input Formats

### From Lead Scraper (JSON)
```json
[
  {
    "name": "Green Landscaping",
    "services": ["Lawn Care", "Tree Trimming"],
    "pain_point": "manual scheduling"
  }
]
```

### Manual CSV
```csv
company,industry,pain_point,location
Green Landscaping,Home Services,manual scheduling,Springfield
```

## Configuration

Edit `scripts/config.json`:
- `frequency`: `daily`, `weekly`, `biweekly`
- `contentTypes`: ["blog", "social", "email", "video"]
- `topicsPerWeek`: 3
- `outputFormat`: `markdown`, `csv`, `json`
- `openaiApiKey`: Optional, for AI-generated topics

## Output Formats

### Markdown Calendar
```markdown
# Content Calendar — June 2026

## Week of June 1

### Monday — Blog Post
**Title:** How Home Service Businesses Can Automate Scheduling
**Audience:** Landscaping, cleaning, HVAC companies
**CTA:** Book a free demo

### Wednesday — Social Post
**Platform:** LinkedIn
**Topic:** "3 signs your business needs automation"
**Format:** Carousel

### Friday — Email Newsletter
**Subject:** This week in automation
**Segments:** All prospects
```

### CSV
```csv
week,date,content_type,title,audience,status
current,2026-06-01,blog,How Home Service Businesses Can Automate Scheduling,Home Services,draft
current,2026-06-03,social,3 signs your business needs automation,LinkedIn,draft
```

## Topic Suggestions

The analyzer suggests topics based on:
- **Pain points** — Most common issues across leads
- **Industries** — Content tailored to top industries
- **Seasonality** — Time-relevant topics (holidays, trends)
- **Competitor gaps** — What competitors aren't covering

## Scripts

- `scripts/generate.py` — Main calendar generator
- `scripts/analyze.py` — Data analysis and topic suggestions
- `scripts/config.json` — Configuration

## References

- See `references/content-types.md` for content format guidelines
- See `references/topic-ideas.md` for pre-built topic templates
