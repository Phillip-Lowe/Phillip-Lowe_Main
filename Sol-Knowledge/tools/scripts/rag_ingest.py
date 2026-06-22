#!/usr/bin/env python3
"""
RAG Ingestion Pipeline for SOL
- Reads markdown files from Obsidian vault + wiki
- Chunks into ~500-token segments
- Generates embeddings via Ollama (nomic-embed-text)
- Stores in Postgres pgvector

Usage:
    python3 rag_ingest.py --full          # Full re-index
    python3 rag_ingest.py --incremental   # Only new/changed files
    python3 rag_ingest.py --verify        # Check counts + test query
"""

import os, sys, argparse, hashlib, json, re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

# ── CONFIG ───────────────────────────────────────────────────────────
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")
DB_PASS = os.environ.get("PGPASSWORD", "")

# Vault paths
VAULT_PATHS = [
    os.path.expanduser("~/.openclaw/wiki"),
    os.path.expanduser("~/.openclaw/workspaces/sol"),
    os.path.expanduser("~/OpenClaw-Wiki"),
]

EXCLUDE_DIRS = {
    "node_modules", ".git", ".obsidian", "_attachments", "_views",
    "main-backup", "reports", ".openclaw", "plugin-skills",
}
INDEXABLE = {".md", ".txt", ".mdx"}

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ── SINGLE DB CONNECTION ────────────────────────────────────────────
_db_conn = None

def get_db():
    global _db_conn
    if _db_conn is None or _db_conn.closed:
        _db_conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASS,
        )
    return _db_conn

def db_commit():
    get_db().commit()

def ensure_table():
    cur = get_db().cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_embeddings (
            id SERIAL PRIMARY KEY,
            source_path TEXT NOT NULL,
            source_type TEXT NOT NULL DEFAULT 'wiki',
            chunk_index INTEGER NOT NULL DEFAULT 0,
            title TEXT,
            content TEXT NOT NULL,
            embedding VECTOR(%s),
            content_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_path, chunk_index)
        );
    """, (EMBEDDING_DIM,))
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_vector
        ON knowledge_embeddings USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);
    """)
    db_commit()
    cur.close()

# ── CHUNKING ──────────────────────────────────────────────────────────
def chunk_markdown(text: str, source_path: str) -> List[Tuple[int, str, str]]:
    lines = text.splitlines()
    title = ""
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    chunks = []
    current = []
    current_len = 0

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        if line_stripped.startswith("#"):
            if current:
                chunks.append("\n".join(current))
                current = []
                current_len = 0
            current.append(line_stripped)
            current_len += len(line_stripped)
            continue

        if current_len + len(line_stripped) + 1 > CHUNK_SIZE and current:
            chunks.append("\n".join(current))
            overlap = []
            olen = 0
            for prev in reversed(current):
                if olen + len(prev) > CHUNK_OVERLAP:
                    break
                overlap.insert(0, prev)
                olen += len(prev) + 1
            current = overlap
            current_len = olen

        current.append(line_stripped)
        current_len += len(line_stripped) + 1

    if current:
        chunks.append("\n".join(current))

    return [(i, title, chunk) for i, chunk in enumerate(chunks) if chunk.strip()]

# ── EMBEDDINGS ────────────────────────────────────────────────────────
def get_embedding(text: str) -> List[float]:
    import urllib.request, urllib.error
    payload = json.dumps({"model": EMBEDDING_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data.get("embedding", [])
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"Ollama embed error {e.code}: {body}")

# ── FILE DISCOVERY ───────────────────────────────────────────────────
def should_exclude(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    for ex in EXCLUDE_DIRS:
        if ex.lower() in parts:
            return True
    return False

def discover_files(vault_paths: List[str]) -> List[Path]:
    files = []
    for vp in vault_paths:
        p = Path(vp)
        if not p.exists():
            continue
        for ext in INDEXABLE:
            for f in p.rglob(f"*{ext}"):
                if not should_exclude(f):
                    files.append(f)
    return files

def file_hash(filepath: Path) -> str:
    h = hashlib.sha256()
    h.update(filepath.read_bytes())
    return h.hexdigest()[:16]

# ── INGEST ───────────────────────────────────────────────────────────
def ingest_file(filepath: Path, source_type: str = "wiki") -> int:
    text = filepath.read_text(encoding="utf-8", errors="replace")
    h = file_hash(filepath)
    path_str = str(filepath.resolve())

    chunks = chunk_markdown(text, path_str)
    if not chunks:
        return 0

    cur = get_db().cursor()
    cur.execute(
        "DELETE FROM knowledge_embeddings WHERE source_path = %s",
        (path_str,)
    )

    inserted = 0
    for idx, title, content in chunks:
        embedding = get_embedding(content)
        if not embedding or len(embedding) != EMBEDDING_DIM:
            print(f"  ⚠️  Bad embedding for {filepath.name} chunk {idx}, skipping")
            continue
        cur.execute("""
            INSERT INTO knowledge_embeddings
            (source_path, source_type, chunk_index, title, content, embedding, content_hash)
            VALUES (%s, %s, %s, %s, %s, %s::vector, %s)
            ON CONFLICT (source_path, chunk_index) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                embedding = EXCLUDED.embedding,
                content_hash = EXCLUDED.content_hash,
                updated_at = CURRENT_TIMESTAMP;
        """, (path_str, source_type, idx, title, content, embedding, h))
        inserted += 1

    db_commit()
    cur.close()
    return inserted

def full_ingest():
    print("Wiping existing embeddings...")
    cur = get_db().cursor()
    cur.execute("TRUNCATE knowledge_embeddings;")
    db_commit()
    cur.close()

    files = discover_files(VAULT_PATHS)
    print(f"Found {len(files)} files\n")

    total_chunks = 0
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {f.name}")
        try:
            n = ingest_file(f)
            print(f"     {n} chunks")
            total_chunks += n
        except Exception as e:
            print(f"     ERROR: {e}")

    print(f"\nDone: {len(files)} files → {total_chunks} chunks")

def incremental_ingest():
    files = discover_files(VAULT_PATHS)
    total, changed = 0, 0

    cur = get_db().cursor()
    cur.execute("SELECT source_path, content_hash FROM knowledge_embeddings")
    known = {r[0]: r[1] for r in cur.fetchall()}
    cur.close()

    for f in files:
        total += 1
        h = file_hash(f)
        path_str = str(f.resolve())
        if known.get(path_str) == h:
            continue
        print(f"  → {f.name}")
        try:
            n = ingest_file(f)
            print(f"     {n} chunks")
            changed += 1
        except Exception as e:
            print(f"     ERROR: {e}")

    print(f"\nScanned {total} files, re-indexed {changed}")

# ── VERIFY / QUERY ────────────────────────────────────────────────────
def verify():
    cur = get_db().cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT COUNT(*) as n FROM knowledge_embeddings")
    n = cur.fetchone()["n"]
    print(f"Total indexed chunks: {n}")

    cur.execute("SELECT source_type, COUNT(*) as n FROM knowledge_embeddings GROUP BY source_type")
    for row in cur.fetchall():
        print(f"  {row['source_type']}: {row['n']}")

    if n == 0:
        print("\nNo data. Run with --full first.")
        cur.close()
        return

    test_q = "Utopia Deli catering order system"
    print(f"\nTest query: '{test_q}'")
    emb = get_embedding(test_q)
    cur.execute("""
        SELECT source_path, title, content,
               1 - (embedding <=> %s::vector) as similarity
        FROM knowledge_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT 3;
    """, (emb, emb))
    for row in cur.fetchall():
        print(f"\n  [{row['similarity']:.3f}] {row['title'] or 'Untitled'}")
        print(f"  {row['source_path']}")
        snippet = row['content'][:200].replace(chr(10), ' ')
        print(f"  {snippet}...")
    cur.close()

# ── MAIN ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG ingestion for SOL")
    parser.add_argument("--full", action="store_true", help="Full re-index")
    parser.add_argument("--incremental", action="store_true", help="Incremental update")
    parser.add_argument("--verify", action="store_true", help="Check status + test query")
    parser.add_argument("--file", help="Index single file")
    args = parser.parse_args()

    ensure_table()

    if args.full:
        full_ingest()
    elif args.incremental:
        incremental_ingest()
    elif args.file:
        p = Path(args.file)
        if not p.exists():
            print(f"File not found: {p}")
            sys.exit(1)
        n = ingest_file(p)
        print(f"Indexed {n} chunks from {p.name}")
    else:
        verify()
