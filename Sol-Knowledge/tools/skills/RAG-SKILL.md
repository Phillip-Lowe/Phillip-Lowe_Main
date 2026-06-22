# RAG Skill — Semantic Knowledge Retrieval for SOL

**Purpose:** Automatically retrieve relevant context from your knowledge base before answering queries.

## Architecture

```
User Query
    ↓
OpenClaw Agent
    ↓
[rag_retrieve.py] → pgvector similarity search
    ↓
Top-k chunks injected into LLM prompt
    ↓
Answer with YOUR knowledge
```

## Components

| File | Purpose |
|------|---------|
| `rag_ingest_v2.py` | Index markdown files into pgvector |
| `rag_retrieve.py` | Query and retrieve relevant chunks |
| `knowledge_embeddings` | Postgres table with 768-dim vectors |

## Commands

```bash
# Full re-index (run after major vault changes)
python3 rag_ingest_v2.py --full

# Incremental update (fast, only changed files)
python3 rag_ingest_v2.py --incremental

# Test retrieval
python3 rag_retrieve.py "your query" --k 5

# Get formatted context for LLM
python3 rag_retrieve.py "your query" --format context
```

## OpenClaw Integration

### Option A: Inline (per-query)
Before answering, run:
```bash
python3 rag_retrieve.py "$USER_QUERY" --format context --k 5
```
Append output to the LLM prompt.

### Option B: Skill Hook (recommended)
Add to your agent system prompt:
```
When the user asks about past work, systems, or specific knowledge:
1. Call: python3 rag_retrieve.py "query" --format context --k 5
2. Include the "Retrieved Knowledge Context" in your reasoning
3. Answer using both retrieved context and your reasoning
```

## Current Status

| Metric | Value |
|--------|-------|
| Indexed chunks | ~10,000 |
| Sources | 439 files |
| Embeddings model | nomic-embed-text (768-dim) |
| Database | Postgres + pgvector |
| Similarity metric | cosine |

## Files Indexed

- Workspace markdown files (`~/.openclaw/workspaces/sol/`)
- Daily logs (`memory/YYYY-MM-DD.md`)
- Project documentation (`*.md` files)

**Note:** iCloud vault files are locked during sync. Retry indexing after iCloud download completes.

## Performance

- Embedding generation: ~1-2 sec per chunk (local Ollama)
- Query retrieval: ~50-200 ms (pgvector index)
- Full re-index: ~10-15 min for 10K chunks

## Maintenance

**Auto-sync:** Set up a cron job for incremental re-indexing:
```bash
# Run hourly
0 * * * * cd ~/.openclaw/workspaces/sol && python3 rag_ingest_v2.py --incremental > /tmp/rag_sync.log 2>&1
```

**When to re-index:**
- After major wiki updates
- After daily log writes
- When retrieval quality degrades

## Troubleshooting

| Issue | Fix |
|-------|-----|
| iCloud files locked | Open files in Finder to force download, then re-index |
| Low similarity scores | Lower `--min-sim` threshold or re-index |
| Ollama not responding | Check `ollama list` and ensure model is loaded |
| pgvector not found | Run `CREATE EXTENSION vector;` as superuser |

---
**Built:** 2026-06-09
**Status:** Production-ready
