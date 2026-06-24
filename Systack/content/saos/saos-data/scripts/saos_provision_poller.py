#!/usr/bin/env python3
"""
SAOS n8n Execution Poller
Polls n8n for webhook execution data and triggers provisioning.

Usage:
    python3 saos_provision_poller.py --interval 30
"""

import os
import sys
import json
import time
import argparse
import requests
from datetime import datetime, timedelta

LOG_FILE = os.path.expanduser("~/.openclaw/workspaces/sol/logs/saos_provision_poller.log")
STATE_FILE = os.path.expanduser("~/.openclaw/workspaces/sol/logs/saos_poller_state.json")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_check": None, "processed_ids": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_n8n_executions(workflow_id=None, since_minutes=5):
    """Fetch recent n8n executions."""
    
    # Try to get n8n API key
    n8n_key = os.environ.get("N8N_API_KEY")
    if not n8n_key:
        cred_path = os.path.expanduser("~/.openclaw/workspaces/sol/Sol-Knowledge/credentials/Green/n8n/n8n Openclaw api")
        if os.path.exists(cred_path):
            with open(cred_path, "r") as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
                n8n_key = lines[-1] if lines else None
    
    if not n8n_key:
        log("WARNING: No n8n API key found")
        return []
    
    try:
        headers = {"X-N8N-API-KEY": n8n_key}
        url = "https://n8n.systack.net/api/v1/executions"
        params = {"limit": 20}
        if workflow_id:
            params["workflowId"] = workflow_id
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
        else:
            log(f"n8n API error: {response.status_code} - {response.text[:200]}")
            return []
    except Exception as e:
        log(f"Error fetching executions: {e}")
        return []

def process_execution(execution):
    """Process a webhook execution and trigger provisioning."""
    
    exec_id = execution.get("id")
    workflow_id = execution.get("workflowId")
    status = execution.get("status")
    
    log(f"Processing execution {exec_id} (workflow: {workflow_id}, status: {status})")
    
    # Extract webhook data from execution
    data = execution.get("data", {})
    
    # The webhook data is usually in data.resultData.runData
    try:
        run_data = data.get("resultData", {}).get("runData", {})
        # Find webhook node output
        for node_name, node_runs in run_data.items():
            if "webhook" in node_name.lower():
                for run in node_runs:
                    node_data = run.get("data", {}).get("main", [[]])[0]
                    if node_data:
                        webhook_payload = node_data[0].get("json", {})
                        log(f"Found webhook payload: {json.dumps(webhook_payload, indent=2)[:500]}")
                        return trigger_provisioning(webhook_payload)
    except Exception as e:
        log(f"Error extracting webhook data: {e}")
    
    return False

def trigger_provisioning(payload):
    """Trigger the provisioning pipeline."""
    
    client_id = payload.get("client_id") or payload.get("stripe_customer_id")
    if not client_id:
        log("No client_id found in payload, skipping")
        return False
    
    tier = payload.get("tier", "business")
    email = payload.get("email") or payload.get("stripe_customer_email", "")
    
    log(f"Triggering provisioning for client {client_id}, tier {tier}, email {email}")
    
    # Call the bridge directly (or pipeline)
    bridge_script = os.path.join(os.path.dirname(__file__), "saos_webhook_bridge.py")
    if os.path.exists(bridge_script):
        import subprocess
        cmd = [sys.executable, bridge_script, "--port", "0"]  # Port 0 = don't start server, just process
        # Actually, better to call pipeline directly
        pass
    
    # Direct pipeline call
    pipeline_script = os.path.join(os.path.dirname(__file__), "provision_pipeline.py")
    if not os.path.exists(pipeline_script):
        log(f"ERROR: Pipeline not found: {pipeline_script}")
        return False
    
    import subprocess
    cmd = [
        sys.executable, pipeline_script,
        "--client-id", str(client_id),
        "--tier", tier,
        "--email", email,
        "--agent-name", payload.get("agent_name", "saos-agent"),
        "--client-name", payload.get("client_name", ""),
        "--contact-name", payload.get("contact_name", "")
    ]
    
    # Check for Vultr key
    if not os.environ.get("VULTR_API_KEY"):
        cred_path = os.path.expanduser("~/.openclaw/workspaces/sol/Sol-Knowledge/credentials/Green/Vultr/VULTR API")
        if not os.path.exists(cred_path):
            log("WARNING: No Vultr API key, using test mode")
            cmd.append("--test-mode")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        log(f"Pipeline started with PID {process.pid}")
        return True
    except Exception as e:
        log(f"ERROR: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="SAOS n8n Execution Poller")
    parser.add_argument("--interval", type=int, default=30, help="Poll interval in seconds")
    parser.add_argument("--workflow-id", help="Filter by workflow ID")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    
    state = load_state()
    log(f"Poller started (interval: {args.interval}s)")
    
    while True:
        try:
            executions = get_n8n_executions(args.workflow_id)
            log(f"Found {len(executions)} recent executions")
            
            for execution in executions:
                exec_id = execution.get("id")
                if exec_id in state["processed_ids"]:
                    continue
                
                log(f"New execution: {exec_id}")
                process_execution(execution)
                state["processed_ids"].append(exec_id)
                # Keep only last 100 IDs
                state["processed_ids"] = state["processed_ids"][-100:]
            
            state["last_check"] = datetime.now().isoformat()
            save_state(state)
            
        except Exception as e:
            log(f"Error in poll loop: {e}")
        
        if args.once:
            break
        
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
