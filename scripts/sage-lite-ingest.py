#!/usr/bin/env python3
"""
SAGE-Lite Graph Memory — Batch Ingest
Reads memory/*.md files, extracts triples via writer, writes to graph DB.

Usage:
  python3 sage-lite-ingest.py                          # ingest all memory files
  python3 sage-lite-ingest.py --file memory/2026-05-17.md
  python3 sage-lite-ingest.py --since 2026-05-10       # only recent files
"""
import sqlite3
import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "sage-graph.db"
MEMORY_DIR = Path(__file__).resolve().parent.parent / "memory"

def chunk_text(text: str, max_chars: int = 4000) -> List[str]:
    """Split text into overlapping chunks for extraction."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        # Try to break at paragraph or sentence
        if end < len(text):
            # Look for paragraph break
            para_break = text.rfind('\n\n', start, end)
            if para_break > start + max_chars * 0.5:
                end = para_break + 2
            else:
                # Look for sentence end
                sent_break = max(
                    text.rfind('. ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('! ', start, end)
                )
                if sent_break > start + max_chars * 0.5:
                    end = sent_break + 2

        chunks.append(text[start:end].strip())
        start = end - 200  # 200 char overlap

    return chunks

def extract_date_from_filename(path: Path) -> str:
    """Parse YYYY-MM-DD from memory filename."""
    match = re.match(r'(\d{4}-\d{2}-\d{2})', path.name)
    return match.group(1) if match else datetime.now().strftime("%Y-%m-%d")

def ingest_file(db_path: Path, file_path: Path, model: str = "qwen3.5:9b", dry_run: bool = False):
    """Ingest a single memory file."""
    from sage_lite_writer import extract_triples, write_triples

    text = file_path.read_text()
    date_tag = extract_date_from_filename(file_path)

    # Extract structured sections
    sections = re.split(r'\n##+\s+', text)
    if len(sections) == 1:
        sections = [text]

    print(f"📥 Ingesting: {file_path.name}")
    print(f"   Sections: {len(sections)}")

    all_triples = []
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        chunks = chunk_text(section.strip(), max_chars=4000)
        for j, chunk in enumerate(chunks):
            triples = extract_triples(chunk, model=model)
            all_triples.extend(triples)
            print(f"   Section {i+1}, chunk {j+1}: {len(triples)} triples")

    print(f"   Total triples: {len(all_triples)}")

    if dry_run:
        print("   (Dry run — not writing to DB)")
        return

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    write_triples(conn, all_triples, source=f"memory/{file_path.name}")
    conn.commit()
    conn.close()
    print(f"   ✅ Written to graph")

def main():
    parser = argparse.ArgumentParser(description="SAGE-Lite Ingest: batch import memory files")
    parser.add_argument("--file", type=Path, help="Specific file to ingest")
    parser.add_argument("--since", help="Ingest files from this date (YYYY-MM-DD)")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be extracted")
    parser.add_argument("--cloud", action="store_true", help="Use cloud model for extraction")
    args = parser.parse_args()

    if not MEMORY_DIR.exists():
        print(f"❌ Memory directory not found: {MEMORY_DIR}")
        return

    # Resolve model
    model = "deepseek-v4-flash:cloud" if args.cloud else args.model

    if args.file:
        ingest_file(args.db, args.file, model=model, dry_run=args.dry_run)
    else:
        files = sorted(MEMORY_DIR.glob("*.md"))
        if args.since:
            files = [f for f in files if extract_date_from_filename(f) >= args.since]

        print(f"📦 Found {len(files)} memory files to ingest")
        for f in files:
            ingest_file(args.db, f, model=model, dry_run=args.dry_run)
            print()

if __name__ == "__main__":
    main()
