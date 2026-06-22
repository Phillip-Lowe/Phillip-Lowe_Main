#!/usr/bin/env python3
"""
Green Content Calendar — Auto-generate from pipeline data

Usage:
    python generate.py --input leads.json --output calendar.md
    python generate.py --input leads.json --frequency weekly --weeks 4 --output calendar.md
    python generate.py --input leads.json --format csv --output calendar.csv
    python generate.py --input pipeline.json --analyze-only
"""

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_config(path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    if path and Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    default = Path(__file__).parent / "config.json"
    if default.exists():
        with open(default, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_data(filepath: str) -> List[Dict[str, Any]]:
    """Load data from JSON or CSV file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")
    
    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif path.suffix == ".csv":
        rows = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
        return rows
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def analyze_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze lead data and extract insights."""
    industries = Counter()
    pain_points = Counter()
    services = Counter()
    locations = Counter()
    
    for item in data:
        # Extract industry
        industry = item.get("industry", item.get("category", "Unknown"))
        if industry:
            industries[industry] += 1
        
        # Extract pain points
        pain = item.get("pain_point", item.get("pain", ""))
        if pain:
            pain_points[pain] += 1
        
        # Extract services
        svc = item.get("services", [])
        if isinstance(svc, str):
            svc = [s.strip() for s in svc.split(",")]
        for s in svc:
            if s:
                services[s] += 1
        
        # Extract location
        loc = item.get("location", item.get("city", ""))
        if loc:
            locations[loc] += 1
    
    return {
        "total_leads": len(data),
        "top_industries": industries.most_common(5),
        "top_pain_points": pain_points.most_common(5),
        "top_services": services.most_common(5),
        "top_locations": locations.most_common(5),
    }


def suggest_topics(analysis: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate content topic suggestions based on analysis."""
    topics = []
    content_types = config.get("contentTypes", ["blog", "social", "email"])
    
    # Pain point based topics
    for pain, count in analysis["top_pain_points"]:
        topics.append({
            "title": f"How to Solve {pain.title()}",
            "angle": "pain_point",
            "audience": "general",
            "content_type": "blog" if "blog" in content_types else content_types[0],
        })
    
    # Industry based topics
    for industry, count in analysis["top_industries"]:
        topics.append({
            "title": f"Automation Trends in {industry.title()}",
            "angle": "industry",
            "audience": industry,
            "content_type": "social" if "social" in content_types else content_types[0],
        })
    
    # Service based topics
    for service, count in analysis["top_services"]:
        topics.append({
            "title": f"Why {service.title()} Businesses Need Automation",
            "angle": "service",
            "audience": service,
            "content_type": "email" if "email" in content_types else content_types[0],
        })
    
    return topics


def schedule_content(topics: List[Dict[str, str]], frequency: str, weeks: int, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """Schedule topics across weeks with dates."""
    if start_date is None:
        start_date = datetime.now()
    
    # Align to Monday
    start_date = start_date - timedelta(days=start_date.weekday())
    
    if frequency == "daily":
        days_per_week = 5
    elif frequency == "weekly":
        days_per_week = 1
    elif frequency == "biweekly":
        days_per_week = 1
        weeks = weeks // 2
    else:
        days_per_week = 3
    
    scheduled = []
    topic_idx = 0
    
    for week in range(weeks):
        week_start = start_date + timedelta(weeks=week)
        
        for day in range(days_per_week):
            if topic_idx >= len(topics):
                break
            
            publish_date = week_start + timedelta(days=day)
            topic = topics[topic_idx]
            
            scheduled.append({
                "week": f"Week of {week_start.strftime('%b %d')}",
                "date": publish_date.strftime("%Y-%m-%d"),
                "day": publish_date.strftime("%A"),
                "content_type": topic["content_type"],
                "title": topic["title"],
                "audience": topic["audience"],
                "status": "draft",
            })
            
            topic_idx += 1
    
    return scheduled


def generate_markdown_calendar(scheduled: List[Dict[str, Any]], analysis: Dict[str, Any]) -> str:
    """Generate Markdown content calendar."""
    lines = [
        "# Green Content Calendar",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Based on:** {analysis['total_leads']} leads",
        "",
        "## Pipeline Insights",
        "",
        f"- **Top Industry:** {analysis['top_industries'][0][0] if analysis['top_industries'] else 'N/A'}",
        f"- **Top Pain Point:** {analysis['top_pain_points'][0][0] if analysis['top_pain_points'] else 'N/A'}",
        f"- **Top Service:** {analysis['top_services'][0][0] if analysis['top_services'] else 'N/A'}",
        "",
        "## Content Schedule",
        "",
    ]
    
    current_week = None
    for item in scheduled:
        if item["week"] != current_week:
            current_week = item["week"]
            lines.append(f"### {current_week}")
            lines.append("")
        
        lines.append(f"#### {item['day']} — {item['content_type'].title()}")
        lines.append(f"**Title:** {item['title']}")
        lines.append(f"**Audience:** {item['audience'].title()}")
        lines.append(f"**Status:** {item['status']}")
        lines.append("")
    
    lines.append("---")
    lines.append("*Auto-generated by Green Content Calendar*")
    
    return "\n".join(lines)


def save_csv_calendar(scheduled: List[Dict[str, Any]], output: str) -> None:
    """Save calendar as CSV."""
    if not scheduled:
        return
    
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=scheduled[0].keys())
        writer.writeheader()
        writer.writerows(scheduled)
    print(f"📁 Saved CSV to {output}")


def save_json_calendar(scheduled: List[Dict[str, Any]], output: str) -> None:
    """Save calendar as JSON."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(scheduled, f, ensure_ascii=False, indent=2)
    print(f"📁 Saved JSON to {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Green Content Calendar Generator")
    parser.add_argument("--input", "-i", required=True, help="Input data file (JSON or CSV)")
    parser.add_argument("--output", "-o", default="calendar.md", help="Output file")
    parser.add_argument("--format", "-f", choices=["markdown", "csv", "json"], default="markdown",
                        help="Output format")
    parser.add_argument("--frequency", choices=["daily", "weekly", "biweekly"], default="weekly",
                        help="Publishing frequency")
    parser.add_argument("--weeks", type=int, default=4, help="Number of weeks")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't generate calendar")
    parser.add_argument("--config", "-c", help="Config JSON path")
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    print(f"🟢 Green Content Calendar")
    print(f"Loading data from {args.input}...\n")
    
    try:
        data = load_data(args.input)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return 1
    
    print(f"Loaded {len(data)} records. Analyzing...\n")
    analysis = analyze_data(data)
    
    print("📊 Pipeline Insights:")
    print(f"  Total leads: {analysis['total_leads']}")
    print(f"  Top industries: {', '.join(f'{k} ({v})' for k, v in analysis['top_industries'])}")
    print(f"  Top pain points: {', '.join(f'{k} ({v})' for k, v in analysis['top_pain_points'])}")
    print(f"  Top services: {', '.join(f'{k} ({v})' for k, v in analysis['top_services'])}")
    print()
    
    if args.analyze_only:
        return 0
    
    topics = suggest_topics(analysis, config)
    scheduled = schedule_content(topics, args.frequency, args.weeks)
    
    print(f"📅 Scheduled {len(scheduled)} content pieces over {args.weeks} weeks\n")
    
    if args.format == "markdown":
        markdown = generate_markdown_calendar(scheduled, analysis)
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"📁 Saved Markdown to {args.output}")
    elif args.format == "csv":
        save_csv_calendar(scheduled, args.output)
    elif args.format == "json":
        save_json_calendar(scheduled, args.output)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
