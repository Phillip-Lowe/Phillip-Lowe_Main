#!/usr/bin/env python3
"""
Load synthetic invoice dataset into AR/AP database.
This seeds the database with 120 ground-truth labeled invoices.
"""

import json
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, '/Users/philliplowe/.openclaw/workspaces/sol')
from invoice_db import init_db

DB_PATH = Path('/Users/philliplowe/.openclaw/workspaces/sol/invoice_data.db')
DATASET_PATH = Path('/Users/philliplowe/.openclaw/workspaces/sol/Invoice Parser Examples/synthetic-invoices-120.json')


def load_synthetic_data():
    """Load the 120 synthetic invoices into AR/AP tables."""
    
    # Read dataset
    with open(DATASET_PATH, 'r') as f:
        invoices = json.load(f)
    
    # Initialize DB
    init_db()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    ar_count = 0
    ap_count = 0
    
    for inv in invoices:
        direction = inv.get('direction')
        invoice_id = inv.get('invoice_id')
        
        # Insert into normalized table
        cursor.execute("""
            INSERT OR REPLACE INTO invoices_normalized 
            (invoice_id, direction, invoice_number, invoice_date, due_date,
             entity_issuer_name, entity_receiver_name,
             subtotal, tax, discount, total, currency,
             payment_status, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_id,
            direction,
            invoice_id,
            inv.get('invoice_date'),
            None,  # due_date not in synthetic data
            inv.get('entity_issuer'),
            inv.get('entity_receiver'),
            inv.get('financials', {}).get('subtotal'),
            inv.get('financials', {}).get('tax'),
            None,  # discount
            inv.get('financials', {}).get('total'),
            inv.get('financials', {}).get('currency', 'USD'),
            inv.get('payment', {}).get('status', 'UNPAID'),
            1.0  # Ground truth = perfect confidence
        ))
        
        # Route to AR or AP table
        if direction == 'INBOUND':
            cursor.execute("""
                INSERT OR REPLACE INTO accounts_receivable
                (invoice_id, customer_name, amount_due, amount_paid, status, due_date,
                 ledger_debit, ledger_credit, journal_entry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                inv.get('entity_receiver'),
                inv.get('financials', {}).get('total'),
                0,
                inv.get('payment', {}).get('status', 'UNPAID'),
                None,
                'Accounts Receivable',
                'Revenue',
                json.dumps({
                    'type': 'AR',
                    'debit': 'Accounts Receivable',
                    'credit': 'Revenue',
                    'amount': inv.get('financials', {}).get('total')
                })
            ))
            ar_count += 1
            
        elif direction == 'OUTBOUND':
            cursor.execute("""
                INSERT OR REPLACE INTO accounts_payable
                (invoice_id, vendor_name, amount_due, amount_paid, status, due_date,
                 ledger_debit, ledger_credit, journal_entry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                inv.get('entity_issuer'),
                inv.get('financials', {}).get('total'),
                0,
                inv.get('payment', {}).get('status', 'UNPAID'),
                None,
                'Expense / COGS',
                'Accounts Payable',
                json.dumps({
                    'type': 'AP',
                    'debit': 'Expense / COGS',
                    'credit': 'Accounts Payable',
                    'amount': inv.get('financials', {}).get('total')
                })
            ))
            ap_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Loaded {len(invoices)} invoices")
    print(f"   AR (INBOUND):  {ar_count}")
    print(f"   AP (OUTBOUND): {ap_count}")
    print(f"   Total value: ${sum(inv.get('financials', {}).get('total', 0) for inv in invoices):,.2f}")


def verify_data():
    """Verify the loaded data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check normalized
    cursor.execute("SELECT COUNT(*) FROM invoices_normalized")
    norm_count = cursor.fetchone()[0]
    
    # Check AR
    cursor.execute("SELECT COUNT(*), SUM(amount_due) FROM accounts_receivable")
    ar_count, ar_total = cursor.fetchone()
    
    # Check AP
    cursor.execute("SELECT COUNT(*), SUM(amount_due) FROM accounts_payable")
    ap_count, ap_total = cursor.fetchone()
    
    # Check status breakdown
    cursor.execute("SELECT status, COUNT(*) FROM accounts_receivable GROUP BY status")
    ar_status = cursor.fetchall()
    
    cursor.execute("SELECT status, COUNT(*) FROM accounts_payable GROUP BY status")
    ap_status = cursor.fetchall()
    
    conn.close()
    
    print(f"\n📊 Database Summary:")
    print(f"   Normalized invoices: {norm_count}")
    print(f"   AR records: {ar_count} (${ar_total or 0:,.2f})")
    print(f"   AP records: {ap_count} (${ap_total or 0:,.2f})")
    print(f"   AR Status: {ar_status}")
    print(f"   AP Status: {ap_status}")


if __name__ == '__main__':
    load_synthetic_data()
    verify_data()
