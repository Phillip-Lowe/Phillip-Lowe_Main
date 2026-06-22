#!/usr/bin/env python3
"""
One-shot script: Backfill PLAN_ID headers on all existing plan files.

Reads plan files from memory/plans/, extracts a stable PLAN_ID from the filename,
and inserts a PLAN_ID: line after the title/header line if missing.

Usage: python3 backfill-plan-ids.py [--dry-run]
"""

from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from typing import Optional

PLANS_DIR = Path("/Users/philliplowe/.openclaw/workspaces/sol/memory/plans")

def extract_id_from_filename(filename: str) -> str | None:
    """Extract PLAN ID from filename patterns."""
    # Pattern 1: PLAN-XXX-suffix.md → PLAN-XXX
    m = re.match(r'(PLAN-[^.-]+(?:-\w+)?)', filename)
    if m:
        return m.group(0)
    # Pattern 2: PLAN-###.md → PLAN-###
    m = re.match(r'(PLAN-\d+)', filename)
    if m:
        return m.group(0)
    # Pattern 3: UTOPIA-DELI-STATUS-... → use as-is
    m = re.match(r'(\w+-\w+-\w+)', filename)
    if m:
        return m.group(0).upper()
    return None


def extract_id_from_content(content: str) -> str | None:
    """Extract PLAN ID from existing content."""
    # Try **ID:** pattern first
    m = re.search(r'\*\*ID:\*\*\s*(PLAN-\S+)', content)
    if m:
        return m.group(1)
    # Try # PLAN-XXX: pattern
    m = re.search(r'^#\s*(PLAN-[\w-]+):', content, re.M)
    if m:
        return m.group(1)
    # Try PLAN_ID: pattern (already has it)
    m = re.search(r'^PLAN_ID:\s*(PLAN-\S+)', content, re.M)
    if m:
        return m.group(1)
    return None


def has_plan_id(content: str) -> bool:
    """Check if PLAN_ID header already exists."""
    return bool(re.search(r'^PLAN_ID:\s', content, re.M))


def insert_plan_id(content: str, plan_id: str) -> str:
    """Insert PLAN_ID line after the title line."""
    lines = content.split('\n')
    # Find title line (# Header) and insert after it
    for i, line in enumerate(lines):
        if re.match(r'^#\s+', line):
            lines.insert(i + 1, f'\n**PLAN_ID:** {plan_id}')
            return '\n'.join(lines)
    # If no title line, prepend
    return f'**PLAN_ID:** {plan_id}\n\n{content}'


def main():
    dry_run = '--dry-run' in sys.argv
    files = sorted(PLANS_DIR.glob('*.md'))
    updated = 0
    skipped = 0
    
    for filepath in files:
        content = filepath.read_text(encoding='utf-8')
        
        if has_plan_id(content):
            skipped += 1
            continue
        
        # Try to extract ID from content first, then filename
        plan_id = extract_id_from_content(content) or extract_id_from_filename(filepath.stem)
        
        if not plan_id:
            print(f"⚠️  Cannot extract ID: {filepath.name}")
            skipped += 1
            continue
        
        new_content = insert_plan_id(content, plan_id)
        
        if dry_run:
            print(f"[DRY RUN] Would add PLAN_ID: {plan_id} → {filepath.name}")
        else:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"✅ Added PLAN_ID: {plan_id} → {filepath.name}")
        
        updated += 1
    
    print(f"\nDone. Updated: {updated}, Skipped: {skipped}, Total: {len(files)}")


if __name__ == "__main__":
    main()
