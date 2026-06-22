#!/usr/bin/env python3
"""
SOL Orchestrator Web Dashboard
- Simple HTTP server showing task status, agent state, recent activity
- Read-only view of Postgres data
- Auto-refreshes every 10 seconds

Usage:
    python3 web_dashboard.py          # Start on port 8080
    python3 web_dashboard.py --port 9090
    
Then open: http://localhost:8080
"""

import os, sys, json, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

# ── CONFIG ─────────────────────────────────────────────────────────
DEFAULT_PORT = 8080
DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": int(os.environ.get("PGPORT", "5432")),
    "dbname": os.environ.get("PGDATABASE", "systack_memory"),
    "user": os.environ.get("PGUSER", "philliplowe"),
    "password": os.environ.get("PGPASSWORD", ""),
}

# ── DATA FETCHING ──────────────────────────────────────────────────
def get_db():
    return psycopg2.connect(**DB_CONFIG)

def fetch_dashboard_data():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT status, COUNT(*) as n FROM task_queue GROUP BY status")
    task_counts = {r['status']: r['n'] for r in cur.fetchall()}
    
    cur.execute("SELECT * FROM agent_state ORDER BY agent_name")
    agents = [dict(r) for r in cur.fetchall()]
    
    cur.execute("""
        SELECT id, task_type, status, assigned_agent, priority, 
               to_char(created_at, 'HH24:MI:SS') as created,
               to_char(updated_at, 'HH24:MI:SS') as updated
        FROM task_queue ORDER BY updated_at DESC LIMIT 15
    """)
    recent_tasks = [dict(r) for r in cur.fetchall()]
    
    cur.execute("SELECT COUNT(*) as n FROM message_bus WHERE status = 'UNREAD'")
    unread = cur.fetchone()['n']
    
    cur.execute("""
        SELECT task_id, agent, step_action, 
               COALESCE(error_message, '') as error,
               to_char(created_at, 'HH24:MI:SS') as time
        FROM execution_log ORDER BY created_at DESC LIMIT 10
    """)
    recent_log = [dict(r) for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return {
        "task_counts": task_counts,
        "agents": agents,
        "recent_tasks": recent_tasks,
        "unread_messages": unread,
        "recent_log": recent_log,
    }

# ── HTML RENDERING ─────────────────────────────────────────────────
def render_dashboard(data):
    parts = []
    
    # Head
    parts.append("""<!DOCTYPE html>
<html>
<head><title>SOL Dashboard</title><meta charset=utf-8><meta http-equiv=refresh content=10>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,monospace;background:#0a0a0a;color:#e0e0e0;padding:20px;line-height:1.6}
h1{color:#00ff88;margin-bottom:10px} h2{color:#00ccff;border-bottom:1px solid #333;padding:5px 0;margin-top:20px}
.card{background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:15px;transition:border-color .2s}
.card:hover{border-color:#00ff88}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.85em;font-weight:bold;margin-right:5px}
.status-done{background:#00ff88;color:#000} .status-pending{background:#ffaa00;color:#000}
.status-running{background:#00aaff;color:#fff} .status-failed{background:#ff4444;color:#fff}
.status-dead{background:#888;color:#000} .status-idle{background:#00ff88;color:#000}
.status-busy{background:#00aaff;color:#fff} .status-error{background:#ff4444;color:#fff}
table{width:100%;border-collapse:collapse;margin-top:10px}
th{text-align:left;padding:8px;color:#00ccff;border-bottom:1px solid #333;font-size:.9em}
td{padding:8px;border-bottom:1px solid #222;font-size:.9em;vertical-align:top}
tr:hover{background:#1a1a1a}
.mono{font-family:'SF Mono',Monaco,monospace;font-size:.85em}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:15px;margin-bottom:10px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px}
.timestamp{color:#888;font-size:.9em}
.refresh-bar{position:fixed;top:0;left:0;height:2px;background:linear-gradient(90deg,#00ff88,#00ccff);animation:progress 10s linear infinite}
@keyframes progress{from{width:0%}to{width:100%}}
.model-name{color:#ffaa00;font-weight:bold} .model-limits{color:#888;font-size:.85em}
</style>
</head>
<body>
<div class=refresh-bar></div>
<div class=header>
<div><h1>🤖 SOL Orchestrator</h1><div class=timestamp>""")
    parts.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S CDT'))
    parts.append("""</div></div>
<div class=timestamp>Auto-refresh: 10s | <a href=/api/status style=color:#00ccff>API</a></div>
</div>""")
    
    # Task counts
    parts.append("<h2>📊 Task Overview</h2><div class=grid>")
    for status in ['PENDING','RUNNING','DONE','FAILED','DEAD']:
        count = data['task_counts'].get(status, 0)
        parts.append(f'<div class=card><span class="badge status-{status.lower()}">{status}</span><span style="font-size:1.5em;font-weight:bold">{count}</span></div>')
    parts.append("</div>")
    
    # Agents
    parts.append("<h2>🤖 Agent Status</h2><div class=grid>")
    for agent in data['agents']:
        status = agent['status'].lower()
        task = f"Task #{agent['current_task_id']}" if agent['current_task_id'] else "None"
        caps = ", ".join(agent['capability_tags'][:3])
        parts.append(f'''<div class=card>
<b>{agent['agent_name']}</b> <span class="badge status-{status}">{agent['status']}</span><br>
Task: {task} | Done: <b>{agent['total_tasks_completed']}</b> | Failed: <span style=color:#ff4444>{agent['total_tasks_failed']}</span><br>
<span class=mono style=color:#ffaa00>{caps}</span>
</div>''')
    parts.append("</div>")
    
    # Messages
    parts.append(f'''<h2>📨 Messages</h2><div class=grid>
<div class=card>Unread: <b{' style=color:#ffaa00' if data['unread_messages'] > 0 else ''}>{data['unread_messages']}</b></div>
</div>''')
    
    # Model limits
    parts.append("<h2>⚙️ Model Token Limits (Safety)</h2><div class=grid>")
    models = {
        "llama3.2:3b": {"ctx": "128K", "prompt": "16K", "size": "2.0GB", "safe": "Conservative"},
        "qwen2.5-coder:7b": {"ctx": "32K", "prompt": "8K", "size": "4.7GB", "safe": "Strict"},
        "llama3.1:8b": {"ctx": "128K", "prompt": "16K", "size": "4.9GB", "safe": "Conservative"},
    }
    for name, info in models.items():
        safe_color = "#00ff88" if info['safe'] == 'Conservative' else '#ffaa00'
        parts.append(f'''<div class=card>
<div class=model-name>{name}</div>
<div class=model-limits>Context: {info['ctx']} | Prompt Limit: <b>{info['prompt']}</b> | Size: {info['size']}</div>
<div style="color:{safe_color};font-size:.85em">Safety: {info['safe']} (never exceeds 50% capacity)</div>
</div>''')
    parts.append("</div>")
    
    # Recent tasks
    parts.append("<h2>📋 Recent Tasks</h2><table><tr><th>ID</th><th>Type</th><th>Status</th><th>Agent</th><th>Prio</th><th>Updated</th></tr>")
    for t in data['recent_tasks'][:10]:
        badge = f'status-{t["status"].lower()}'
        parts.append(f'''<tr>
<td class=mono>#{t['id']}</td><td>{t['task_type']}</td>
<td><span class="badge {badge}">{t['status']}</span></td>
<td class=mono>{t['assigned_agent'] or "—"}</td><td>{t['priority']}</td>
<td class=mono>{t['updated']}</td>
</tr>''')
    parts.append("</table>")
    
    # Recent log
    parts.append("<h2>📝 Execution Log</h2><table><tr><th>Task</th><th>Agent</th><th>Action</th><th>Error</th><th>Time</th></tr>")
    for l in data['recent_log']:
        error = l['error'][:50] + "..." if l['error'] else "—"
        error_color = "#ff4444" if l['error'] else "#888"
        parts.append(f'''<tr>
<td class=mono>#{l['task_id']}</td><td class=mono>{l['agent']}</td>
<td>{l['step_action']}</td>
<td style="color:{error_color}">{error}</td>
<td class=mono>{l['time']}</td>
</tr>''')
    parts.append("</table></body></html>")
    
    return "\n".join(parts)

# ── HTTP SERVER ────────────────────────────────────────────────────
class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            try:
                data = fetch_dashboard_data()
                html = render_dashboard(data)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(f"Error: {str(e)}".encode())
        elif self.path == "/api/status":
            try:
                data = fetch_dashboard_data()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(json.dumps(data, default=str).encode())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

# ── MAIN ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SOL Orchestrator Dashboard")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="HTTP port")
    args = parser.parse_args()
    
    server = HTTPServer(("", args.port), DashboardHandler)
    print(f"🌐 Dashboard running at http://localhost:{args.port}")
    print(f"   API: http://localhost:{args.port}/api/status")
    print(f"   Refresh: 10s | Press Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
        server.shutdown()
