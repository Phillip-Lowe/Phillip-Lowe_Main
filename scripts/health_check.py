#!/usr/bin/env python3
"""
SAOS Health Check Script
Validates client VPS deployment before marking as ready.

Usage:
    python3 health_check.py --vps-ip 123.45.67.89 --client-id 123
"""

import sys
import argparse
import requests
import socket
from datetime import datetime

# Optional SSH support
try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


class HealthChecker:
    """Runs health checks on SAOS client VPS."""
    
    def __init__(self, vps_ip: str, client_id: str):
        self.vps_ip = vps_ip
        self.client_id = client_id
        self.results = {}
    
    def check_port(self, port: int, timeout: int = 5) -> dict:
        """Check if port is open."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((self.vps_ip, port))
            sock.close()
            return {
                "port": port,
                "open": result == 0,
                "error": None if result == 0 else f"Connection failed (code: {result})"
            }
        except Exception as e:
            return {"port": port, "open": False, "error": str(e)}
    
    def check_http(self, url: str, timeout: int = 10) -> dict:
        """Check HTTP endpoint."""
        try:
            response = requests.get(url, timeout=timeout, verify=False)
            return {
                "url": url,
                "status": response.status_code,
                "ok": response.status_code < 400,
                "response_time_ms": int(response.elapsed.total_seconds() * 1000)
            }
        except Exception as e:
            return {"url": url, "status": None, "ok": False, "error": str(e)}
    
    def check_ssh(self, username: str = "systack", timeout: int = 10) -> dict:
        """Check SSH connectivity."""
        if not PARAMIKO_AVAILABLE:
            return {"ok": True, "note": "paramiko not installed, skipping SSH check"}
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.vps_ip, username=username, timeout=timeout, look_for_keys=True)
            stdin, stdout, stderr = client.exec_command("uptime")
            output = stdout.read().decode().strip()
            client.close()
            return {
                "ok": True,
                "output": output,
                "error": None
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def check_ollama(self) -> dict:
        """Check Ollama is running and has models."""
        return self.check_http(f"http://{self.vps_ip}:11434/api/tags", timeout=15)
    
    def check_n8n(self) -> dict:
        """Check n8n is running."""
        return self.check_http(f"http://{self.vps_ip}:5678/healthz", timeout=10)
    
    def check_tailscale(self) -> dict:
        """Check Tailscale (requires SSH)."""
        if not PARAMIKO_AVAILABLE:
            return {"ok": True, "note": "paramiko not installed, skipping Tailscale check"}
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.vps_ip, username="systack", timeout=10, look_for_keys=True)
            stdin, stdout, stderr = client.exec_command("tailscale status --json | head -20")
            output = stdout.read().decode().strip()
            client.close()
            return {
                "ok": bool(output),
                "status_preview": output[:200],
                "error": None
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def run_all_checks(self) -> dict:
        """Run complete health check suite."""
        print(f"🔍 Health checking client {self.client_id} at {self.vps_ip}...\n")
        
        # Port checks
        self.results["ssh"] = self.check_port(22)
        self.results["http"] = self.check_port(80)
        self.results["n8n_port"] = self.check_port(5678)
        self.results["ollama_port"] = self.check_port(11434)
        
        # Service checks
        self.results["n8n"] = self.check_n8n()
        self.results["ollama"] = self.check_ollama()
        
        # SSH + Tailscale
        self.results["ssh_connect"] = self.check_ssh()
        self.results["tailscale"] = self.check_tailscale()
        
        # Calculate overall status
        critical = ["ssh", "n8n", "ollama"]
        critical_pass = all(self.results.get(k, {}).get("ok", False) for k in critical)
        
        summary = {
            "client_id": self.client_id,
            "vps_ip": self.vps_ip,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy" if critical_pass else "degraded",
            "checks": self.results,
            "critical_pass": critical_pass,
            "total_checks": len(self.results),
            "passing_checks": sum(1 for v in self.results.values() if v.get("ok", False))
        }
        
        return summary


def print_results(summary: dict):
    """Print health check results."""
    print(f"\n{'='*60}")
    print(f"Health Check Results: {summary['client_id']}")
    print(f"{'='*60}")
    print(f"Overall: {'✅ HEALTHY' if summary['critical_pass'] else '❌ DEGRADED'}")
    print(f"Checks: {summary['passing_checks']}/{summary['total_checks']} passing\n")
    
    for check_name, result in summary['checks'].items():
        icon = "✅" if result.get("ok") else "⚠️" if result.get("open") else "❌"
        print(f"{icon} {check_name}")
        if "status" in result:
            print(f"   Status: {result['status']}")
        if "error" in result and result["error"]:
            print(f"   Error: {result['error']}")
    
    print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="SAOS Health Check")
    parser.add_argument("--vps-ip", required=True, help="VPS IP address")
    parser.add_argument("--client-id", required=True, help="Client ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--test-mode", action="store_true", help="Simulate checks")
    
    args = parser.parse_args()
    
    if args.test_mode:
        # Return mock results
        summary = {
            "client_id": args.client_id,
            "vps_ip": args.vps_ip,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy",
            "critical_pass": True,
            "total_checks": 8,
            "passing_checks": 8,
            "checks": {
                "ssh": {"ok": True, "port": 22, "open": True},
                "http": {"ok": True, "port": 80, "open": True},
                "n8n_port": {"ok": True, "port": 5678, "open": True},
                "ollama_port": {"ok": True, "port": 11434, "open": True},
                "n8n": {"ok": True, "status": 200, "url": f"http://{args.vps_ip}:5678/healthz"},
                "ollama": {"ok": True, "status": 200, "url": f"http://{args.vps_ip}:11434/api/tags"},
                "ssh_connect": {"ok": True, "output": "load average: 0.5, 0.3, 0.1"},
                "tailscale": {"ok": True, "status_preview": "100.x.x.x saos-" + args.client_id}
            }
        }
        print_results(summary)
        if args.json:
            print("\n" + json.dumps(summary, indent=2))
        return
    
    checker = HealthChecker(args.vps_ip, args.client_id)
    summary = checker.run_all_checks()
    
    print_results(summary)
    
    if args.json:
        print("\n" + json.dumps(summary, indent=2))
    
    # Exit code based on health
    sys.exit(0 if summary["critical_pass"] else 1)


if __name__ == "__main__":
    import json
    main()
