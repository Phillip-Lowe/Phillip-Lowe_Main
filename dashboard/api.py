#!/usr/bin/env python3
"""
SAOS Fleet Dashboard API
Simple Flask API serving fleet status data.

Usage:
    python3 api.py          # Start server on port 5000
    python3 api.py --port 8080  # Custom port
"""

from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
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

@app.route('/api/status')
def fleet_status():
    """Get full fleet status."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Task counts
    cur.execute("SELECT status, COUNT(*) as n FROM task_queue GROUP BY STATUS")
    tasks = {r['status']: r['n'] for r in cur.fetchall()}
    
    # Agent states
    cur.execute("SELECT * FROM agent_state ORDER BY agent_name")
    agents = [dict(r) for r in cur.fetchall()]
    
    # Recent clients
    cur.execute("SELECT id, customer_name, vps_status, created_at FROM saos_clients ORDER BY created_at DESC LIMIT 10")
    clients = [dict(r) for r in cur.fetchall()]
    
    # Messages
    cur.execute("SELECT COUNT(*) as n FROM message_bus WHERE status = 'UNREAD'")
    unread = cur.fetchone()['n']
    
    cur.close()
    conn.close()
    
    return jsonify({
        "tasks": tasks,
        "agents": agents,
        "clients": clients,
        "unread_messages": unread,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })

@app.route('/api/clients')
def client_list():
    """List all SAOS clients."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM saos_clients ORDER BY created_at DESC")
    clients = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(clients)

@app.route('/api/tasks')
def task_history():
    """Recent task history."""
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT t.id, t.task_type, t.assigned_agent, t.status, t.priority,
               t.created_at, t.completed_at,
               c.customer_name
        FROM task_queue t
        LEFT JOIN saos_clients c ON t.payload_json LIKE '%' || c.id || '%'
        ORDER BY t.created_at DESC
        LIMIT 50
    """)
    tasks = [dict(r) for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(tasks)

@app.route('/api/health')
def health_check():
    """Simple health check."""
    return jsonify({"status": "ok", "service": "saos-dashboard-api"})

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    
    print(f"🚀 SAOS Dashboard API starting on port {args.port}")
    print(f"   Endpoints:")
    print(f"   - GET /api/status   (fleet overview)")
    print(f"   - GET /api/clients  (client list)")
    print(f"   - GET /api/tasks    (task history)")
    print(f"   - GET /api/health   (health check)")
    
    app.run(host='0.0.0.0', port=args.port, debug=False)
