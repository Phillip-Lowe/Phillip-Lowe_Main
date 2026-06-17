#!/usr/bin/env python3
"""
SAGE-Lite Graph Memory — Database Initializer
Creates SQLite schema for local self-evolving graph memory.

Usage: python3 sage-lite-init.py [--path data/sage-graph.db]
"""
import sqlite3
import json
import argparse
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "sage-graph.db"

SCHEMA_SQL = """
-- Nodes: entities, concepts, episodes, documents, aliases
CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_type TEXT NOT NULL CHECK(node_type IN ('entity','concept','episode','document','alias')),
    name TEXT NOT NULL,
    aliases TEXT DEFAULT '[]',
    description TEXT,
    source TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    embedding TEXT DEFAULT '[]',
    weight REAL DEFAULT 1.0
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_nodes_unique ON nodes(name, node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_weight ON nodes(weight);

-- Edges: relations between nodes
CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relation TEXT NOT NULL,
    strength REAL DEFAULT 1.0 CHECK(strength >= 0.0 AND strength <= 1.0),
    evidence TEXT,
    source TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (source_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES nodes(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_edges_unique ON edges(source_id, target_id, relation);
CREATE INDEX IF NOT EXISTS idx_edges_strength ON edges(strength);

-- Episodes: time-bounded events linked to nodes
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER,
    description TEXT,
    timestamp TEXT,
    participants TEXT DEFAULT '[]',
    source TEXT,
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- Retrieval log: every query + result for evolution feedback
CREATE TABLE IF NOT EXISTS retrieval_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    retrieved_nodes TEXT DEFAULT '[]',
    retrieved_edges TEXT DEFAULT '[]',
    answer TEXT,
    success INTEGER DEFAULT -1,  -- -1=unknown, 0=fail, 1=success
    failure_reason TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);

-- Evolution queue: pending graph improvements
CREATE TABLE IF NOT EXISTS evolution_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id INTEGER,
    action TEXT NOT NULL CHECK(action IN ('add_edge','merge_nodes','strengthen_edge','add_alias','add_node','delete_edge')),
    params TEXT NOT NULL DEFAULT '{}',
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','applied','rejected')),
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (log_id) REFERENCES retrieval_log(id) ON DELETE SET NULL
);

-- Metadata table for schema versioning
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', '1.0');
INSERT OR REPLACE INTO meta (key, value) VALUES ('created_at', datetime('now'));
"""

def init_db(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"✅ SAGE-Lite graph DB initialized: {db_path}")
    print(f"   Tables: nodes, edges, episodes, retrieval_log, evolution_queue")
    print(f"   Schema version: 1.0")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize SAGE-Lite graph database")
    parser.add_argument("--path", type=Path, default=DEFAULT_DB, help="Path to SQLite DB")
    args = parser.parse_args()
    init_db(args.path)
