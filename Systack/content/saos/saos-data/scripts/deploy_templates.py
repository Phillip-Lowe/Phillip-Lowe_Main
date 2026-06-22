#!/usr/bin/env python3
"""
SAOS Template Deployment Script
Imports and activates n8n workflows for SAOS client based on tier.

Usage:
    python3 deploy_templates.py --client-id 123 --tier business --n8n-url http://localhost:5678
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

# Template paths by tier
TEMPLATE_DIRS = {
    "business": "templates/private",
    "enterprise": "templates/accelerate",
    "test": "templates/private"
}

# Required workflows for each tier
REQUIRED_WORKFLOWS = {
    "business": [
        "booking-system.json",
        "invoice-pipeline.json",
        "onboarding-sequence.json",
        "error-monitor.json"
    ],
    "enterprise": [
        "booking-system.json",
        "invoice-pipeline.json",
        "onboarding-sequence.json",
        "error-monitor.json",
        "slack-integration.json",
        "google-drive-sync.json",
        "calendar-integration.json"
    ],
    "test": [
        "booking-system.json",
        "error-monitor.json"
    ]
}


class TemplateDeployer:
    """Deploys n8n templates to client instance."""
    
    def __init__(self, n8n_url: str, n8n_api_key: str = None):
        self.n8n_url = n8n_url.rstrip('/')
        if n8n_api_key:
            self.api_key = n8n_api_key
        else:
            from provision_vps import load_credentials
            creds = load_credentials()
            self.api_key = creds.get('n8n') or os.environ.get("N8N_API_KEY")
        self.headers = {}
        if self.api_key:
            self.headers["X-N8N-API-KEY"] = self.api_key
    
    def import_workflow(self, workflow_path: str, client_id: str) -> dict:
        """Import a single workflow into n8n."""
        with open(workflow_path, 'r') as f:
            workflow = json.load(f)
        
        # Customize workflow for client
        workflow['name'] = f"{workflow['name']} - Client {client_id}"
        workflow['settings'] = {
            "saveManualExecutions": True,
            "callerPolicy": "workflowsFromSameOwner"
        }
        
        # Post to n8n
        url = f"{self.n8n_url}/rest/workflows"
        response = requests.post(url, headers=self.headers, json=workflow, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow."""
        url = f"{self.n8n_url}/rest/workflows/{workflow_id}/activate"
        response = requests.post(url, headers=self.headers, timeout=30)
        return response.status_code == 200
    
    def deploy_for_client(self, client_id: str, tier: str) -> list:
        """Deploy all templates for a client."""
        template_dir = TEMPLATE_DIRS.get(tier, "templates/private")
        workflows = REQUIRED_WORKFLOWS.get(tier, [])
        
        results = []
        for workflow_file in workflows:
            path = Path(template_dir) / workflow_file
            if not path.exists():
                print(f"⚠️  Template not found: {path}")
                continue
            
            try:
                imported = self.import_workflow(str(path), client_id)
                workflow_id = imported.get('id')
                
                if workflow_id:
                    self.activate_workflow(workflow_id)
                    results.append({
                        'file': workflow_file,
                        'id': workflow_id,
                        'status': 'activated'
                    })
                    print(f"✅ {workflow_file} -> {workflow_id}")
                
            except Exception as e:
                print(f"❌ Failed to import {workflow_file}: {e}")
                results.append({
                    'file': workflow_file,
                    'error': str(e),
                    'status': 'failed'
                })
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Deploy SAOS templates")
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--tier", default="business", choices=["business", "enterprise", "test"])
    parser.add_argument("--n8n-url", default="http://localhost:5678")
    parser.add_argument("--n8n-api-key", default=os.environ.get("N8N_API_KEY"))
    parser.add_argument("--test-mode", action="store_true")
    
    args = parser.parse_args()
    
    if args.test_mode:
        print(f"🧪 TEST MODE: Would deploy {args.tier} templates for client {args.client_id}")
        print(f"   Templates: {REQUIRED_WORKFLOWS[args.tier]}")
        print(f"   n8n URL: {args.n8n_url}")
        return
    
    deployer = TemplateDeployer(args.n8n_url, args.n8n_api_key)
    results = deployer.deploy_for_client(args.client_id, args.tier)
    
    print(f"\n📋 Deployment Summary:")
    success = sum(1 for r in results if r['status'] == 'activated')
    print(f"   Success: {success}/{len(results)}")
    
    for r in results:
        icon = "✅" if r['status'] == 'activated' else "❌"
        print(f"   {icon} {r['file']}: {r.get('id', r.get('error'))}")


if __name__ == "__main__":
    main()
