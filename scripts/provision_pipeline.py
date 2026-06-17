#!/usr/bin/env python3
"""
SAOS Complete Provisioning Pipeline
Orchestrates the full client deployment: VPS → Templates → Identity → Health Check → Email.

Usage:
    python3 provision_pipeline.py --client-id 123 --tier business --email "client@example.com"
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import Optional

# Import our provisioning modules
sys.path.insert(0, os.path.dirname(__file__))
from provision_vps import VultrProvisioner, TIER_PLANS
from deploy_templates import TemplateDeployer
from health_check import HealthChecker
from send_client_email import generate_welcome_email, send_email_smtp, save_email_to_file


class SAOSProvisioner:
    """Complete SAOS provisioning orchestrator."""
    
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        self.results = {
            "client_id": None,
            "tier": None,
            "email": None,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "status": "running",
            "steps": {},
            "errors": []
        }
    
    def log_step(self, step: str, status: str, details: dict = None):
        """Log a provisioning step."""
        self.results["steps"][step] = {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        print(f"\n{'='*60}")
        print(f"Step: {step} — {status}")
        if details:
            for k, v in details.items():
                print(f"  {k}: {v}")
        print(f"{'='*60}")
    
    def run_step(self, name: str, func, *args, **kwargs) -> Optional[dict]:
        """Run a provisioning step with error handling."""
        try:
            print(f"\n▶️  Running: {name}...")
            result = func(*args, **kwargs)
            self.log_step(name, "success", result)
            return result
        except Exception as e:
            error_msg = f"{name} failed: {str(e)}"
            self.results["errors"].append(error_msg)
            self.log_step(name, "failed", {"error": str(e)})
            print(f"❌ {error_msg}")
            return None
    
    def provision(self, client_id: str, tier: str, email: str, 
                  agent_name: str = None, client_name: str = None,
                  contact_name: str = None) -> dict:
        """Run complete provisioning pipeline."""
        
        self.results["client_id"] = client_id
        self.results["tier"] = tier
        self.results["email"] = email
        
        agent_name = agent_name or f"Agent-{client_id}"
        client_name = client_name or f"Client-{client_id}"
        contact_name = contact_name or "There"
        
        print(f"\n🚀 SAOS Provisioning Pipeline")
        print(f"   Client: {client_id}")
        print(f"   Tier: {tier}")
        print(f"   Email: {email}")
        print(f"   Agent: {agent_name}")
        print(f"   Test Mode: {'YES' if self.test_mode else 'NO'}")
        print(f"\n{'='*60}")
        
        # Step 1: Create VPS
        vps_result = self.run_step(
            "create_vps",
            self._create_vps,
            client_id, tier, agent_name
        )
        
        if not vps_result:
            self.results["status"] = "failed"
            return self.results
        
        vps_ip = vps_result.get("vps_ip", "PENDING")
        
        # Step 2: Wait for VPS ready (skip in test mode)
        if not self.test_mode:
            self.run_step("wait_for_vps", self._wait_for_vps, vps_result["vps_id"])
        
        # Step 3: Deploy templates
        templates_result = self.run_step(
            "deploy_templates",
            self._deploy_templates,
            client_id, tier, vps_ip
        )
        
        # Step 4: Generate identity files
        identity_result = self.run_step(
            "generate_identity",
            self._generate_identity,
            client_id, agent_name, client_name, email, tier
        )
        
        # Step 5: Health check
        health_result = self.run_step(
            "health_check",
            self._health_check,
            vps_ip, client_id
        )
        
        # Step 6: Send welcome email
        email_result = self.run_step(
            "send_email",
            self._send_welcome_email,
            client_id, email, client_name, contact_name, agent_name, tier, vps_ip
        )
        
        # Final status
        failed_steps = [k for k, v in self.results["steps"].items() if v["status"] == "failed"]
        self.results["status"] = "completed" if not failed_steps else "partial"
        self.results["completed_at"] = datetime.utcnow().isoformat()
        
        return self.results
    
    def _create_vps(self, client_id: str, tier: str, agent_name: str) -> dict:
        """Create Vultr VPS."""
        if self.test_mode:
            return {
                "vps_id": f"TEST-{client_id}",
                "vps_ip": "192.0.2.1",
                "status": "test",
                "message": "Test mode - no real VPS created"
            }
        
        provisioner = VultrProvisioner()
        instance = provisioner.create_instance(client_id, tier, agent_name, "PLACEHOLDER")
        
        # Wait for active
        instance = provisioner.wait_for_instance(instance["id"])
        
        return {
            "vps_id": instance["id"],
            "vps_ip": instance.get("main_ip", "PENDING"),
            "region": instance["region"],
            "plan": instance["plan"],
            "status": instance["status"]
        }
    
    def _wait_for_vps(self, vps_id: str) -> dict:
        """Wait for VPS to be ready."""
        if self.test_mode:
            return {"status": "test"}
        
        # Wait logic is in create_vps, but this is for additional checks
        return {"status": "ready", "vps_id": vps_id}
    
    def _deploy_templates(self, client_id: str, tier: str, vps_ip: str) -> dict:
        """Deploy n8n templates."""
        if self.test_mode:
            return {
                "templates": ["booking-system.json", "invoice-pipeline.json"],
                "status": "test"
            }
        
        deployer = TemplateDeployer(f"http://{vps_ip}:5678")
        results = deployer.deploy_for_client(client_id, tier)
        
        return {
            "templates_deployed": len([r for r in results if r["status"] == "activated"]),
            "templates_failed": len([r for r in results if r["status"] == "failed"]),
            "details": results
        }
    
    def _generate_identity(self, client_id: str, agent_name: str, client_name: str,
                          email: str, tier: str) -> dict:
        """Generate identity files for client agent."""
        
        # Use existing generate-identity.py
        script_path = os.path.join(os.path.dirname(__file__), "generate-identity.py")
        
        if not os.path.exists(script_path):
            return {"status": "skipped", "reason": "generate-identity.py not found"}
        
        cmd = [
            "python3", script_path,
            "--client-id", client_id,
            "--name", client_name,
            "--email", email,
            "--agent-name", agent_name
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _health_check(self, vps_ip: str, client_id: str) -> dict:
        """Run health checks."""
        if self.test_mode:
            return {
                "overall_status": "healthy",
                "checks": {"test_mode": True},
                "status": "test"
            }
        
        checker = HealthChecker(vps_ip, client_id)
        return checker.run_all_checks()
    
    def _send_welcome_email(self, client_id: str, email: str, client_name: str,
                           contact_name: str, agent_name: str, tier: str, vps_ip: str) -> dict:
        """Send welcome email."""
        
        client_data = {
            "client_id": client_id,
            "client_name": client_name,
            "contact_name": contact_name,
            "agent_name": agent_name,
            "tier": tier,
            "vps_ip": vps_ip,
            "tailscale_url": f"https://{agent_name.lower()}.tailnet-systack.ts.net",
            "deployed_at": datetime.now().strftime("%B %d, %Y")
        }
        
        html = generate_welcome_email(client_data)
        
        if self.test_mode:
            filename = save_email_to_file(client_data)
            return {
                "status": "test",
                "saved_to": filename,
                "message": "Test mode - email saved to file"
            }
        
        # Try to send via SMTP
        subject = f"🛰️ Your SAOS Fleet is Live — Welcome {contact_name}!"
        sent = send_email_smtp(email, subject, html)
        
        if not sent:
            # Fallback: save to file
            filename = save_email_to_file(client_data)
            return {
                "status": "saved_to_file",
                "saved_to": filename,
                "message": "SMTP failed - saved to file for manual sending"
            }
        
        return {"status": "sent", "to": email}


def print_summary(results: dict):
    """Print provisioning summary."""
    print(f"\n{'='*70}")
    print(f"SAOS PROVISIONING COMPLETE")
    print(f"{'='*70}")
    print(f"Client: {results['client_id']}")
    print(f"Tier: {results['tier']}")
    print(f"Status: {results['status'].upper()}")
    print(f"Started: {results['started_at']}")
    print(f"Completed: {results['completed_at']}")
    
    if results['errors']:
        print(f"\n⚠️  Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   ❌ {error}")
    
    print(f"\n📋 Steps:")
    for step_name, step_data in results['steps'].items():
        icon = "✅" if step_data['status'] == 'success' else "❌"
        print(f"   {icon} {step_name}: {step_data['status']}")
    
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="SAOS Complete Provisioning Pipeline")
    parser.add_argument("--client-id", required=True, help="SAOS client ID")
    parser.add_argument("--tier", default="business", choices=["business", "enterprise", "test"])
    parser.add_argument("--email", required=True, help="Client email")
    parser.add_argument("--agent-name", help="Agent name (default: auto-generated)")
    parser.add_argument("--client-name", help="Business name")
    parser.add_argument("--contact-name", help="Contact person name")
    parser.add_argument("--test-mode", action="store_true", help="Test mode - no real resources")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    # Run provisioning
    provisioner = SAOSProvisioner(test_mode=args.test_mode)
    results = provisioner.provision(
        client_id=args.client_id,
        tier=args.tier,
        email=args.email,
        agent_name=args.agent_name,
        client_name=args.client_name,
        contact_name=args.contact_name
    )
    
    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_summary(results)
    
    # Save results to file
    output_file = f"/tmp/saos-provision-{args.client_id}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {output_file}")
    
    # Exit code
    sys.exit(0 if results["status"] == "completed" else 1)


if __name__ == "__main__":
    main()
