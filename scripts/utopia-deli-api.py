#!/usr/bin/env python3
"""
Utopia Deli - Local Data API
Replaces Google Sheets for n8n workflow integration
"""

import sqlite3
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify

DB_PATH = os.path.expanduser("~/.openclaw/workspaces/sol/data/utopia-deli.db")
app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "time": datetime.now().isoformat()})

@app.route('/open-hours', methods=['GET'])
def get_open_hours():
    """Returns open hours schedule. Format: [day, open_time, close_time, is_open]"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT day, open_time, close_time, is_open FROM open_hours ORDER BY day_order")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"data": [[r["day"], r["open_time"], r["close_time"], r["is_open"]] for r in rows]})

@app.route('/menu', methods=['GET'])
def get_menu():
    """Returns menu catalog. Format: [item_id, name, price_cents, description, active, image_url]"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT item_id, name, price_cents, description, active, image_url FROM menu_catalog WHERE active = 1")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"data": [[r["item_id"], r["name"], r["price_cents"], r["description"], r["active"], r["image_url"]] for r in rows]})

@app.route('/tax-rate', methods=['GET'])
def get_tax_rate():
    """Returns tax rate for Little Rock. Always 9.75%"""
    return jsonify({"data": [["Little Rock", "Pulaski", 9.75]]})

@app.route('/orders', methods=['POST'])
def append_order():
    """Appends an order to the orders log."""
    data = request.get_json() or {}
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders_log (timestamp, customer_name, email, phone, city, county, 
                               entree, modifiers, subtotal_cents, tax_cents, total_cents,
                               payment_link, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("timestamp", datetime.now().isoformat()),
        data.get("customer_name", ""),
        data.get("email", ""),
        data.get("phone", ""),
        data.get("city", ""),
        data.get("county", ""),
        data.get("entree", ""),
        json.dumps(data.get("modifiers", [])),
        data.get("subtotal_cents", 0),
        data.get("tax_cents", 0),
        data.get("total_cents", 0),
        data.get("payment_link", ""),
        data.get("status", "pending")
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

@app.route('/orders', methods=['GET'])
def get_orders():
    """Returns recent orders."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders_log ORDER BY timestamp DESC LIMIT 100")
    rows = cur.fetchall()
    conn.close()
    return jsonify({"data": [dict(r) for r in rows]})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
