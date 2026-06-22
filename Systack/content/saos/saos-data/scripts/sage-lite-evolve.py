#!/usr/bin/env python3
"""
SAGE-Lite Graph Memory — Evolution Engine
Processes retrieval failures and proposes graph improvements.

Usage:
  python3 sage-lite-evolve.py --log-id 42 --correct "The answer should have been X"
  python3 sage-lite-evolve.py --auto 5  # Auto-process last 5 failed retrievals
"""
import sqlite3
import json
import argparse
from pathlib import Path
from typing import List, Dict
import urllib.request

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "sage-graph.db"

EVOLUTION_PROMPT = """You are a graph memory evolution engine. A query failed to retrieve the correct answer. Analyze why and propose specific graph modifications.

QUERY: {query}
RETRIEVED ANSWER: {answer}
CORRECT ANSWER: {correct_answer}
FAILURE REASON: {failure_reason}

CURRENT GRAPH AROUND FAILURE:
Nodes: {nodes}
Edges: {edges}

INSTRUCTIONS:
Propose 1-3 specific graph modifications to fix this failure:
- add_edge: create a new connection between existing nodes
- strengthen_edge: boost an existing edge that was too weak
- merge_nodes: two nodes represent the same concept
- add_alias: add an alternative name to a node
- add_node: create a new node (rare, only if key concept missing)

Each proposal must include exact node names that exist in the graph.

OUTPUT JSON ONLY:
[
  {{
    "action": "add_edge",
    "source": "exact node name",
    "target": "exact node name",
    "relation": "...",
    "strength": 0.9,
    "rationale": "why this fixes the failure"
  }}
]
"""

def call_ollama(prompt: str, model: str = "qwen3.5:9b", temperature: float = 0.2, timeout: int = 300) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": 2048}
    }
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
        return data.get("response", "")

def get_failure_subgraph(conn: sqlite3.Connection, log_id: int, max_nodes: int = 30) -> Tuple[List, List]:
    """Extract subgraph around a failed retrieval."""
    c = conn.cursor()
    c.execute("SELECT query, retrieved_nodes, retrieved_edges, answer, failure_reason FROM retrieval_log WHERE id = ?", (log_id,))
    row = c.fetchone()
    if not row:
        return None

    query, node_ids_json, edge_ids_json, answer, reason = row
    node_ids = json.loads(node_ids_json or "[]")
    edge_ids = json.loads(edge_ids_json or "[]")

    # Get nodes
    nodes = []
    if node_ids:
        placeholders = ','.join('?' * len(node_ids))
        c.execute(f"SELECT id, name, node_type, description, weight FROM nodes WHERE id IN ({placeholders})", node_ids)
        for r in c.fetchall():
            nodes.append({"id": r[0], "name": r[1], "type": r[2], "description": r[3] or "", "weight": r[4]})

    # Get edges
    edges = []
    if edge_ids:
        placeholders = ','.join('?' * len(edge_ids))
        c.execute(f"""
            SELECT e.id, n1.name, n2.name, e.relation, e.strength
            FROM edges e
            JOIN nodes n1 ON e.source_id = n1.id
            JOIN nodes n2 ON e.target_id = n2.id
            WHERE e.id IN ({placeholders})
        """, edge_ids)
        for r in c.fetchall():
            edges.append({"id": r[0], "source": r[1], "target": r[2], "relation": r[3], "strength": r[4]})

    # Also expand to neighbors
    if nodes:
        node_id_set = {n["id"] for n in nodes}
        c.execute(f"""
            SELECT e.id, n1.name, n2.name, e.relation, e.strength
            FROM edges e
            JOIN nodes n1 ON e.source_id = n1.id
            JOIN nodes n2 ON e.target_id = n2.id
            WHERE e.source_id IN ({placeholders}) OR e.target_id IN ({placeholders})
            ORDER BY e.strength DESC
            LIMIT 30
        """, list(node_id_set) + list(node_id_set))
        for r in c.fetchall():
            if r[0] not in {e["id"] for e in edges}:
                edges.append({"id": r[0], "source": r[1], "target": r[2], "relation": r[3], "strength": r[4]})

    return {"query": query, "answer": answer, "reason": reason}, nodes, edges

def process_evolution(conn: sqlite3.Connection, log_id: int, correct_answer: str,
                      model: str = "qwen3.5:9b", use_cloud: bool = False) -> List[Dict]:
    """Analyze a failure and queue improvements."""

    result = get_failure_subgraph(conn, log_id)
    if not result:
        print(f"❌ Log {log_id} not found")
        return []

    log_info, nodes, edges = result

    print(f"🧬 SAGE-Lite Evolution — Log {log_id}")
    print(f"   Query: {log_info['query'][:80]}...")
    print(f"   Failure: {log_info['reason'] or 'unknown'}")
    print(f"   Subgraph: {len(nodes)} nodes, {len(edges)} edges")

    if not nodes:
        print("   ⚠️ Empty subgraph, cannot evolve")
        return []

    nodes_str = "\n".join([f"- {n['name']} (type={n['type']}, weight={n['weight']:.2f})" for n in nodes])
    edges_str = "\n".join([f"- {e['source']} --[{e['relation']}, {e['strength']:.2f}]--> {e['target']}" for e in edges])

    prompt = EVOLUTION_PROMPT.format(
        query=log_info["query"],
        answer=log_info["answer"],
        correct_answer=correct_answer,
        failure_reason=log_info["reason"] or "retrieval failed to find correct evidence",
        nodes=nodes_str,
        edges=edges_str
    )

    try:
        raw = call_ollama(prompt, model=model)
    except Exception as e:
        if not use_cloud:
            print(f"   ⚠️ Local model failed ({e}), trying cloud...")
            return process_evolution(conn, log_id, correct_answer, model="deepseek-v4-pro:cloud", use_cloud=True)
        raise

    # Parse JSON
    import re
    raw = re.sub(r'^```json\s*', '', raw.strip())
    raw = re.sub(r'```\s*$', '', raw.strip())
    raw = raw.strip()

    try:
        proposals = json.loads(raw)
        if not isinstance(proposals, list):
            proposals = []
    except:
        print(f"   ⚠️ Failed to parse evolution JSON")
        proposals = []

    # Queue proposals
    c = conn.cursor()
    queued = 0
    for p in proposals:
        c.execute("""
            INSERT INTO evolution_queue (log_id, action, params, status)
            VALUES (?, ?, ?, 'pending')
        """, (log_id, p.get("action", "unknown"), json.dumps(p)))
        queued += 1

    # Update log with failure reason if not set
    if not log_info["reason"]:
        c.execute("UPDATE retrieval_log SET failure_reason = ? WHERE id = ?", ("evolution_processed", log_id))

    conn.commit()
    print(f"   Queued {queued} improvement proposals")
    return proposals

def apply_queued(conn: sqlite3.Connection, auto_apply: bool = False):
    """Apply pending evolution proposals. Auto-apply safe ones."""
    c = conn.cursor()
    c.execute("SELECT id, action, params FROM evolution_queue WHERE status = 'pending'")
    pending = c.fetchall()

    if not pending:
        print("   No pending evolutions")
        return

    print(f"   Applying {len(pending)} queued improvements...")

    for qid, action, params_json in pending:
        params = json.loads(params_json)

        if action == "add_edge":
            # Find or create nodes
            src_name = params.get("source")
            tgt_name = params.get("target")
            relation = params.get("relation")
            strength = params.get("strength", 0.8)

            c.execute("SELECT id FROM nodes WHERE name = ?", (src_name,))
            src_row = c.fetchone()
            c.execute("SELECT id FROM nodes WHERE name = ?", (tgt_name,))
            tgt_row = c.fetchone()

            if src_row and tgt_row:
                c.execute("""
                    INSERT OR REPLACE INTO edges (source_id, target_id, relation, strength)
                    VALUES (?, ?, ?, ?)
                """, (src_row[0], tgt_row[0], relation, strength))
                c.execute("UPDATE evolution_queue SET status = 'applied' WHERE id = ?", (qid,))
                print(f"   ✅ Added edge: {src_name} --[{relation}]--> {tgt_name} (strength={strength:.2f})")
            else:
                c.execute("UPDATE evolution_queue SET status = 'rejected' WHERE id = ?", (qid,))
                print(f"   ❌ Rejected: nodes not found ({src_name}, {tgt_name})")

        elif action == "strengthen_edge":
            src_name = params.get("source")
            tgt_name = params.get("target")
            relation = params.get("relation")
            boost = params.get("strength", 0.2)

            c.execute("""
                SELECT e.id, e.strength FROM edges e
                JOIN nodes n1 ON e.source_id = n1.id
                JOIN nodes n2 ON e.target_id = n2.id
                WHERE n1.name = ? AND n2.name = ? AND e.relation = ?
            """, (src_name, tgt_name, relation))
            row = c.fetchone()
            if row:
                new_strength = min(1.0, row[1] + boost)
                c.execute("UPDATE edges SET strength = ? WHERE id = ?", (new_strength, row[0]))
                c.execute("UPDATE evolution_queue SET status = 'applied' WHERE id = ?", (qid,))
                print(f"   ✅ Strengthened: {src_name}--[{relation}]-->{tgt_name} to {new_strength:.2f}")
            else:
                c.execute("UPDATE evolution_queue SET status = 'rejected' WHERE id = ?", (qid,))

        elif action == "add_alias":
            node_name = params.get("node")
            alias = params.get("alias")
            c.execute("SELECT id, aliases FROM nodes WHERE name = ?", (node_name,))
            row = c.fetchone()
            if row:
                aliases = json.loads(row[1] or "[]")
                if alias not in aliases:
                    aliases.append(alias)
                    c.execute("UPDATE nodes SET aliases = ? WHERE id = ?", (json.dumps(aliases), row[0]))
                    c.execute("UPDATE evolution_queue SET status = 'applied' WHERE id = ?", (qid,))
                    print(f"   ✅ Added alias: {node_name} -> {alias}")
                else:
                    c.execute("UPDATE evolution_queue SET status = 'applied' WHERE id = ?", (qid,))
            else:
                c.execute("UPDATE evolution_queue SET status = 'rejected' WHERE id = ?", (qid,))

        else:
            # merge_nodes, add_node, delete_edge — require explicit approval
            if auto_apply:
                c.execute("UPDATE evolution_queue SET status = 'rejected' WHERE id = ?", (qid,))
                print(f"   ⏭️ Skipped {action}: requires manual approval")
            else:
                print(f"   ⏸️ Pending approval: {action} — {params}")

    conn.commit()

def main():
    parser = argparse.ArgumentParser(description="SAGE-Lite Evolution: improve graph from failures")
    parser.add_argument("--log-id", type=int, help="Process specific retrieval log")
    parser.add_argument("--correct", default="", help="Correct answer for the failed query")
    parser.add_argument("--auto", type=int, help="Auto-process last N failed retrievals")
    parser.add_argument("--apply", action="store_true", help="Apply queued evolutions")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--cloud", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(str(args.db))
    conn.execute("PRAGMA foreign_keys = ON")

    if args.apply:
        apply_queued(conn)
    elif args.log_id:
        process_evolution(conn, args.log_id, args.correct, model=args.model, use_cloud=args.cloud)
    elif args.auto:
        c = conn.cursor()
        c.execute("""
            SELECT id FROM retrieval_log
            WHERE success = 0 OR success = -1
            ORDER BY timestamp DESC
            LIMIT ?
        """, (args.auto,))
        logs = c.fetchall()
        for (log_id,) in logs:
            process_evolution(conn, log_id, "", model=args.model, use_cloud=args.cloud)
    else:
        print("Provide --log-id, --auto N, or --apply")

    conn.close()

if __name__ == "__main__":
    main()
