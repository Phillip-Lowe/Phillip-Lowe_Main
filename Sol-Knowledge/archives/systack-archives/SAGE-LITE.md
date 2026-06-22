# SAGE-Lite — Self-Evolving Graph Memory (Local)

**Version:** 1.0 | **Date:** 2026-05-17 | **Status:** ✅ Architecture complete, ready for use

---

## What This Is

A lightweight, local-first implementation of the core SAGE idea from the paper *"SAGE: A Self-Evolving Agentic Graph-Memory Engine"* (arXiv:2605.12061).

**What it does:**
- Extracts entity-relation-object triples from your text and memory files
- Stores them in a local SQLite graph database
- Lets you query the graph for evidence chains
- Logs failures and proposes graph improvements (evolution loop)

**What it does NOT do:**
- Train GNNs or run RL (that requires GPU compute — see paper)
- Achieve 0.03s retrieval (that requires the full trained model)
- Replace the paper's architecture — it captures the **feedback loop idea** pragmatically

---

## Quick Start

### 1. Initialize the graph database

```bash
cd ~/.openclaw/workspaces/sol
python3 scripts/sage-lite-init.py
```

Creates: `data/sage-graph.db` with tables `nodes`, `edges`, `episodes`, `retrieval_log`, `evolution_queue`

### 2. Write triples to the graph

```bash
# From a text string
python3 scripts/sage-lite-writer.py --text "Alice works at Google." --source "manual"

# From a file
python3 scripts/sage-lite-writer.py --file memory/2026-05-17.md --source "memory"

# From stdin
python3 scripts/sage-lite-writer.py --stdin --source "document" < report.txt

# Force cloud model for complex text
python3 scripts/sage-lite-writer.py --file complex-paper.md --cloud
```

**Model routing:**
- Default: `qwen3.5:9b` or `qwen2.5-coder:7b` (local, fast)
- Fallback: `deepseek-v4-flash:cloud` or `kimi-k2.6:cloud` (cloud, powerful)
- Use `--cloud` to force cloud model

### 3. Query the graph

```bash
python3 scripts/sage-lite-reader.py --query "What is SAGE and how does it relate to graph memory?"
python3 scripts/sage-lite-reader.py --query "Who does Alice work for?"

# Force cloud model for complex reasoning
python3 scripts/sage-lite-reader.py --query "Explain the self-evolution loop in detail" --cloud
```

Returns: `anchor_nodes`, `evidence_path`, `confidence`, `answer`

### 4. Evolve the graph (improve from failures)

```bash
# Process a specific failed retrieval
python3 scripts/sage-lite-evolve.py --log-id 42 --correct "The answer should be X"

# Auto-process last 5 failed retrievals
python3 scripts/sage-lite-evolve.py --auto 5

# Apply queued improvements
python3 scripts/sage-lite-evolve.py --apply
```

### 5. Batch ingest all memory files

```bash
# Ingest all memory/*.md files
python3 scripts/sage-lite-ingest.py

# Only files since a date
python3 scripts/sage-lite-ingest.py --since 2026-05-10

# Dry run (show what would extract, don't write)
python3 scripts/sage-lite-ingest.py --dry-run
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  INPUT: text, memory notes, documents         │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  WRITER (Ollama LLM)                        │
│  Extracts triples: (subject, relation, object)│
│  Local: 7–9B fast  |  Cloud: 70B+ complex   │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  GRAPH STORE (SQLite + networkx)            │
│  nodes: entities, concepts, episodes        │
│  edges: relations with strength 0.0–1.0     │
│  episodes: time-bounded events               │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  READER (Ollama LLM + structured prompt)     │
│  Traverses graph, returns evidence chain    │
│  Dampens noisy hubs, preserves bridges      │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  RETRIEVAL LOG (SQLite)                     │
│  query | retrieved path | answer | success   │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  EVOLUTION (Ollama LLM)                     │
│  Analyzes failures → proposes graph fixes   │
│  Auto-applies safe changes, queues risky    │
└─────────────────────────────────────────────┘
```

---

## Model Routing

| Task | Local Model | Cloud Fallback | When to use cloud |
|---|---|---|---|
| Simple triple extraction | `qwen2.5-coder:7b` | `deepseek-v4-flash:cloud` | Dense technical text |
| Complex reasoning | `qwen3.5:9b` | `deepseek-v4-pro:cloud` | Graph > 50 nodes, ambiguous query |
| Failure analysis | `qwen3.5:9b` | `kimi-k2.6:cloud` | Complex multi-factor failure |
| Batch ingest | `qwen2.5-coder:7b` | `deepseek-v4-flash:cloud` | Large documents |

**Add more models:** Edit `scripts/sage-lite-*.py` — the `call_ollama()` function uses any model Ollama has available.

---

## Schema

See full schema: [`schemas/sage-lite-schema.md`](schemas/sage-lite-schema.md)

Key tables:
- `nodes` — entities, concepts, episodes, documents, aliases
- `edges` — relations with `strength` (0.0–1.0, evolves over time)
- `retrieval_log` — every query + result (drives evolution)
- `evolution_queue` — pending graph improvements

---

## Files

| File | Purpose |
|---|---|
| `schemas/sage-lite-schema.md` | Canonical schema documentation |
| `scripts/sage-lite-init.py` | Create SQLite database |
| `scripts/sage-lite-writer.py` | Extract triples, write to graph |
| `scripts/sage-lite-reader.py` | Query graph, return evidence |
| `scripts/sage-lite-evolve.py` | Process failures, evolve graph |
| `scripts/sage-lite-ingest.py` | Batch import memory/*.md files |
| `data/sage-graph.db` | SQLite database (gitignored) |

---

## Evolution Rules

1. **Failure triggers review** — every failed `retrieval_log` queues an evolution task
2. **Batch processing** — evolution runs manually or on heartbeat, not per-query
3. **Auto-apply safe changes** — `add_edge`, `strengthen_edge`, `add_alias` are auto-applied
4. **Queue risky changes** — `merge_nodes`, `delete_edge` require explicit approval
5. **Strength decay** — unused edges lose 0.01/day; negative feedback drops by 0.2
6. **Strength boost** — successful retrievals increase edge strength by 0.05

---

## Limitations

1. **No trained GNN** — reader uses LLM + structured prompt instead of graph neural network
2. **Slower retrieval** — ~1–5s per query vs. 0.03s in the paper
3. **No true RL** — evolution is prompt-driven, not policy gradient optimization
4. **Local model dependency** — if Ollama local models hang, falls back to cloud (costs tokens)

These are tradeoffs for running on a MacBook Air. The **feedback loop** — write → read → fail → improve — is real and functional.

---

## Next Steps

- [ ] Integrate with OpenClaw heartbeat for automatic memory ingestion
- [ ] Add vector similarity layer (sqlite-vec) for hybrid retrieval
- [ ] Build simple web UI for graph inspection
- [ ] Benchmark: compare graph-based retrieval vs. keyword search on your memory
- [ ] Tune model routing thresholds based on actual performance

---

## Citation

Original paper: **SAGE: A Self-Evolving Agentic Graph-Memory Engine for Structure-Aware Associative Memory**  
Juntong Wang et al., Peking University / Beijing Institute of Technology  
arXiv:2605.12061 [cs.AI] — May 2026

This local implementation captures the architectural insight. For the full 62-page mathematical treatment, read the paper.
