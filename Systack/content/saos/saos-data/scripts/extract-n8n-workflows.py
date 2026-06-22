#!/usr/bin/env python3
"""
Extract n8n workflows from SQLite backup database.
Reconstructs full workflow JSON from nodes + connections + settings columns.

Usage:
    python3 extract-n8n-workflows.py [workflow_name_pattern]
    
Examples:
    python3 extract-n8n-workflows.py "Utopia%"     # Extract Utopia workflows
    python3 extract-n8n-workflows.py "Error%"      # Extract Error Catcher
    python3 extract-n8n-workflows.py               # Extract all production workflows
"""

import sqlite3
import json
import sys
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.openclaw/workspaces/sol/n8n-backup-20260530-202509/database.sqlite")
OUTPUT_DIR = os.path.expanduser("~/.openclaw/workspaces/sol/n8n-workflows/extracted/")

# Production workflow names (exclude tests)
SKIP_PATTERNS = [
    'Test-%', 'Sol Test%', 'My workflow%', 'SOL-Test%', 'SOL-%',
    'Build Your First AI Agent'
]

PRODUCTION_NAMES = [
    'Error Catcher — Master',
    'Utopia-Deli-Simple-Checkout-v4',
    'Utopia Deli — Full Checkout',
    'Utopia Deli — Google Forms Intake',
    'Utopia Deli — HTML Webhook Checkout v2',
    'Utopia Deli — HTML Checkout v3 (Local API)',
    'Utopia Deli — Minimal Checkout',
    'Utopia Deli – Menu Form Only (Alt Schema)',
    'Order Received',
    'Utopia Deli – Full Order Flow (Sheets Config)',
    'Green Systems — Lead Scraper (Little Rock Restaurants)',
    'Green Systems — Service Business Lead Scraper',
    'Systack Lead Scraper — PostgreSQL CRM',
    'Green Systems — Outreach Sequencer',
    'SOL Morning Briefing',
    'Cart Renderer + Router',
    'Contact + Item + Cart',
    'Add Another Item',
    'Utopia Deli Online Order Unused Payment Link deletion',
    'Square Refund / Void Confirmation → ONLINE_ORDERS',
    'Deli Online Order Disable Square Payment Link on Payment Completed',
    'MOD 1 — Streetwear Daily (RSS Aggregator) v1',
]

def reconstruct_workflow(row):
    """Reconstruct full n8n workflow JSON from database columns."""
    workflow = {
        "id": row['id'],
        "name": row['name'],
        "active": bool(row['active']),
        "nodes": json.loads(row['nodes'] or '[]'),
        "connections": json.loads(row['connections'] or '{}'),
        "settings": json.loads(row['settings'] or '{}'),
        "staticData": json.loads(row['staticData'] or 'null') if row['staticData'] else None,
        "meta": json.loads(row['meta'] or '{}') if row['meta'] else {},
        "tags": [],
        "versionId": row['versionId'],
        "triggerCount": row['triggerCount'],
    }
    
    # Add pin data if present
    if row['pinData']:
        workflow['pinData'] = json.loads(row['pinData'])
    
    return workflow

def extract_workflows(pattern=None, specific_names=None):
    """Extract workflows from database."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if specific_names:
        placeholders = ','.join('?' * len(specific_names))
        query = f"SELECT * FROM workflow_entity WHERE name IN ({placeholders})"
        cursor.execute(query, specific_names)
    elif pattern:
        query = "SELECT * FROM workflow_entity WHERE name LIKE ?"
        cursor.execute(query, (pattern,))
    else:
        # Extract all non-test production workflows
        skip_conditions = ' AND '.join([f"name NOT LIKE '{p}'" for p in SKIP_PATTERNS])
        query = f"SELECT * FROM workflow_entity WHERE {skip_conditions}"
        cursor.execute(query)
    
    workflows = []
    for row in cursor.fetchall():
        workflow = reconstruct_workflow(row)
        workflows.append(workflow)
        
        # Save to file
        filename = f"{workflow['name'].replace(' ', '_').replace('/', '_')}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        print(f"✅ Extracted: {workflow['name']} ({len(workflow['nodes'])} nodes)")
    
    conn.close()
    
    # Save manifest
    manifest = {
        "extracted_at": datetime.now().isoformat(),
        "database": DB_PATH,
        "count": len(workflows),
        "workflows": [w['name'] for w in workflows]
    }
    
    with open(os.path.join(OUTPUT_DIR, '_manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n📦 Extracted {len(workflows)} workflows to: {OUTPUT_DIR}")
    return workflows

if __name__ == '__main__':
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print(f"🔍 Extracting workflows matching: {pattern}")
        extract_workflows(pattern=pattern)
    else:
        print("🔍 Extracting all production workflows...")
        extract_workflows(specific_names=PRODUCTION_NAMES)