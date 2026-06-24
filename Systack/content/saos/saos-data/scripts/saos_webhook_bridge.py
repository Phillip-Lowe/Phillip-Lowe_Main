#!/usr/bin/env python3
"""
SAOS Webhook Bridge
Receives n8n webhook calls and triggers the provisioning pipeline.

Usage:
    python3 saos_webhook_bridge.py --port 8767
    
Expected webhook payload:
    {
        "client_id": "123",
        "tier": "business",
        "email": "client@example.com",
        "agent_name": "Percy",
        "client_name": "Acme Corp",
        "contact_name": "Jane Doe"
    }
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = os.path.expanduser("~/.openclaw/workspaces/sol/logs/saos_webhook_bridge.log")

def log(msg):
    """Write to log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming webhook requests."""
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        log(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Handle GET - health check."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "service": "saos-webhook-bridge"}).encode())
    
    def do_POST(self):
        """Handle webhook payload."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        log(f"Received webhook: {body[:500]}")
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            # Try parsing as form data
            try:
                from urllib.parse import parse_qs
                parsed = parse_qs(body)
                data = {k: v[0] for k, v in parsed.items()}
            except Exception:
                data = {"raw_body": body}
        
        # Extract fields
        client_id = data.get("client_id") or data.get("stripe_customer_id", "unknown")
        tier = data.get("tier", "business")
        email = data.get("email") or data.get("stripe_customer_email", "")
        agent_name = data.get("agent_name", "saos-agent")
        client_name = data.get("client_name", "")
        contact_name = data.get("contact_name", "")
        
        log(f"Parsed: client_id={client_id}, tier={tier}, email={email}")
        
        # Trigger provisioning pipeline
        pipeline_script = os.path.join(os.path.dirname(__file__), "provision_pipeline.py")
        
        if not os.path.exists(pipeline_script):
            log(f"ERROR: Pipeline script not found: {pipeline_script}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Pipeline not found"}).encode())
            return
        
        # Run pipeline in background
        cmd = [
            sys.executable, pipeline_script,
            "--client-id", str(client_id),
            "--tier", tier,
            "--email", email,
            "--agent-name", agent_name,
            "--client-name", client_name,
            "--contact-name", contact_name
        ]
        
        # Add test flag if no Vultr key (to avoid real provisioning)
        if not os.environ.get("VULTR_API_KEY"):
            # Check credential file
            cred_path = os.path.expanduser("~/.openclaw/workspaces/sol/Sol-Knowledge/credentials/Green/Vultr/VULTR API")
            if not os.path.exists(cred_path):
                log("WARNING: No Vultr API key found, using test mode")
                cmd.append("--test-mode")
        
        log(f"Running: {' '.join(cmd)}")
        
        try:
            # Run asynchronously so webhook responds immediately
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            log(f"Pipeline started with PID {process.pid}")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "accepted",
                "client_id": client_id,
                "tier": tier,
                "pipeline_pid": process.pid,
                "message": "Provisioning started"
            }).encode())
            
        except Exception as e:
            log(f"ERROR starting pipeline: {e}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode())


def run_server(port=8767):
    """Start webhook bridge server."""
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    log(f"SAOS Webhook Bridge started on port {port}")
    log(f"Log file: {LOG_FILE}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAOS Webhook Bridge")
    parser.add_argument("--port", type=int, default=8767, help="Port to listen on")
    args = parser.parse_args()
    
    run_server(args.port)
