#!/usr/bin/env python3
"""
Invoice Database Layer
SQLite backend for invoice pipeline.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "invoice_data.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            vendor TEXT,
            invoice_date TEXT,
            invoice_number TEXT,
            subtotal REAL,
            tax REAL,
            total REAL,
            raw_text TEXT,
            parsed_json TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'email'
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            item_name TEXT,
            price REAL,
            FOREIGN KEY (invoice_id) REFERENCES invoices(id)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices_normalized (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT UNIQUE,
            direction TEXT,
            invoice_number TEXT,
            invoice_date TEXT,
            due_date TEXT,
            entity_issuer_name TEXT,
            entity_receiver_name TEXT,
            subtotal REAL,
            tax REAL,
            discount REAL,
            total REAL,
            currency TEXT DEFAULT 'USD',
            payment_status TEXT,
            payment_method TEXT,
            payment_terms TEXT,
            confidence_score REAL,
            raw_invoice_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts_receivable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            customer_name TEXT,
            amount_due REAL,
            amount_paid REAL DEFAULT 0,
            status TEXT DEFAULT 'UNPAID',
            due_date TEXT,
            ledger_debit TEXT,
            ledger_credit TEXT,
            journal_entry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts_payable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            vendor_name TEXT,
            amount_due REAL,
            amount_paid REAL DEFAULT 0,
            status TEXT DEFAULT 'UNPAID',
            due_date TEXT,
            ledger_debit TEXT,
            ledger_credit TEXT,
            journal_entry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS review_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT,
            reason TEXT,
            raw_data TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"[DB] Initialized: {DB_PATH}")


def save_invoice(file_name, vendor, invoice_date, invoice_number, subtotal, tax, total, raw_text, parsed_json, source="api"):
    """Save parsed invoice to database."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO invoices (file_name, vendor, invoice_date, invoice_number, subtotal, tax, total, raw_text, parsed_json, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (file_name, vendor, invoice_date, invoice_number, subtotal, tax, total, raw_text, parsed_json, source))
    
    invoice_id = cur.lastrowid
    conn.commit()
    conn.close()
    return invoice_id


def get_invoices(limit=50, offset=0):
    """Get recent invoices."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices ORDER BY processed_at DESC LIMIT ? OFFSET ?", (limit, offset))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice_count():
    """Get total invoice count."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM invoices")
    count = cur.fetchone()[0]
    conn.close()
    return count


if __name__ == '__main__':
    init_db()
    print(f"Database initialized at: {DB_PATH}")
    print(f"Total invoices: {get_invoice_count()}")
