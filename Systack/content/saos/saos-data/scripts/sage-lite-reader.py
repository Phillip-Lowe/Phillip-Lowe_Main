#!/usr/bin/env python3
"""
SAGE-Lite Graph Memory — Reader Engine
Queries the graph via structured prompts to Ollama, returns evidence chains.

Usage:
  python3 sage-lite-reader.py --query "What did Alice say about the project?"
  python3 sage-lite-reader.py --query "How does SAGE relate to graph memory?"
"""
import sqlite3
import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import urllib.request

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "sage-graph.db"

READER_PROMPT = """You are a graph memory reader. I will give you a graph structure and a query.
Your task is to traverse the graph to find the most relevant evidence chain.

GRAPH NODES:
{nodes}

GRAPH EDGES:
{edges}

QUERY: {query}

INSTRUCTIONS:
1. Identify anchor nodes that match concepts in the query
2. Follow edges by relevance (higher strength = more relevant)
3. Prefer multi-hop paths that connect disparate cues in the query
4. Dampen noisy hubs: if a node has >10 edges, only use it if directly relevant
5. Preserve sparse bridges: edges with few connections may be critical paths
6. Return the shortest relevant path with highest total strength

OUTPUT JSON ONLY:
{{
  "anchor_nodes": ["name1", "name2"],
  "evidence_path": [
    {{"from": "...", "relation": "...", "to": "...", "strength": 0.8}}
  ],
  "confidence": 0.0-1.0,
  "answer": "synthesized answer based on evidence"
}}
"""

def call_ollama(prompt: str, model: str = "qwen3.5:9b", temperature: float = 0.1, timeout: int = 300) -> str:
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

def get_subgraph(conn: sqlite3.Connection, query: str, max_nodes: int = 50,
                 max_hops: int = 3) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract a relevant subgraph using hybrid strategy:
    1. Vector/keyword match for anchor candidates
    2. BFS expansion from anchors up to max_hops
    3. Prioritize by edge strength + node weight
    """
    c = conn.cursor()

    # Simple keyword-based anchor selection
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    query_words.discard('the'); query_words.discard('a'); query_words.discard('is'); query_words.discard('what'); query_words.discard('how'); query_words.discard('does')

    # Find matching nodes
    placeholders = ','.join('?' * len(query_words))
    c.execute(f"""
        SELECT id, node_type, name, aliases, description, weight
        FROM nodes
        WHERE name IN ({placeholders})
           OR json_array_length(aliases) > 0
    """, list(query_words))

    all_nodes = c.fetchall()

    # Filter by keyword match in name or aliases
    anchor_ids = set()
    matched_nodes = []
    for row in all_nodes:
        nid, ntype, name, aliases, desc, weight = row
        node_words = set(name.lower().split())
        alias_words = set()
        try:
            alias_list = json.loads(aliases or "[]")
            for a in alias_list:
                alias_words.update(a.lower().split())
        except:
            pass

        if query_words & node_words or query_words & alias_words:
            anchor_ids.add(nid)
            matched_nodes.append({
                "id": nid, "type": ntype, "name": name,
                "aliases": alias_list if 'alias_list' in dir() else [],
                "description": desc or "", "weight": weight
            })

    if not anchor_ids:
        # Fallback: just grab highest-weight nodes
        c.execute("SELECT id, node_type, name, aliases, description, weight FROM nodes ORDER BY weight DESC LIMIT ?", (max_nodes,))
        for row in c.fetchall():
            nid, ntype, name, aliases, desc, weight = row
            anchor_ids.add(nid)
            try:
                alias_list = json.loads(aliases or "[]")
            except:
                alias_list = []
            matched_nodes.append({"id": nid, "type": ntype, "name": name, "aliases": alias_list, "description": desc or "", "weight": weight})

    # BFS expansion from anchors
    visited = set(anchor_ids)
    frontier = list(anchor_ids)
    edges_result = []
    nodes_in_subgraph = {n["id"]: n for n in matched_nodes}

    for hop in range(max_hops):
        if not frontier or len(nodes_in_subgraph) >= max_nodes:
            break
        next_frontier = []
        for node_id in frontier:
            c.execute("""
                SELECT e.id, e.source_id, e.target_id, e.relation, e.strength,
                       n1.name as src_name, n2.name as tgt_name
                FROM edges e
                JOIN nodes n1 ON e.source_id = n1.id
                JOIN nodes n2 ON e.target_id = n2.id
                WHERE e.source_id = ? OR e.target_id = ?
                ORDER BY e.strength DESC
                LIMIT 15
            """, (node_id, node_id))

            for erow in c.fetchall():
                eid, sid, tid, rel, strength, sname, tname = erow
                edges_result.append({
                    "id": eid, "source_id": sid, "target_id": tid,
                    "relation": rel, "strength": strength,
                    "source_name": sname, "target_name": tname
                })

                other_id = tid if sid == node_id else sid
                if other_id not in visited and len(nodes_in_subgraph) < max_nodes:
                    visited.add(other_id)
                    next_frontier.append(other_id)
                    c.execute("SELECT id, node_type, name, aliases, description, weight FROM nodes WHERE id = ?", (other_id,))
                    nrow = c.fetchone()
                    if nrow:
                        nid, ntype, name, aliases, desc, weight = nrow
                        try:
                            alias_list = json.loads(aliases or "[]")
                        except:
                            alias_list = []
                        nodes_in_subgraph[nid] = {"id": nid, "type": ntype, "name": name, "aliases": alias_list, "description": desc or "", "weight": weight}

        frontier = next_frontier

    return list(nodes_in_subgraph.values()), edges_result

def read_memory(conn: sqlite3.Connection, query: str, model: str = "qwen3.5:9b",
                use_cloud: bool = False, max_nodes: int = 50) -> Dict:
    """Query the graph and return structured answer."""

    print(f"🔍 SAGE-Lite Reader")
    print(f"   Query: {query}")
    print(f"   Model: {model} {'(cloud)' if use_cloud else '(local)'}")

    # Get subgraph
    nodes, edges = get_subgraph(conn, query, max_nodes=max_nodes)
    print(f"   Subgraph: {len(nodes)} nodes, {len(edges)} edges")

    if not nodes:
        return {"error": "No relevant nodes found in graph", "confidence": 0.0, "answer": "I don't have relevant information about that."}

    # Format for prompt
    nodes_str = "\n".join([
        f"- {n['name']} (type={n['type']}, weight={n['weight']:.2f}, desc={n['description'][:80] if n['description'] else 'none'})"
        for n in nodes[:max_nodes]
    ])
    edges_str = "\n".join([
        f"- {e['source_name']} --[{e['relation']}, strength={e['strength']:.2f}]--> {e['target_name']}"
        for e in edges[:80]  # cap edges
    ])

    prompt = READER_PROMPT.format(nodes=nodes_str, edges=edges_str, query=query)

    try:
        raw = call_ollama(prompt, model=model)
    except Exception as e:
        if not use_cloud:
            print(f"   ⚠️ Local model failed ({e}), trying cloud fallback...")
            return read_memory(conn, query, model="deepseek-v4-pro:cloud", use_cloud=True, max_nodes=max_nodes)
        raise

    # Parse JSON
    raw = re.sub(r'^```json\s*', '', raw.strip())
    raw = re.sub(r'```\s*$', '', raw.strip())
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        print(f"   ⚠️ Failed to parse reader JSON. Raw:\n{raw[:500]}")
        result = {"error": "Parse failed", "raw": raw[:500], "confidence": 0.0, "answer": ""}

    # Log retrieval
    retrieved_node_ids = [n["id"] for n in nodes]
    retrieved_edge_ids = [e["id"] for e in edges]
    c = conn.cursor()
    c.execute("""
        INSERT INTO retrieval_log (query, retrieved_nodes, retrieved_edges, answer, success)
        VALUES (?, ?, ?, ?, ?)
    """, (query, json.dumps(retrieved_node_ids), json.dumps(retrieved_edge_ids),
          result.get("answer", ""), -1))
    log_id = c.lastrowid
    conn.commit()

    result["_log_id"] = log_id
    result["_nodes_count"] = len(nodes)
    result["_edges_count"] = len(edges)
    return result

def main():
    parser = argparse.ArgumentParser(description="SAGE-Lite Reader: query graph memory")
    parser.add_argument("--query", required=True, help="Question to ask")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--model", default="qwen3.5:9b")
    parser.add_argument("--cloud", action="store_true")
    parser.add_argument("--max-nodes", type=int, default=50)
    args = parser.parse_args()

    conn = sqlite3.connect(str(args.db))
    conn.execute("PRAGMA foreign_keys = ON")

    result = read_memory(conn, args.query, model=args.model, use_cloud=args.cloud,
                         max_nodes=args.max_nodes)

    conn.close()

    print(f"\n📊 Result:")
    print(f"   Confidence: {result.get('confidence', 'N/A')}")
    print(f"   Anchors: {', '.join(result.get('anchor_nodes', []))}")
    print(f"   Path length: {len(result.get('evidence_path', []))}")
    print(f"   Answer: {result.get('answer', 'N/A')}")
    print(f"   (Log ID: {result.get('_log_id')})")

if __name__ == "__main__":
    main()
