#!/usr/bin/env python3
"""
White-Label Dashboard Scaffolding
===================================
Generates client-branded dashboard files for Enterprise tier deployments.

Usage:
    python3 generate_dashboard.py --client-id ACME-CORP --brand-color '#ff6600' \\
        --logo-url 'https://client.com/logo.png' --output-dir /var/www/dashboard
"""
import os
import sys
import json
import argparse
from datetime import datetime

# ─── DASHBOARD TEMPLATES ────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{client_name}} — Operations Dashboard</title>
    <link rel="stylesheet" href="assets/dashboard.css">
    <link rel="icon" href="{{favicon_url}}">
</head>
<body>
    <header class="app-header">
        <div class="brand-bar" style="background: linear-gradient(135deg, {{primary_color}}, {{accent_color}});">
            <img src="{{logo_url}}" alt="{{client_name}}" class="client-logo">
            <div class="header-meta">
                <span class="tier-badge">{{tier}}</span>
                <span class="status-indicator status-ok">● All Systems Operational</span>
            </div>
        </div>
        <nav class="main-nav">
            <a href="#overview" class="nav-item active">Overview</a>
            <a href="#agents" class="nav-item">Agents</a>
            <a href="#locations" class="nav-item">Locations</a>
            <a href="#compliance" class="nav-item">Compliance</a>
            <a href="#audit" class="nav-item">Audit Log</a>
            <a href="#backups" class="nav-item">Backups</a>
        </nav>
    </header>

    <main class="dashboard-content">
        <!-- Overview Cards -->
        <section id="overview" class="card-grid">
            <div class="metric-card">
                <div class="metric-value" id="uptime-value">99.98%</div>
                <div class="metric-label">Uptime (30d)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="tasks-value">{{task_count}}</div>
                <div class="metric-label">Tasks Completed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="locations-value">{{location_count}}</div>
                <div class="metric-label">Active Locations</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="agents-value">{{agent_count}}</div>
                <div class="metric-label">AI Agents Active</div>
            </div>
        </section>

        <!-- Agent Status -->
        <section id="agents" class="content-section">
            <h2>Agent Fleet Status</h2>
            <div class="agent-grid" id="agent-status-container">
                {{agent_cards}}
            </div>
        </section>

        <!-- Location Map -->
        <section id="locations" class="content-section">
            <h2>Multi-Location Infrastructure</h2>
            <div class="location-list" id="location-container">
                {{location_cards}}
            </div>
        </section>

        <!-- Compliance Dashboard -->
        <section id="compliance" class="content-section">
            <h2>Compliance Status</h2>
            <div class="compliance-grid">
                {{compliance_cards}}
            </div>
        </section>

        <!-- Audit Log -->
        <section id="audit" class="content-section">
            <h2>Audit Log</h2>
            <div class="table-container">
                <table class="data-table" id="audit-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Event</th>
                            <th>User</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="audit-body">
                        {{audit_rows}}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Backup Status -->
        <section id="backups" class="content-section">
            <h2>Backup Status</h2>
            <div class="backup-grid">
                <div class="backup-card">
                    <div class="backup-icon">💾</div>
                    <div class="backup-info">
                        <div class="backup-title">Last Snapshot</div>
                        <div class="backup-time" id="last-backup">{{last_backup}}</div>
                    </div>
                </div>
                <div class="backup-card">
                    <div class="backup-icon">📦</div>
                    <div class="backup-info">
                        <div class="backup-title">Retention</div>
                        <div class="backup-time">{{retention_days}} days</div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="dashboard-footer">
        <p>Powered by <a href="https://systack.net" target="_blank">SyStack</a> | 
           <a href="/docs/privacy">Privacy</a> | 
           <a href="/docs/terms">Terms</a> | 
           <a href="/docs/compliance">Compliance</a></p>
        <p class="version">Dashboard v1.0 | Generated: {{generated_at}}</p>
    </footer>

    <script src="assets/dashboard.js"></script>
</body>
</html>
"""

CSS_TEMPLATE = """:root {
    --primary: {{primary_color}};
    --accent: {{accent_color}};
    --navy: #001a2d;
    --white: #ffffff;
    --gray-50: #f8fafc;
    --gray-100: #f1f5f9;
    --gray-200: #e2e8f0;
    --gray-400: #94a3b8;
    --gray-600: #475569;
    --gray-800: #1e293b;
    --success: #22c55e;
    --warning: #eab308;
    --error: #ef4444;
    --shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background: var(--gray-50);
    color: var(--gray-800);
    line-height: 1.6;
}

.app-header { background: var(--white); box-shadow: var(--shadow); }

.brand-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 2rem;
    color: var(--white);
}

.client-logo { height: 40px; filter: brightness(0) invert(1); }

.header-meta { display: flex; align-items: center; gap: 1rem; }

.tier-badge {
    background: rgba(255,255,255,0.2);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-indicator { font-size: 0.875rem; }
.status-ok { color: #86efac; }

.main-nav {
    display: flex;
    gap: 0;
    padding: 0 2rem;
    border-bottom: 1px solid var(--gray-200);
}

.nav-item {
    padding: 0.875rem 1.25rem;
    color: var(--gray-600);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
}

.nav-item:hover, .nav-item.active {
    color: var(--primary);
    border-bottom-color: var(--primary);
}

.dashboard-content { padding: 2rem; max-width: 1400px; margin: 0 auto; }

.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--white);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    text-align: center;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary);
    line-height: 1;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.875rem;
    color: var(--gray-600);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.content-section {
    background: var(--white);
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow);
}

.content-section h2 {
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
    color: var(--gray-800);
}

.agent-grid, .location-list, .compliance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.agent-card, .location-card, .compliance-card {
    border: 1px solid var(--gray-200);
    border-radius: 8px;
    padding: 1.25rem;
    transition: all 0.2s;
}

.agent-card:hover, .location-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(0,161,219,0.1);
}

.agent-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}

.agent-emoji { font-size: 1.5rem; }

.agent-name { font-weight: 600; }

.agent-status {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-left: auto;
}

.status-online { background: var(--success); }
.status-busy { background: var(--warning); }
.status-offline { background: var(--error); }

.table-container { overflow-x: auto; }

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}

.data-table th {
    text-align: left;
    padding: 0.75rem;
    border-bottom: 2px solid var(--gray-200);
    color: var(--gray-600);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
}

.data-table td {
    padding: 0.75rem;
    border-bottom: 1px solid var(--gray-100);
    color: var(--gray-600);
}

.data-table tr:hover td { background: var(--gray-50); }

.backup-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.backup-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem;
    background: var(--gray-50);
    border-radius: 8px;
}

.backup-icon { font-size: 1.5rem; }

.backup-title { font-size: 0.875rem; font-weight: 600; color: var(--gray-800); }
.backup-time { font-size: 0.75rem; color: var(--gray-600); margin-top: 0.25rem; }

.dashboard-footer {
    text-align: center;
    padding: 2rem;
    color: var(--gray-400);
    font-size: 0.875rem;
}

.dashboard-footer a { color: var(--accent); text-decoration: none; }
.dashboard-footer a:hover { text-decoration: underline; }

.version { margin-top: 0.5rem; font-size: 0.75rem; }
"""

JS_TEMPLATE = """// SyStack White-Label Dashboard JS
// Auto-refreshes every 30 seconds

const CONFIG = {
    refreshInterval: 30000,
    apiBase: '/api/v1',
    clientId: '{{client_id}}'
};

// Mock data for scaffolding — replace with real API calls
const AGENTS = [
    { name: 'Invoice Agent', emoji: '📄', status: 'online', tasks: 245 },
    { name: 'Booking Agent', emoji: '📅', status: 'online', tasks: 189 },
    { name: 'Communication', emoji: '💬', status: 'busy', tasks: 56 },
    { name: 'Compliance', emoji: '⚖️', status: 'online', tasks: 12 },
    { name: 'Analytics', emoji: '📊', status: 'online', tasks: 78 }
];

const LOCATIONS = [
    { region: 'ord', name: 'Chicago', status: 'active', ip: '192.0.2.1', uptime: '99.99%' },
    { region: 'lax', name: 'Los Angeles', status: 'active', ip: '192.0.2.2', uptime: '99.97%' },
    { region: 'lon', name: 'London', status: 'active', ip: '192.0.2.3', uptime: '99.98%' }
];

const COMPLIANCE = [
    { framework: 'SOC 2 Type I', status: 'ready', last_audit: '2026-06-01' },
    { framework: 'GDPR', status: 'ready', last_audit: '2026-06-01' },
    { framework: 'HIPAA', status: 'pending', last_audit: '—' },
    { framework: 'CCPA', status: 'ready', last_audit: '2026-06-01' }
];

function renderAgents() {
    const container = document.getElementById('agent-status-container');
    if (!container) return;
    
    container.innerHTML = AGENTS.map(agent => `
        <div class="agent-card">
            <div class="agent-header">
                <span class="agent-emoji">${agent.emoji}</span>
                <span class="agent-name">${agent.name}</span>
                <span class="agent-status status-${agent.status}"></span>
            </div>
            <div style="font-size: 0.875rem; color: var(--gray-600);">
                ${agent.tasks} tasks completed today
            </div>
        </div>
    `).join('');
}

function renderLocations() {
    const container = document.getElementById('location-container');
    if (!container) return;
    
    container.innerHTML = LOCATIONS.map(loc => `
        <div class="location-card">
            <div class="agent-header">
                <span class="agent-emoji">🌍</span>
                <span class="agent-name">${loc.name} (${loc.region.toUpperCase()})</span>
                <span class="agent-status status-${loc.status === 'active' ? 'online' : 'offline'}"></span>
            </div>
            <div style="font-size: 0.875rem; color: var(--gray-600); margin-top: 0.5rem;">
                IP: ${loc.ip} | Uptime: ${loc.uptime}
            </div>
        </div>
    `).join('');
}

function renderCompliance() {
    const container = document.querySelector('.compliance-grid');
    if (!container) return;
    
    container.innerHTML = COMPLIANCE.map(item => `
        <div class="compliance-card">
            <div class="agent-header">
                <span class="agent-emoji">${item.status === 'ready' ? '✅' : '⏳'}</span>
                <span class="agent-name">${item.framework}</span>
                <span style="margin-left: auto; font-size: 0.75rem; color: ${item.status === 'ready' ? 'var(--success)' : 'var(--warning)'};">
                    ${item.status.toUpperCase()}
                </span>
            </div>
            <div style="font-size: 0.875rem; color: var(--gray-600); margin-top: 0.5rem;">
                Last audit: ${item.last_audit}
            </div>
        </div>
    `).join('');
}

function init() {
    renderAgents();
    renderLocations();
    renderCompliance();
    
    // Auto-refresh
    setInterval(() => {
        renderAgents();
        renderLocations();
    }, CONFIG.refreshInterval);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
"""


# ─── GENERATOR ────────────────────────────────────────────────────────────────

class DashboardGenerator:
    """Generates white-label dashboard files for Enterprise clients."""
    
    def __init__(self, client_id: str, brand_config: dict):
        self.client_id = client_id
        self.config = {
            "client_name": brand_config.get("name", client_id),
            "primary_color": brand_config.get("primary_color", "#001a2d"),
            "accent_color": brand_config.get("accent_color", "#00a1db"),
            "logo_url": brand_config.get("logo_url", "/assets/default-logo.png"),
            "favicon_url": brand_config.get("favicon_url", "/assets/default-favicon.ico"),
            "tier": brand_config.get("tier", "Enterprise"),
            "locations": brand_config.get("locations", ["ord"]),
            "compliance": brand_config.get("compliance", ["SOC2"]),
            "task_count": brand_config.get("task_count", 0),
            "agent_count": brand_config.get("agent_count", 10),
            "last_backup": brand_config.get("last_backup", "Never"),
            "retention_days": brand_config.get("retention_days", 30),
        }
    
    def generate(self, output_dir: str):
        """Generate all dashboard files."""
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/assets", exist_ok=True)
        
        # Generate HTML
        html = self._render_template(HTML_TEMPLATE)
        with open(f"{output_dir}/index.html", "w") as f:
            f.write(html)
        
        # Generate CSS
        css = self._render_template(CSS_TEMPLATE)
        with open(f"{output_dir}/assets/dashboard.css", "w") as f:
            f.write(css)
        
        # Generate JS
        js = self._render_template(JS_TEMPLATE)
        with open(f"{output_dir}/assets/dashboard.js", "w") as f:
            f.write(js)
        
        # Generate config JSON
        config = {
            "client_id": self.client_id,
            "generated_at": datetime.utcnow().isoformat(),
            **self.config
        }
        with open(f"{output_dir}/config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"📄 Dashboard generated: {output_dir}")
        print(f"   Files: index.html, assets/dashboard.css, assets/dashboard.js, config.json")
        
        return output_dir
    
    def _render_template(self, template: str) -> str:
        """Replace template variables with config values."""
        result = template
        for key, value in self.config.items():
            placeholder = f"{{{{{key}}}}}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        
        # Generate dynamic content
        result = result.replace("{{agent_cards}}", self._generate_agent_cards())
        result = result.replace("{{location_cards}}", self._generate_location_cards())
        result = result.replace("{{compliance_cards}}", self._generate_compliance_cards())
        result = result.replace("{{audit_rows}}", self._generate_audit_rows())
        result = result.replace("{{generated_at}}", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"))
        
        return result
    
    def _generate_agent_cards(self) -> str:
        agents = [
            {"name": "Invoice Agent", "emoji": "📄", "status": "online", "tasks": 245},
            {"name": "Booking Agent", "emoji": "📅", "status": "online", "tasks": 189},
            {"name": "Communication", "emoji": "💬", "status": "busy", "tasks": 56},
            {"name": "Compliance", "emoji": "⚖️", "status": "online", "tasks": 12}
        ]
        return "\n".join([
            f'                <div class="agent-card"><div class="agent-header">'
            f'<span class="agent-emoji">{a["emoji"]}</span>'
            f'<span class="agent-name">{a["name"]}</span>'
            f'<span class="agent-status status-{a["status"]}"></span></div>'
            f'<div style="font-size: 0.875rem; color: var(--gray-600);">'
            f'{a["tasks"]} tasks completed today</div></div>'
            for a in agents
        ])
    
    def _generate_location_cards(self) -> str:
        locations = self.config.get("locations", [])
        region_names = {"ord": "Chicago", "lax": "Los Angeles", "lon": "London", 
                       "ams": "Amsterdam", "fra": "Frankfurt"}
        return "\n".join([
            f'                <div class="location-card"><div class="agent-header">'
            f'<span class="agent-emoji">🌍</span>'
            f'<span class="agent-name">{region_names.get(loc, loc)} ({loc.upper()})</span>'
            f'<span class="agent-status status-online"></span></div>'
            f'<div style="font-size: 0.875rem; color: var(--gray-600); margin-top: 0.5rem;">'
            f'Uptime: 99.98% | Status: Active</div></div>'
            for loc in locations
        ])
    
    def _generate_compliance_cards(self) -> str:
        compliance = self.config.get("compliance", ["SOC2"])
        frameworks = {
            "SOC2": {"name": "SOC 2 Type I", "status": "ready", "icon": "✅"},
            "HIPAA": {"name": "HIPAA", "status": "pending", "icon": "⏳"},
            "GDPR": {"name": "GDPR", "status": "ready", "icon": "✅"},
            "CCPA": {"name": "CCPA", "status": "ready", "icon": "✅"}
        }
        return "\n".join([
            f'                <div class="compliance-card"><div class="agent-header">'
            f'<span class="agent-emoji">{frameworks.get(c, {}).get("icon", "⏳")}</span>'
            f'<span class="agent-name">{frameworks.get(c, {}).get("name", c)}</span>'
            f'<span style="margin-left: auto; font-size: 0.75rem; color: var(--success);">'
            f'{frameworks.get(c, {}).get("status", "pending").upper()}</span></div></div>'
            for c in compliance
        ])
    
    def _generate_audit_rows(self) -> str:
        events = [
            {"time": "2026-06-19 10:00:00", "event": "Backup completed", "user": "SYSTEM", "status": "success"},
            {"time": "2026-06-19 09:30:00", "event": "Agent deployment", "user": "SOL", "status": "success"},
            {"time": "2026-06-19 09:00:00", "event": "Compliance scan", "user": "JURIS", "status": "success"}
        ]
        return "\n".join([
            f'                        <tr><td>{e["time"]}</td><td>{e["event"]}</td>'
            f'<td>{e["user"]}</td><td><span style="color: var(--success);">✓</span></td></tr>'
            for e in events
        ])


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate white-label dashboard")
    parser.add_argument("--client-id", required=True, help="Client identifier")
    parser.add_argument("--client-name", default=None, help="Display name (defaults to client-id)")
    parser.add_argument("--primary-color", default="#001a2d", help="Brand primary color")
    parser.add_argument("--accent-color", default="#00a1db", help="Brand accent color")
    parser.add_argument("--logo-url", default="/assets/client-logo.png", help="Logo URL")
    parser.add_argument("--locations", default="ord", help="Comma-separated regions")
    parser.add_argument("--compliance", default="SOC2", help="Comma-separated compliance flags")
    parser.add_argument("--output-dir", default=None, help="Output directory")
    
    args = parser.parse_args()
    
    brand_config = {
        "name": args.client_name or args.client_id,
        "primary_color": args.primary_color,
        "accent_color": args.accent_color,
        "logo_url": args.logo_url,
        "locations": [l.strip() for l in args.locations.split(",")],
        "compliance": [c.strip() for c in args.compliance.split(",")]
    }
    
    output = args.output_dir or f"/tmp/systack-saas-init/dashboards/{args.client_id}"
    
    gen = DashboardGenerator(args.client_id, brand_config)
    gen.generate(output)
    
    print(f"\n✅ Dashboard ready: {output}")
    print(f"   Open: file://{output}/index.html")


if __name__ == "__main__":
    main()
