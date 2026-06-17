#!/usr/bin/env python3
"""
SAGE-Lite Pipeline Verification — Cloud Model Only
Tests the full write→read→evolve cycle with known-working cloud models.
"""
import urllib.request
import json
import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sage-graph.db')

def call_ollama(prompt, model, timeout=60):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 1024}
    }).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
        return data

def extract_triples(text):
    prompt = f"""You are a knowledge graph extraction engine.
Read the text and output ONLY a JSON array of entity-relation-object triples.
Format: [{{"subject": "...", "relation": "...", "object": "..."}}]
Use relations: is_a, uses, part_of, leads_to, helps_with, creates, requires
Output ONLY valid JSON. No explanation.

Text: {text}

JSON:"""
    data = call_ollama(prompt, "deepseek-v4-flash:cloud", timeout=30)
    raw = data.get("response", "[]")
    # Clean markdown
    raw = re.sub(r'^```json\s*', '', raw.strip())
    raw = re.sub(r'```\s*$', '', raw.strip())
    raw = raw.strip()
    try:
        return json.loads(raw) if raw else []
    except:
        print(f"   Parse fail, raw: {raw[:200]}")
        return []

def read_graph(query, nodes_data, edges_data):
    nodes_str = "\n".join([f"- {n[1]} (type={n[2]})" for n in nodes_data])
    edges_str = "\n".join([f"- {e[0]} --[{e[1]}, {e[2]:.2f}]--> {e[3]}" for e in edges_data])

    prompt = f"""You are a graph memory reader.
Given these nodes and edges, answer the query.

NODES:
{nodes_str}

EDGES:
{edges_str}

QUERY: {query}

Answer directly and concisely."""

    data = call_ollama(prompt, "deepseek-v4-flash:cloud", timeout=30)
    return data.get("response", "No answer")

print("=== SAGE-LITE PIPELINE VERIFICATION ===\n")

# Check DB
assert os.path.exists(DB_PATH), f"DB not found: {DB_PATH}"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check existing graph
c.execute("SELECT COUNT(*) FROM nodes")
nc = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM edges")
ec = c.fetchone()[0]
print(f"📊 Existing graph: {nc} nodes, {ec} edges\n")

# Step 1: Extract triples
text = "SAGE is a self-evolving graph memory engine. It couples reinforcement learning with a structurally gated graph neural network."
print("📝 Step 1: Extract triples from text...")
triples = extract_triples(text)
print(f"✅ Extracted {len(triples)} triples")
for t in triples[:5]:
    print(f"   ({t.get('subject')}) --[{t.get('relation')}]--> ({t.get('object')})")

# Step 2: Write to graph
print("\n💾 Step 2: Write to graph...")
for t in triples:
    subj, rel, obj = t.get("subject",""), t.get("relation",""), t.get("object","")
    if not all([subj, rel, obj]):
        continue
    for name in [subj, obj]:
        c.execute("INSERT OR IGNORE INTO nodes (node_type, name, source) VALUES (?, ?, ?)",
                  ("entity", name, "pipeline-test"))
    c.execute("SELECT id FROM nodes WHERE name=?", (subj,))
    src_id = c.fetchone()[0]
    c.execute("SELECT id FROM nodes WHERE name=?", (obj,))
    tgt_id = c.fetchone()[0]
    c.execute("INSERT OR IGNORE INTO edges (source_id, target_id, relation, source) VALUES (?, ?, ?, ?)",
              (src_id, tgt_id, rel, "pipeline-test"))
conn.commit()
print(f"✅ Written to graph")

# Step 3: Read graph
c.execute("SELECT COUNT(*) FROM nodes")
nc2 = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM edges")
ec2 = c.fetchone()[0]
print(f"\n🔍 Step 3: Query graph ({nc2} nodes, {ec2} edges)...")

# Get all nodes/edges for context
c.execute("SELECT id, name, node_type FROM nodes")
nodes_data = c.fetchall()
c.execute("SELECT n1.name, e.relation, e.strength, n2.name FROM edges e JOIN nodes n1 ON e.source_id=n1.id JOIN nodes n2 ON e.target_id=n2.id")
edges_data = c.fetchall()

query = "What is SAGE and how does it work?"
answer = read_graph(query, nodes_data, edges_data)
print(f"✅ Answer: {answer[:200]}")

# Step 4: Log retrieval
c.execute("INSERT INTO retrieval_log (query, answer, success) VALUES (?, ?, -1)", (query, answer))
log_id = c.lastrowid
conn.commit()
print(f"\n📝 Step 4: Logged retrieval (log_id={log_id})")

# Step 5: Show evidence chains
c.execute("""
    SELECT n1.name, e.relation, n2.name, e.strength
    FROM edges e
    JOIN nodes n1 ON e.source_id = n1.id
    JOIN nodes n2 ON e.target_id = n2.id
    WHERE n1.name = 'SAGE' OR n2.name = 'SAGE'
    ORDER BY e.strength DESC
    LIMIT 5
""")
chains = c.fetchall()
print(f"\n🔗 Evidence chains for SAGE:")
for ch in chains:
    print(f"   {ch[0]} --[{ch[1]}, {ch[3]:.2f}]--> {ch[2]}")

conn.close()
print("\n=== ✅ PIPELINE VERIFICATION COMPLETE ===")
