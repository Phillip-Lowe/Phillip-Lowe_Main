#!/usr/bin/env python3
"""
SAOS Customer Dashboard API
Serves client-scoped fleet data for the customer-facing portal.

Usage:
    python3 customer-api.py --port 8766
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)
CORS(app)

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER
    )

def get_client_id():
    """In production, extract client ID from auth token/header.
    For now, accepts ?client_id= query param or X-Client-ID header.
    Returns integer client ID or None."""
    raw = request.args.get('client_id') or request.headers.get('X-Client-ID')
    if raw and raw.isdigit():
        return int(raw)
    return None

@app.route('/api/portal/status')
def client_status():
    """Client-scoped fleet status."""
    client_id = get_client_id()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    client = None
    if client_id is not None:
        cur.execute("SELECT * FROM saos_clients WHERE id = %s", (client_id,))
        client = cur.fetchone()

    # Task counts
    cur.execute("SELECT status, COUNT(*) as n FROM task_queue GROUP BY status")
    tasks = {r['status']: r['n'] for r in cur.fetchall()}

    # Agent states
    cur.execute("SELECT * FROM agent_state ORDER BY agent_name")
    agents = [dict(r) for r in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "client": dict(client) if client else None,
        "tasks": tasks,
        "agents": agents,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/portal/tasks')
def client_tasks():
    """Client-scoped task history."""
    client_id = get_client_id()
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT t.id, t.task_type, t.assigned_agent, t.status, t.priority,
               t.created_at, t.completed_at
        FROM task_queue t
        ORDER BY t.created_at DESC
        LIMIT 50
    """)
    tasks = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(tasks)

@app.route('/api/portal/agents')
def client_agents():
    """Agent fleet status for this client."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM agent_state ORDER BY agent_name")
    agents = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(agents)

@app.route('/api/portal/client')
def client_info():
    """Get this client's account details."""
    client_id = get_client_id()
    if client_id is None:
        return jsonify({"error": "client_id required (integer)"}), 400

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM saos_clients WHERE id = %s", (client_id,))
    client = cur.fetchone()
    cur.close()
    conn.close()

    if not client:
        return jsonify({"error": "Client not found"}), 404

    return jsonify(dict(client))

@app.route('/api/portal/health')
def health():
    return jsonify({"status": "ok", "service": "saos-customer-portal-api"})

# ── Static file serving ──
# Serve dashboard HTML at root + all static files (PDFs, etc.)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_dashboard(path):
    # If path is empty or points to a directory, serve index.html
    if not path:
        return send_from_directory(BASE_DIR, 'index.html')
    full_path = os.path.join(BASE_DIR, path)
    if os.path.isfile(full_path):
        return send_from_directory(BASE_DIR, path)
    # Fall back to index.html for SPA routing
    return send_from_directory(BASE_DIR, 'index.html')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()

    print(f"🛰️  SAOS Customer Portal API starting on port {args.port}")
    print(f"   Endpoints:")
    print(f"   - GET /                  (dashboard HTML)")
    print(f"   - GET /api/portal/status (client fleet overview)")
    print(f"   - GET /api/portal/tasks (client task history)")
    print(f"   - GET /api/portal/agents (agent fleet status)")
    print(f"   - GET /api/portal/client (account details)")
    print(f"   - GET /api/portal/health (health check)")
    print(f"")
    print(f"   Auth: ?client_id= query param or X-Client-ID header")

    app.run(host='0.0.0.0', port=args.port, debug=False)
