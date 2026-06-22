#!/usr/bin/env python3
"""Simple HTML dashboard generator — no f-string format issues"""

from web_dashboard import fetch_dashboard_data
import datetime

data = fetch_dashboard_data()

html_parts = []
html_parts.append("""<!DOCTYPE html>
<html>
<head><title>SOL Dashboard</title><meta charset=utf-8><meta http-equiv=refresh content=10>
<style>
body{font-family:monospace;background:#0a0a0a;color:#e0e0e0;padding:20px}
h1{color:#00ff88} h2{color:#00ccff;border-bottom:1px solid #333;padding:5px 0}
.card{background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:15px;margin:10px 0}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.85em;font-weight:bold}
.status-done{background:#00ff88;color:#000} .status-pending{background:#ffaa00;color:#000}
.status-running{background:#00aaff;color:#fff} .status-failed{background:#ff4444;color:#fff}
.status-idle{background:#00ff88;color:#000} .status-busy{background:#00aaff;color:#fff}
table{width:100%;border-collapse:collapse;margin-top:10px}
th{text-align:left;padding:8px;color:#00ccff;border-bottom:1px solid #333}
td{padding:8px;border-bottom:1px solid #222;font-size:.9em}
.mono{font-family:monospace;font-size:.85em}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px}
</style>
</head>
<body>
<h1>🤖 SOL Orchestrator</h1>
<p>Last updated: """)
html_parts.append(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S CDT'))
html_parts.append("""</p>""")

# Task counts
html_parts.append("<h2>📊 Tasks</h2><div class=grid>")
for status in ['PENDING','RUNNING','DONE','FAILED','DEAD']:
    count = data['task_counts'].get(status, 0)
    html_parts.append(f'<div class=card><span class="badge status-{status.lower()}">{status}</span>: <b>{count}</b></div>')
html_parts.append("</div>")

# Agents
html_parts.append("<h2>🤖 Agents</h2><div class=grid>")
for agent in data['agents']:
    status = agent['status'].lower()
    task = f"Task #{agent['current_task_id']}" if agent['current_task_id'] else "None"
    caps = ", ".join(agent['capability_tags'][:3])
    html_parts.append(f'''<div class=card>
<b>{agent['agent_name']}</b> <span class="badge status-{status}">{agent['status']}</span><br>
Task: {task} | Done: {agent['total_tasks_completed']} | Failed: {agent['total_tasks_failed']}<br>
<span class=mono style=color:#ffaa00>{caps}</span>
</div>''')
html_parts.append("</div>")

# Recent tasks
html_parts.append("<h2>📋 Recent Tasks</h2><table><tr><th>ID</th><th>Type</th><th>Status</th><th>Agent</th><th>Prio</th><th>Updated</th></tr>")
for t in data['recent_tasks'][:10]:
    badge = f'status-{t["status"].lower()}'
    html_parts.append(f'''<tr>
<td class=mono>#{t['id']}</td><td>{t['task_type']}</td>
<td><span class="badge {badge}">{t['status']}</span></td>
<td class=mono>{t['assigned_agent'] or "—"}</td><td>{t['priority']}</td>
<td class=mono>{t['updated']}</td>
</tr>''')
html_parts.append("</table>")

# Model limits
html_parts.append("<h2>⚙️ Model Token Limits</h2><div class=grid>")
models = {
    "llama3.2:3b": {"ctx": "128K", "prompt": "16K", "size": "2.0GB"},
    "qwen2.5-coder:7b": {"ctx": "32K", "prompt": "8K", "size": "4.7GB"},
    "llama3.1:8b": {"ctx": "128K", "prompt": "16K", "size": "4.9GB"},
}
for name, info in models.items():
    html_parts.append(f'''<div class=card>
<b style=color:#ffaa00>{name}</b><br>
Context: {info['ctx']} | Prompt Limit: {info['prompt']} | Size: {info['size']}
</div>''')
html_parts.append("</div></body></html>")

# Write
full_html = "\n".join(html_parts)
with open("dashboard.html", "w") as f:
    f.write(full_html)

print(f"Dashboard saved: dashboard.html ({len(full_html)} bytes)")
