#!/usr/bin/env python3
"""
SAGE-Lite Graph Memory — Writer Engine
Extracts entity-relation-object triples from text via Ollama,
writes to graph DB with deduplication.

Usage:
  python3 sage-lite-writer.py --text "Alice works at Google."
  python3 sage-lite-writer.py --file memory/2026-05-17.md
  cat document.txt | python3 sage-lite-writer.py --stdin
"""
import sqlite3
import json
import re
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "sage-graph.db"

WRITER_PROMPT_LOCAL = """You are a knowledge graph extraction engine. Read the text and output ONLY a JSON array of entity-relation-object triples.

Rules:
- Each triple: {{"subject": "...", "relation": "...", "object": "..."}}
- Use these relations when applicable: causes, part_of, leads_to, similar_to, contradicts, temporal_before, authored_by, located_in, works_for, mentioned_in, inspired_by, field_of, helps_with, uses, creates, requires, inhibits, enables
- Entities can be people, places, concepts, events, documents, organizations, products, technologies
- Output ONLY valid JSON array. No explanation, no markdown code blocks.
- If no triples found, output: []

Text:
{text}
"""

WRITER_PROMPT_CLOUD = """You are a knowledge graph extraction engine specializing in complex technical and scientific text. Read the text and output ONLY a JSON array of entity-relation-object triples.

Rules:
- Each triple: {{"subject": "...", "relation": "...", "object": "...", "confidence": 0.0-1.0}}
- Relations: causes, part_of, leads_to, similar_to, contradicts, temporal_before, authored_by, located_in, works_for, mentioned_in, inspired_by, field_of, helps_with, uses, creates, requires, inhibits, enables, implements, extends, evaluates, compares_to, depends_on, alternative_to
- Capture implicit relationships, not just explicit ones
- Identify domain-specific entities (algorithms, papers, systems, metrics)
- Output ONLY valid JSON array
- If no triples found, output: []

Text:
{text}
"""

def call_ollama(prompt: str, model: str = "qwen3.5:9b", temperature: float = 0.2, timeout: int = 300) -> str:
    """Call Ollama generate API."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 2048}
    }
    import urllib.request
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
        return data.get("response", "")

def extract_triples(text: str, model: str = "qwen3.5:9b", use_cloud: bool = False) -> List[Dict]:
    """Extract triples from text using Ollama."""
    prompt = WRITER_PROMPT_CLOUD if use_cloud else WRITER_PROMPT_LOCAL
    prompt = prompt.format(text=text[:8000])  # truncate to 8K

    try:
        raw = call_ollama(prompt, model=model)
    except Exception as e:
        if not use_cloud:
            print(f"⚠️ Local model failed ({e}), trying cloud fallback...")
            return extract_triples(text, model="deepseek-v4-flash:cloud", use_cloud=True)
        raise

    # Extract JSON from response (handle markdown code blocks)
    raw = re.sub(r'^```json\s*', '', raw.strip())
    raw = re.sub(r'```\s*$', '', raw.strip())
    raw = raw.strip()

    try:
        triples = json.loads(raw)
        if not isinstance(triples, list):
            print(f"⚠️ Unexpected response format, expected list got {type(triples)}")
            return []
        return triples
    except json.JSONDecodeError:
        print(f"⚠️ Failed to parse triples JSON. Raw response:\n{raw[:500]}")
        return []

def ensure_node(conn: sqlite3.Connection, name: str, node_type: str = "entity",
                description: str = "", source: str = "", aliases: List[str] = None) -> int:
    """Get or create node, return id."""
    c = conn.cursor()
    c.execute("SELECT id, aliases, description FROM nodes WHERE name = ? AND node_type = ?",
              (name, node_type))
    row = c.fetchone()
    if row:
        node_id, old_aliases, old_desc = row
        # Merge aliases
        if aliases:
            merged = set(json.loads(old_aliases or "[]"))
            merged.update(aliases)
            c.execute("UPDATE nodes SET aliases = ?, updated_at = datetime('now') WHERE id = ?",
                      (json.dumps(list(merged)), node_id))
        # Merge description if longer/new
        if description and len(description) > len(old_desc or ""):
            c.execute("UPDATE nodes SET description = ?, updated_at = datetime('now') WHERE id = ?",
                      (description, node_id))
        return node_id

    c.execute("""
        INSERT INTO nodes (node_type, name, aliases, description, source)
        VALUES (?, ?, ?, ?, ?)
    """, (node_type, name, json.dumps(aliases or []), description, source))
    return c.lastrowid

def ensure_edge(conn: sqlite3.Connection, source_id: int, target_id: int,
                relation: str, strength: float = 1.0, evidence: str = "",
                source: str = "") -> int:
    """Get or create edge, return id. Boost strength if exists."""
    c = conn.cursor()
    c.execute("SELECT id, strength FROM edges WHERE source_id = ? AND target_id = ? AND relation = ?",
              (source_id, target_id, relation))
    row = c.fetchone()
    if row:
        edge_id, old_strength = row
        new_strength = min(1.0, old_strength + 0.05)
        c.execute("UPDATE edges SET strength = ?, updated_at = datetime('now') WHERE id = ?",
                  (new_strength, edge_id))
        return edge_id

    c.execute("""
        INSERT INTO edges (source_id, target_id, relation, strength, evidence, source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source_id, target_id, relation, strength, evidence, source))
    return c.lastrowid

def infer_node_type(name: str, relation: str, is_object: bool = False) -> str:
    """Heuristic node type from name/relation."""
    name_lower = name.lower()
    if any(x in name_lower for x in ["algorithm", "model", "system", "framework", "engine", "method"]):
        return "concept"
    if any(x in name_lower for x in ["university", "company", "inc", "corp", "lab", "institute", "school"]):
        return "entity"
    if relation in ["authored_by", "works_for"] and not is_object:
        return "entity"
    if relation in ["field_of", "helps_with", "uses", "creates", "implements"]:
        return "concept"
    return "entity"

def write_triples(conn: sqlite3.Connection, triples: List[Dict], source: str = ""):
    """Write extracted triples to graph."""
    nodes_added = 0
    edges_added = 0
    edges_boosted = 0

    for t in triples:
        subj = t.get("subject", "").strip()
        rel = t.get("relation", "").strip()
        obj = t.get("object", "").strip()
        conf = t.get("confidence", 0.8)
        if not subj or not rel or not obj:
            continue

        subj_type = infer_node_type(subj, rel, is_object=False)
        obj_type = infer_node_type(obj, rel, is_object=True)

        subj_id = ensure_node(conn, subj, subj_type, source=source)
        obj_id = ensure_node(conn, obj, obj_type, source=source)

        c = conn.cursor()
        c.execute("SELECT id FROM edges WHERE source_id = ? AND target_id = ? AND relation = ?",
                  (subj_id, obj_id, rel))
        exists = c.fetchone()

        if exists:
            edges_boosted += 1
        else:
            edges_added += 1

        ensure_edge(conn, subj_id, obj_id, rel, strength=min(1.0, conf), source=source)

    print(f"   Nodes ensured: {len(set(t.get('subject','') + '|' + t.get('object','') for t in triples))}")
    print(f"   Edges added: {edges_added}, boosted: {edges_boosted}")

def main():
    parser = argparse.ArgumentParser(description="SAGE-Lite Writer: extract triples from text")
    parser.add_argument("--text", help="Text to extract from")
    parser.add_argument("--file", type=Path, help="File to read text from")
    parser.add_argument("--stdin", action="store_true", help="Read text from stdin")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite DB path")
    parser.add_argument("--model", default="qwen3.5:9b", help="Ollama model for extraction")
    parser.add_argument("--cloud", action="store_true", help="Force cloud model")
    parser.add_argument("--source", default="manual", help="Source tag for provenance")
    args = parser.parse_args()

    # Get text
    if args.stdin:
        text = sys.stdin.read()
    elif args.file:
        text = args.file.read_text()
    elif args.text:
        text = args.text
    else:
        print("❌ Provide --text, --file, or --stdin")
        sys.exit(1)

    if not text.strip():
        print("❌ Empty input")
        sys.exit(1)

    print(f"📝 SAGE-Lite Writer")
    print(f"   Source: {args.source}")
    print(f"   Model: {args.model} {'(cloud)' if args.cloud else '(local)'}")
    print(f"   Text length: {len(text)} chars")

    # Extract
    triples = extract_triples(text, model=args.model, use_cloud=args.cloud)
    print(f"   Triples extracted: {len(triples)}")
    if not triples:
        print("   ⚠️ No triples found. Skipping DB write.")
        sys.exit(0)

    # Show sample
    for i, t in enumerate(triples[:3]):
        print(f"   Example: ({t.get('subject')}) —[{t.get('relation')}]→ ({t.get('object')})")
    if len(triples) > 3:
        print(f"   ... and {len(triples)-3} more")

    # Write to DB
    conn = sqlite3.connect(str(args.db))
    conn.execute("PRAGMA foreign_keys = ON")
    write_triples(conn, triples, source=args.source)
    conn.commit()
    conn.close()
    print(f"✅ Written to {args.db}")

if __name__ == "__main__":
    main()
