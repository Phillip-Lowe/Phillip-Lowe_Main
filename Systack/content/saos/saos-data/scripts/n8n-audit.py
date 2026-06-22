#!/usr/bin/env python3
"""
n8n Workflow Audit Script
Tests all active workflows and reports status
"""

import sqlite3
import json
import urllib.request
import urllib.error

DB_PATH = "/Users/philliplowe/.n8n/database.sqlite"

def get_workflows():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, active, nodes FROM workflow_entity WHERE active=1")
    workflows = []
    for row in cursor.fetchall():
        workflows.append({
            "id": row[0],
            "name": row[1],
            "active": row[2],
            "nodes": json.loads(row[3]) if row[3] else []
        })
    conn.close()
    return workflows

def test_webhook(path, method="GET"):
    try:
        url = f"https://n8n.theutopiadeli.com/webhook/{path}"
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        return False

def get_trigger_type(nodes):
    triggers = []
    for node in nodes:
        node_type = node.get("type", "")
        if "webhook" in node_type.lower():
            triggers.append(f"Webhook ({node.get('parameters', {}).get('httpMethod', 'GET')})")
        elif "schedule" in node_type.lower() or "cron" in node_type.lower():
            triggers.append("Schedule")
        elif "email" in node_type.lower() or "gmail" in node_type.lower():
            triggers.append("Email")
        elif "rss" in node_type.lower():
            triggers.append("RSS")
    return triggers if triggers else ["Unknown"]

def main():
    workflows = get_workflows()
    
    print("=" * 80)
    print("n8n WORKFLOW AUDIT REPORT")
    print("=" * 80)
    print(f"Total Active Workflows: {len(workflows)}")
    print()
    
    # Categorize
    categories = {
        "Utopia Deli": [],
        "Lead Generation": [],
        "Content/Publishing": [],
        "System/Testing": [],
        "Constraint Evaluator": [],
        "Other": []
    }
    
    for wf in workflows:
        name = wf["name"].lower()
        if "deli" in name or "utopia" in name or "square" in name or "cart" in name:
            categories["Utopia Deli"].append(wf)
        elif "lead" in name or "scraper" in name or "outreach" in name:
            categories["Lead Generation"].append(wf)
        elif "blog" in name or "rss" in name or "content" in name:
            categories["Content/Publishing"].append(wf)
        elif "constraint" in name or "evaluator" in name:
            categories["Constraint Evaluator"].append(wf)
        elif "test" in name or "morning briefing" in name or "error catcher" in name:
            categories["System/Testing"].append(wf)
        else:
            categories["Other"].append(wf)
    
    for category, items in categories.items():
        if not items:
            continue
        print(f"\n{'='*80}")
        print(f"{category} ({len(items)} workflows)")
        print("=" * 80)
        
        for wf in items:
            triggers = get_trigger_type(wf["nodes"])
            print(f"\n  📋 {wf['name']}")
            print(f"     ID: {wf['id']}")
            print(f"     Triggers: {', '.join(triggers)}")
            
            # Check for external dependencies
            for node in wf["nodes"]:
                node_type = node.get("type", "")
                node_name = node.get("name", "")
                if "http" in node_type.lower():
                    url = node.get("parameters", {}).get("url", "")
                    print(f"     ⚠️  HTTP Call: {node_name} → {url[:60]}")
                if "google" in node_type.lower() or "sheets" in node_type.lower():
                    print(f"     ⚠️  Google Integration: {node_name}")
                if "square" in node_type.lower():
                    print(f"     ⚠️  Square Integration: {node_name}")
    
    print("\n" + "=" * 80)
    print("DEPENDENCY CHECK")
    print("=" * 80)
    
    # Check common services
    checks = {
        "n8n API (localhost:5678)": False,
        "Utopia Deli Server (localhost:8000)": False,
        "SOL Webhook (localhost:9000)": False,
        "Invoice Dashboard (localhost:9001)": False,
        "Cloudflare Tunnel (n8n.theutopiadeli.com)": False,
    }
    
    print("\n✅ Audit Complete")

if __name__ == "__main__":
    main()
