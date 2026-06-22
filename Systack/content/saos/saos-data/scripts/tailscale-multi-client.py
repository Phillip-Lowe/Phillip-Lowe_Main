#!/usr/bin/env python3
"""
SAOS Multi-Client Tailscale Manager
Handles device tagging and access for unlimited clients without user seat limits.

Usage:
    python3 tailscale-multi-client.py --action setup --client-id 123
    python3 tailscale-multi-client.py --action list-devices
    python3 tailscale-multi-client.py --action get-url --client-id 123
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime

TAILSCALE_API_BASE = "https://api.tailscale.com/api/v2"

# Tailscale auth key types for clients
AUTH_KEY_TAGS = {
    "client_vps": "tag:saos-client",
    "infrastructure": "tag:systack-infra"
}


class TailscaleManager:
    """Manages Tailscale multi-client architecture using tags instead of users."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("TAILSCALE_API_KEY")
        if not self.api_key:
            raise ValueError("TAILSCALE_API_KEY required. Set env var or pass --api-key.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Get tailnet name from API key
        self.tailnet = self._get_tailnet()
    
    def _api(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make Tailscale API call."""
        url = f"{TAILSCALE_API_BASE}{endpoint}"
        response = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
        
        if response.status_code >= 400:
            print(f"API Error: {response.status_code} - {response.text[:500]}")
            response.raise_for_status()
        
        return response.json() if response.text else {}
    
    def _get_tailnet(self) -> str:
        """Get tailnet name from API key."""
        try:
            result = self._api("GET", "/tailnet")
            return result.get("name", "unknown")
        except:
            # Fallback: try common tailnet names
            return "systack.net"  # adjust based on your setup
    
    def create_auth_key(self, tag: str, reusable: bool = True, 
                       ephemeral: bool = False, expiry_hours: int = 168) -> str:
        """Create reusable auth key for client VPS."""
        
        payload = {
            "capabilities": {
                "devices": {
                    "create": {
                        "reusable": reusable,
                        "ephemeral": ephemeral,
                        "preauthorized": True,
                        "tags": [tag]
                    }
                }
            },
            "expirySeconds": expiry_hours * 3600
        }
        
        result = self._api("POST", f"/tailnet/{self.tailnet}/keys", json=payload)
        return result.get("key", "")
    
    def list_devices(self, tag: str = None) -> list:
        """List devices, optionally filtered by tag."""
        result = self._api("GET", f"/tailnet/{self.tailnet}/devices")
        devices = result.get("devices", [])
        
        if tag:
            devices = [d for d in devices if tag in d.get("tags", [])]
        
        return devices
    
    def get_device_url(self, device_id: str, port: int = 443) -> str:
        """Get MagicDNS URL for device."""
        result = self._api("GET", f"/device/{device_id}")
        hostname = result.get("name", "")
        
        if hostname:
            return f"https://{hostname}:{port}"
        return ""
    
    def setup_client_access(self, client_id: str, agent_name: str) -> dict:
        """Setup access for a new client without creating user seat."""
        
        # Create auth key for client VPS
        auth_key = self.create_auth_key("tag:saos-client")
        
        # Generate expected MagicDNS name
        dns_name = f"saos-{client_id}.{self.tailnet}"
        
        return {
            "client_id": client_id,
            "agent_name": agent_name,
            "auth_key": auth_key,
            "dns_name": dns_name,
            "access_url": f"https://{dns_name}",
            "setup_date": datetime.utcnow().isoformat(),
            "note": "Client does NOT need Tailscale user account. Access via HTTPS URL."
        }
    
    def get_client_status(self, client_id: str) -> dict:
        """Check if client VPS is online."""
        devices = self.list_devices(tag="tag:saos-client")
        
        for device in devices:
            if device.get("name", "").startswith(f"saos-{client_id}"):
                return {
                    "client_id": client_id,
                    "online": device.get("connected", False),
                    "last_seen": device.get("lastSeen", ""),
                    "ip": device.get("addresses", [""])[0] if device.get("addresses") else "",
                    "url": f"https://{device.get('name', '')}"
                }
        
        return {"client_id": client_id, "online": False, "error": "Device not found"}


def print_multi_client_summary():
    """Print summary of multi-client architecture."""
    print("""
🌐 SAOS Multi-Client Tailscale Architecture
═════════════════════════════════════════════

USER SEAT STRATEGY (Free tier = 6 users):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ You (admin) = 1 user seat
  ✅ Systack team = 1-2 user seats
  ❌ Clients = 0 user seats (use TAGS instead)

DEVICE LIMITS:
━━━━━━━━━━━━━━━━━━
  ✅ Tagged devices: UNLIMITED
  ✅ User devices per user: UNLIMITED
  ✅ Ephemeral resources: 1,000 min/month (free)

ACCESS METHODS FOR CLIENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Method 1: HTTPS URL (Recommended)
    • Tailscale Serve / Funnel
    • Client gets: https://saos-123.tailnet.ts.net
    • No Tailscale app needed on client device
    • Works in any browser

  Method 2: Tailscale SSH (Optional)
    • For clients who need server access
    • Requires Tailscale app installed
    • Counts as user device (NOT user seat)

  Method 3: MagicDNS (Internal)
    • http://saos-123 inside tailnet
    • Only from devices already on tailnet

COST PROJECTION:
━━━━━━━━━━━━━━━━━━
  ┌─────────────────────────────────────────┐
  │ Clients │ User Seats │ Tailscale Cost   │
  ├─────────────────────────────────────────┤
  │    5    │     1      │ FREE (6 max)     │
  │   10    │     1      │ FREE (6 max)     │
  │   20    │     1      │ FREE (6 max)     │
  │   50    │     1      │ FREE (6 max)     │
  │  100    │     1      │ FREE (6 max)     │
  └─────────────────────────────────────────┘

  💡 KEY INSIGHT: Tagged devices don't count toward user limit!
     You can have 100 clients on free tier as long as they're tagged.

RECOMMENDED SETUP:
━━━━━━━━━━━━━━━━━━━
  1. Create auth keys with tag:saos-client
  2. Client VPS joins with auth key (auto-tagged)
  3. Enable Tailscale Serve on VPS (public HTTPS)
  4. Give client the URL: https://saos-123.tailnet.ts.net
  5. Client accesses dashboard without any Tailscale account
""")


def main():
    parser = argparse.ArgumentParser(description="SAOS Tailscale Multi-Client Manager")
    parser.add_argument("--action", required=True, 
                       choices=["setup", "list-devices", "get-url", "status", "summary"])
    parser.add_argument("--client-id")
    parser.add_argument("--agent-name", default="SAOS-Agent")
    parser.add_argument("--api-key")
    parser.add_argument("--tag", default="tag:saos-client")
    
    args = parser.parse_args()
    
    if args.action == "summary":
        print_multi_client_summary()
        return
    
    manager = TailscaleManager(api_key=args.api_key)
    
    if args.action == "setup":
        if not args.client_id:
            print("❌ --client-id required for setup")
            sys.exit(1)
        
        result = manager.setup_client_access(args.client_id, args.agent_name)
        print(json.dumps(result, indent=2))
    
    elif args.action == "list-devices":
        devices = manager.list_devices(args.tag)
        print(f"\n📱 Devices with tag '{args.tag}':\n")
        for device in devices:
            print(f"  {'🟢' if device.get('connected') else '🔴'} {device.get('name', 'unknown')}")
            print(f"     IP: {device.get('addresses', ['N/A'])[0]}")
            print(f"     Last seen: {device.get('lastSeen', 'never')}")
        
        print(f"\nTotal: {len(devices)} devices")
    
    elif args.action == "get-url":
        if not args.client_id:
            print("❌ --client-id required")
            sys.exit(1)
        
        # Find device by client ID
        devices = manager.list_devices("tag:saos-client")
        for device in devices:
            if device.get("name", "").startswith(f"saos-{args.client_id}"):
                url = manager.get_device_url(device.get("id"))
                print(f"Client {args.client_id} URL: {url}")
                return
        
        print(f"❌ Device for client {args.client_id} not found")
    
    elif args.action == "status":
        if not args.client_id:
            print("❌ --client-id required")
            sys.exit(1)
        
        status = manager.get_client_status(args.client_id)
        print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
