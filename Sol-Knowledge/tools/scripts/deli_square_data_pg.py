#!/usr/bin/env python3
"""
deli_square_data_pg.py — Pull customer contacts from Square & save to local Postgres

Usage:
    python3 deli_square_data_pg.py

Outputs:
    - Upserts customers into local Postgres `utopia_deli` database
    - Table: `contacts` (name, email, phone, last_order_date, order_count, square_id)
    - Exports to CSV: `utopia-contacts.csv`

Requires:
    pip install requests psycopg2-binary

Environment:
    SQUARE_ACCESS_TOKEN  (from 1Password or .env)
    SQUARE_LOCATION_ID
    PG_PASSWORD          (for local Postgres)
"""

import requests
import psycopg2
import csv
import os
import sys
from datetime import datetime, timedelta

# --- CONFIG ---
ACCESS_TOKEN = os.environ.get("SQUARE_ACCESS_TOKEN", "EAAAlyODFq82nkBSiZ6J3SA4VnXoXzMGFsNZQSPUbgh7jUefGGB1X3xKY7OxuCcG")
LOCATION_ID = os.environ.get("SQUARE_LOCATION_ID", "J4B6A3X6RYA63")
BASE_URL = "https://connect.squareup.com/v2"

PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'utopia_deli',
    'user': 'philliplowe',
    'password': os.environ.get('PG_PASSWORD', ''),
}

HEADERS = {
    "Square-Version": "2023-07-22",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

CSV_FILE = "utopia-contacts.csv"


def get_db():
    """Connect to local Postgres."""
    conn = psycopg2.connect(**PG_CONFIG)
    conn.autocommit = False
    return conn


def ensure_schema():
    """Create contacts table if not exists."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            square_id VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            email VARCHAR(255),
            phone VARCHAR(50),
            last_order_date TIMESTAMP,
            order_count INTEGER DEFAULT 0,
            consent_status VARCHAR(50) DEFAULT 'implicit',
            unsubscribed_sms BOOLEAN DEFAULT FALSE,
            unsubscribed_email BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
    conn.commit()
    conn.close()
    print("[OK] Database schema ready")


def fetch_customers():
    """Pull all customers from Square API with pagination (iterative)."""
    url = f"{BASE_URL}/customers"
    customers = []
    params = {"limit": 100}
    pages = 0
    max_pages = 50  # Safety limit

    while pages < max_pages:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        batch = data.get("customers", [])
        customers.extend(batch)
        pages += 1
        print(f"  → Page {pages}: {len(batch)} customers (total: {len(customers)})")

        next_cursor = data.get("cursor")
        if not next_cursor:
            break
        params["cursor"] = next_cursor

    return customers


def fetch_orders(days_back=90):
    """Fetch recent orders to enrich customer data (iterative)."""
    url = f"{BASE_URL}/orders/search"
    start = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

    body = {
        "location_ids": [LOCATION_ID],
        "query": {
            "filter": {
                "date_time_filter": {
                    "created_at": {"start_at": start}
                }
            }
        },
        "limit": 100
    }

    orders = []
    cursor = None
    pages = 0
    max_pages = 100  # Safety limit

    while pages < max_pages:
        if cursor:
            body["cursor"] = cursor
        resp = requests.post(url, headers=HEADERS, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get("orders", [])
        orders.extend(batch)
        pages += 1
        print(f"  → Page {pages}: {len(batch)} orders (total: {len(orders)})")
        cursor = data.get("cursor")
        if not cursor:
            break
    return orders


def sync_to_postgres(customers, orders):
    """Upsert customers into Postgres with order stats."""
    conn = get_db()
    cur = conn.cursor()

    # Build order stats per customer
    customer_stats = {}
    for order in orders:
        cid = order.get("customer_id")
        if cid:
            stats = customer_stats.setdefault(cid, {"count": 0, "last_date": None})
            stats["count"] += 1
            created = order.get("created_at", "")
            if created and (stats["last_date"] is None or created > stats["last_date"]):
                stats["last_date"] = created

    inserted = 0
    updated = 0
    now = datetime.now()

    for c in customers:
        square_id = c.get("id", "")
        name_parts = [c.get("given_name", ""), c.get("family_name", "")]
        name = " ".join(p for p in name_parts if p).strip() or "Unknown"
        email = c.get("email_address", "") or None
        phone = c.get("phone_number", "") or None
        stats = customer_stats.get(square_id, {"count": 0, "last_date": None})

        cur.execute("SELECT id FROM contacts WHERE square_id = %s", (square_id,))
        row = cur.fetchone()

        if row:
            cur.execute('''
                UPDATE contacts SET
                    name = COALESCE(NULLIF(%s, 'Unknown'), name),
                    email = COALESCE(%s, email),
                    phone = COALESCE(%s, phone),
                    order_count = %s,
                    last_order_date = COALESCE(%s::timestamp, last_order_date),
                    updated_at = %s
                WHERE square_id = %s
            ''', (name, email, phone, stats["count"], stats["last_date"], now, square_id))
            updated += 1
        else:
            cur.execute('''
                INSERT INTO contacts
                (square_id, name, email, phone, order_count, last_order_date, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s::timestamp, %s, %s)
                ON CONFLICT (square_id) DO NOTHING
            ''', (square_id, name, email, phone, stats["count"], stats["last_date"], now, now))
            inserted += 1

    conn.commit()
    conn.close()
    return inserted, updated


def export_csv():
    """Export contacts with contact info to CSV."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT name, email, phone, last_order_date, order_count, consent_status
        FROM contacts
        WHERE (email IS NOT NULL AND email != '') OR (phone IS NOT NULL AND phone != '')
        ORDER BY last_order_date DESC NULLS LAST
    ''')
    rows = cur.fetchall()
    conn.close()

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "phone", "last_order_date", "order_count", "consent_status"])
        writer.writerows(rows)
    return len(rows)


def main():
    print("=" * 50)
    print("Utopia Deli — Square → Postgres Sync")
    print("=" * 50)

    print(f"\n[{datetime.now():%H:%M:%S}] Setting up database...")
    ensure_schema()

    print(f"[{datetime.now():%H:%M:%S}] Fetching customers from Square...")
    customers = fetch_customers()
    print(f"  → {len(customers)} customers found")

    print(f"[{datetime.now():%H:%M:%S}] Fetching recent orders...")
    orders = fetch_orders(days_back=90)
    print(f"  → {len(orders)} orders in last 90 days")

    print(f"[{datetime.now():%H:%M:%S}] Syncing to Postgres...")
    inserted, updated = sync_to_postgres(customers, orders)
    print(f"  → {inserted} new, {updated} updated")

    print(f"[{datetime.now():%H:%M:%S}] Exporting to CSV...")
    total = export_csv()
    print(f"  → {total} contacts exported to {CSV_FILE}")

    print(f"\n{'=' * 50}")
    print("DONE")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    main()
