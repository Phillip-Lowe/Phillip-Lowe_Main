#!/usr/bin/env python3
"""
RAG Retrieval Layer for SOL
- Takes a query → returns top-k relevant chunks
- Can be called from OpenClaw skill or standalone

Usage:
    python3 rag_retrieve.py "Utopia Deli order system"
    python3 rag_retrieve.py "n8n workflow credentials" --k 5
    python3 rag_retrieve.py "catering deployment" --format json
"""

import os, sys, argparse, json
from typing import List, Dict

import psycopg2
from psycopg2.extras import RealDictCursor

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIM = 768

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")
DB_PASS = os.environ.get("PGPASSWORD", "")


def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=os.environ.get('PGPASSWORD', '')
    )

def get_embedding(text: str) -> List[float]:
    import urllib.request
    payload = json.dumps({"model": EMBEDDING_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/embeddings",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
        return data.get("embedding", [])

def retrieve(query: str, k: int = 5, min_similarity: float = 0.3) -> List[Dict]:
    """
    Retrieve top-k most relevant chunks for a query.
    Returns list of dicts with: source_path, title, content, similarity
    """
    embedding = get_embedding(query)
    if not embedding or len(embedding) != EMBEDDING_DIM:
        raise RuntimeError(f"Failed to generate embedding for query: {query}")

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT source_path, source_type, title, content,
               1 - (embedding <=> %s::vector) as similarity
        FROM knowledge_embeddings
        WHERE 1 - (embedding <=> %s::vector) >= %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (embedding, embedding, min_similarity, embedding, k))

    results = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results

def format_context(results: List[Dict], max_chars: int = 4000) -> str:
    """Format results into a context block for LLM prompt injection."""
    lines = ["## Retrieved Knowledge Context", ""]
    total = 0
    for i, r in enumerate(results, 1):
        snippet = r["content"].strip()
        source = r["source_path"].split("/")[-1]
        title = r.get("title") or "Untitled"
        sim = r.get("similarity", 0)

        block = f"### [{i}] {title} (relevance: {sim:.2f})\n**Source:** {source}\n\n{snippet}\n\n"
        if total + len(block) > max_chars:
            break
        lines.append(block)
        total += len(block)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="RAG retrieval for SOL")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--k", type=int, default=5, help="Number of results")
    parser.add_argument("--min-sim", type=float, default=0.3, help="Minimum similarity threshold")
    parser.add_argument("--format", choices=["text", "json", "context"], default="context",
                        help="Output format")
    args = parser.parse_args()

    try:
        results = retrieve(args.query, k=args.k, min_similarity=args.min_sim)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(results, indent=2, default=str))
    elif args.format == "text":
        for i, r in enumerate(results, 1):
            print(f"\n--- Result {i} [{r['similarity']:.3f}] ---")
            print(f"Title: {r.get('title') or 'Untitled'}")
            print(f"Source: {r['source_path']}")
            print(f"Content: {r['content'][:500]}...")
    else:  # context
        print(format_context(results))

if __name__ == "__main__":
    main()
