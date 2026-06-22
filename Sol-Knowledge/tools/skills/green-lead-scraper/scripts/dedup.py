#!/usr/bin/env python3
"""
Green Lead Scraper — Deduplication

Usage:
    python dedup.py --input leads.json --key domain --output final.json
    python dedup.py --input leads.json --key phone --merge-strategy best --output final.json
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def normalize(value: Any) -> str:
    """Normalize a field value for deduplication."""
    if not value:
        return ""
    v = str(value).lower().strip()
    # Remove common prefixes/suffixes
    for prefix in ["https://", "http://", "www.", "tel:", "mailto:"]:
        v = v.removeprefix(prefix)
    return v


def merge_records(records: List[Dict[str, Any]], strategy: str) -> Dict[str, Any]:
    """Merge duplicate records based on strategy."""
    if strategy == "first":
        return records[0]
    elif strategy == "last":
        return records[-1]
    elif strategy == "best":
        # Prefer records with more filled fields
        best = records[0]
        best_score = sum(1 for v in best.values() if v is not None and v != "")
        for record in records[1:]:
            score = sum(1 for v in record.values() if v is not None and v != "")
            if score > best_score:
                best = record
                best_score = score
        return best
    elif strategy == "merge":
        merged: Dict[str, Any] = {}
        for record in records:
            for key, value in record.items():
                if value is not None and value != "" and (key not in merged or merged[key] == ""):
                    merged[key] = value
                elif key == "services" and isinstance(value, list) and key in merged:
                    # Merge lists uniquely
                    existing = merged[key] if isinstance(merged[key], list) else []
                    merged[key] = list(set(existing + value))
        return merged
    else:
        return records[0]


def deduplicate(leads: List[Dict[str, Any]], key: str, strategy: str) -> List[Dict[str, Any]]:
    """Deduplicate leads by a given key."""
    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for lead in leads:
        value = normalize(lead.get(key, ""))
        if value:
            groups[value].append(lead)

    deduped: List[Dict[str, Any]] = []
    for group in groups.values():
        if len(group) == 1:
            deduped.append(group[0])
        else:
            merged = merge_records(group, strategy)
            merged["_duplicate_count"] = len(group)
            merged["_merged_at"] = datetime.utcnow().isoformat() + "Z"
            deduped.append(merged)

    # Also add leads that didn't have the key
    ungrouped = [lead for lead in leads if not normalize(lead.get(key, ""))]
    return deduped + ungrouped


def main() -> int:
    parser = argparse.ArgumentParser(description="Deduplicate leads")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file")
    parser.add_argument("--key", "-k", default="domain", help="Deduplication key")
    parser.add_argument("--merge-strategy", "-m", choices=["first", "last", "best", "merge"],
                        default="merge", help="Merge strategy for duplicates")
    parser.add_argument("--output", "-o", required=True, help="Output JSON file")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        leads = json.load(f)

    print(f"🟢 Deduplicating {len(leads)} leads by '{args.key}' (strategy: {args.merge_strategy})")
    deduped = deduplicate(leads, args.key, args.merge_strategy)
    removed = len(leads) - len(deduped)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)

    print(f"  ✅ {len(deduped)} leads after deduplication")
    print(f"  🗑️  {removed} duplicates removed")
    print(f"📁 Saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
