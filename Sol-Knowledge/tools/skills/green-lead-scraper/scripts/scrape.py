#!/usr/bin/env python3
"""
Green Lead Scraper — Main scraper engine

Usage:
    python scrape.py --source <url|csv|json> --output leads.json
    python scrape.py --source urls.csv --format csv --output leads.json
    python scrape.py --source leads.json --enrich hunter --output enriched.json
"""

import argparse
import csv
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


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


def fetch_html(url: str, config: Dict[str, Any]) -> Optional[str]:
    """Fetch HTML from a URL with rate limiting and user-agent."""
    headers = {
        "User-Agent": config.get("userAgent", "GreenBot/1.0 (+https://green.example.com/bot)"),
        "Accept": "text/html,application/xhtml+xml",
    }
    delay = config.get("delayMs", 1500) / 1000
    time.sleep(delay)
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  ⚠️  Failed to fetch {url}: {e}")
        return None


def parse_page(html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
    """Parse a page using CSS selectors."""
    soup = BeautifulSoup(html, "lxml")
    data: Dict[str, Any] = {}
    for field, selector in selectors.items():
        el = soup.select_one(selector)
        data[field] = el.get_text(strip=True) if el else None
    return data


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc
    except Exception:
        return None


def scrape_url(url: str, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Scrape a single URL and return lead data."""
    selectors = config.get("selectors", {
        "name": "h1, .business-name, [data-testid='business-name']",
        "phone": "a[href^='tel:'], .phone, [data-testid='phone']",
        "email": "a[href^='mailto:'], .email",
        "address": ".address, [data-testid='address']",
        "rating": ".rating, [data-testid='rating']",
        "review_count": ".review-count, [data-testid='review-count']",
    })
    html = fetch_html(url, config)
    if not html:
        return None
    data = parse_page(html, selectors)
    # Clean up fields
    phone = data.get("phone", "")
    if phone and phone.startswith("tel:"):
        data["phone"] = phone[4:]
    email = data.get("email", "")
    if email and email.startswith("mailto:"):
        data["email"] = email[7:]
    domain = extract_domain(url)
    data["domain"] = domain
    data["source_url"] = url
    data["scraped_at"] = datetime.utcnow().isoformat() + "Z"
    data["enriched"] = False
    return data


def scrape_from_csv(filepath: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape URLs from a CSV file."""
    leads: List[Dict[str, Any]] = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("url", "").strip()
            if not url:
                continue
            print(f"Scraping: {url}")
            lead = scrape_url(url, config)
            if lead:
                leads.append(lead)
                print(f"  ✅ {lead.get('name', 'N/A')} | {lead.get('phone', 'N/A')}")
    return leads


def scrape_from_json(filepath: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape URLs from a JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    leads: List[Dict[str, Any]] = []
    for item in data:
        url = item.get("url", "").strip()
        if not url:
            continue
        print(f"Scraping: {url}")
        lead = scrape_url(url, config)
        if lead:
            lead.update(item)  # merge any extra fields
            leads.append(lead)
            print(f"  ✅ {lead.get('name', 'N/A')} | {lead.get('phone', 'N/A')}")
    return leads


def enrich_leads(leads: List[Dict[str, Any]], enricher: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Enrich leads using specified enrichment service."""
    if enricher == "hunter":
        api_key = os.environ.get("HUNTER_API_KEY") or config.get("hunterApiKey")
        if not api_key:
            print("⚠️  HUNTER_API_KEY not set. Skipping enrichment.")
            return leads
        for lead in leads:
            domain = lead.get("domain")
            if not domain or lead.get("enriched"):
                continue
            try:
                resp = requests.get(
                    "https://api.hunter.io/v2/domain-search",
                    params={"domain": domain, "api_key": api_key},
                    timeout=10,
                )
                resp.raise_for_status()
                result = resp.json()
                emails = result.get("data", {}).get("emails", [])
                if emails:
                    lead["email"] = emails[0]["value"]
                    lead["enriched"] = True
                    print(f"  🔍 {domain} → {lead['email']}")
            except requests.RequestException as e:
                print(f"  ⚠️  Enrichment failed for {domain}: {e}")
            time.sleep(1)
    elif enricher == "apollo":
        api_key = os.environ.get("APOLLO_API_KEY") or config.get("apolloApiKey")
        if not api_key:
            print("⚠️  APOLLO_API_KEY not set. Skipping enrichment.")
            return leads
        for lead in leads:
            domain = lead.get("domain")
            if not domain or lead.get("enriched"):
                continue
            try:
                resp = requests.get(
                    "https://api.apollo.io/v1/people/match",
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={"q_organization_domains": domain},
                    timeout=10,
                )
                resp.raise_for_status()
                result = resp.json()
                people = result.get("people", [])
                if people:
                    lead["email"] = people[0].get("email")
                    lead["title"] = people[0].get("title")
                    lead["enriched"] = True
                    print(f"  🔍 {domain} → {lead.get('email', 'N/A')}")
            except requests.RequestException as e:
                print(f"  ⚠️  Enrichment failed for {domain}: {e}")
            time.sleep(1)
    return leads


def save_leads(leads: List[Dict[str, Any]], output: str) -> None:
    """Save leads to JSON file."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    print(f"\n📁 Saved {len(leads)} leads to {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Green Lead Scraper")
    parser.add_argument("--source", "-s", required=True, help="Source URL, CSV, or JSON file")
    parser.add_argument("--format", "-f", choices=["url", "csv", "json"], default="url",
                        help="Source format (default: url)")
    parser.add_argument("--output", "-o", default="leads.json", help="Output JSON file")
    parser.add_argument("--enrich", choices=["hunter", "apollo", "none"], default="none",
                        help="Enrichment service")
    parser.add_argument("--config", "-c", help="Config JSON path")
    args = parser.parse_args()

    config = load_config(args.config)
    leads: List[Dict[str, Any]] = []

    print(f"🟢 Green Lead Scraper")
    print(f"Source: {args.source} | Format: {args.format} | Enrich: {args.enrich}\n")

    if args.format == "url":
        print(f"Scraping: {args.source}")
        lead = scrape_url(args.source, config)
        if lead:
            leads.append(lead)
            print(f"  ✅ {lead.get('name', 'N/A')} | {lead.get('phone', 'N/A')}")
    elif args.format == "csv":
        leads = scrape_from_csv(args.source, config)
    elif args.format == "json":
        leads = scrape_from_json(args.source, config)

    if args.enrich != "none":
        print(f"\n🔍 Enriching {len(leads)} leads via {args.enrich}...")
        leads = enrich_leads(leads, args.enrich, config)

    save_leads(leads, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
