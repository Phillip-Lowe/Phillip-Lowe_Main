---
name: dashboard-api
description: "Build lightweight HTML dashboards backed by SQLite or Postgres with REST API endpoints, real-time data views, and mobile-responsive design."
---

# Dashboard API

Build real-time HTML dashboards for business data. SQLite/Postgres backend + Python HTTP API + vanilla JS frontend. No framework dependencies.

## When to Use
- Client needs to view invoice/order/booking data
- Real-time metrics display (revenue, counts, trends)
- Admin panel for automation monitoring
- Mobile-friendly data viewer for field staff

## Architecture

```
SQLite/Postgres
    ↓
Python HTTPServer (or FastAPI)
    ↓
REST API (JSON)
    ↓
Vanilla JS Frontend
    ↓
Responsive HTML Table/Cards
```

## Quick Start

```python
#!/usr/bin/env python3
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = "data.db"
PORT = 9001

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if self.path == "/api/invoices":
            cursor.execute("SELECT * FROM invoices ORDER BY created_at DESC LIMIT 50")
            rows = [dict(r) for r in cursor.fetchall()]
            self._send_json(200, rows)
        elif self.path == "/api/stats":
            cursor.execute("SELECT COUNT(*), SUM(total) FROM invoices")
            total = cursor.fetchone()
            self._send_json(200, {"count": total[0], "revenue": total[1]})
        
        conn.close()

HTTPServer(("", PORT), Handler).serve_forever()
```

## Frontend Pattern

```html
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; margin: 0; padding: 20px; background: #f8fafc; }
    .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stat { font-size: 32px; font-weight: bold; color: #001a2d; }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
    th { background: #001a2d; color: white; }
    tr:hover { background: #f1f5f9; }
    @media (max-width: 600px) {
      .card { padding: 15px; }
      table { font-size: 14px; }
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="stat" id="total-revenue">$0</div>
    <div>Total Revenue (This Month)</div>
  </div>
  <div id="invoices-table"></div>
  
  <script>
    async function loadStats() {
      const res = await fetch('/api/stats');
      const data = await res.json();
      document.getElementById('total-revenue').textContent = '$' + data.revenue?.toFixed(2) || 0;
    }
    
    async function loadInvoices() {
      const res = await fetch('/api/invoices');
      const invoices = await res.json();
      let html = '<table><tr><th>Vendor</th><th>Amount</th><th>Date</th></tr>';
      invoices.forEach(inv => {
        html += `<tr><td>${inv.vendor_name}</td><td>$${inv.total}</td><td>${inv.invoice_date}</td></tr>`;
      });
      html += '</table>';
      document.getElementById('invoices-table').innerHTML = html;
    }
    
    loadStats();
    loadInvoices();
    setInterval(loadStats, 30000); // Refresh every 30s
  </script>
</body>
</html>
```

## Endpoints Pattern

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/items` | List items (paginated) |
| GET | `/api/items/:id` | Single item |
| GET | `/api/stats` | Aggregated stats |
| POST | `/api/items` | Create item |
| PUT | `/api/items/:id` | Update item |
| DELETE | `/api/items/:id` | Delete item |

## Database Agnostic

Switch between SQLite and Postgres with minimal changes:

```python
# SQLite
conn = sqlite3.connect(DB_PATH)
cursor.execute("SELECT * FROM table WHERE id = ?", (id,))

# Postgres (psycopg2)
conn = psycopg2.connect(**DB_CONFIG)
cursor.execute("SELECT * FROM table WHERE id = %s", (id,))
```

## Security

- **CORS**: Limit to known origins
- **Authentication**: Add API key header check for admin endpoints
- **Input validation**: Sanitize all URL params and query inputs
- **Rate limiting**: Implement if public-facing

## Deployment

```bash
# Start dashboard server
python3 dashboard_server.py 9001

# Or as systemd service for production
cat > /etc/systemd/system/dashboard.service << EOF
[Unit]
Description=Dashboard API
After=network.target

[Service]
User=systack
WorkingDirectory=/opt/dashboard
ExecStart=/usr/bin/python3 dashboard_server.py 9001
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

## Common Dashboard Types

| Type | Tables | Key Metrics |
|------|--------|-------------|
| **Invoice** | invoices, items | Total spent, vendor breakdown, monthly trend |
| **Orders** | orders, items | Daily revenue, popular items, fulfillment rate |
| **Bookings** | bookings, customers | Upcoming appointments, no-show rate, revenue |
| **Leads** | leads, activities | Conversion rate, source breakdown, follow-ups |
| **Monitoring** | error_logs, executions | Success rate, error count, latency |

## Files

- `templates/private/dashboard.html` — Generic dashboard template
- `saos/dashboard/index.html` — SAOS fleet dashboard
- `dashboard-demo/` — Demo implementation
