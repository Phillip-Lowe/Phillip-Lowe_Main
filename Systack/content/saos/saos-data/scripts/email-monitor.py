#!/usr/bin/env python3
"""
email-monitor.py — SOL Email Monitoring (IMAP via App Passwords)

Monitors multiple Gmail/Google Workspace inboxes for unread messages.
Reads app passwords securely from macOS Keychain.

Accounts:
- sol.liaison@gmail.com (Gmail)
- sol.liaison@systack.net (Google Workspace)
- support@systack.net (Google Workspace - shared)

Usage:
    python3 email-monitor.py --account sol.liaison@gmail.com
    python3 email-monitor.py --all
    python3 email-monitor.py --all --json

Security:
- App passwords stored in macOS Keychain (never hardcoded)
- No password logging or display
"""

import argparse
import imaplib
import email
import json
import subprocess
import sys
from datetime import datetime
from email.header import decode_header

ACCOUNTS = {
    "sol.liaison@gmail.com": {
        "imap_server": "imap.gmail.com",
        "label": "SOL Primary"
    },
    "sol.liaison@systack.net": {
        "imap_server": "imap.gmail.com",
        "label": "SOL Systack Business"
    },
    "support@systack.net": {
        "imap_server": "imap.gmail.com",
        "label": "Systack Support (Shared)"
    }
}

def get_password_from_keychain(account):
    """Retrieve app password from macOS Keychain securely."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "sol-email-credentials", "-a", account, "-w"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def decode_mime_header(header_value):
    """Decode MIME-encoded email headers."""
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            except:
                result.append(part.decode('utf-8', errors='replace'))
        else:
            result.append(part)
    return "".join(result)

def check_inbox(account):
    """Check unread emails for a single account via IMAP."""
    config = ACCOUNTS[account]
    password = get_password_from_keychain(account)
    
    if not password:
        return {
            "account": account,
            "label": config["label"],
            "error": "App password not found in Keychain",
            "unread_count": -1,
            "preview": []
        }
    
    try:
        mail = imaplib.IMAP4_SSL(config["imap_server"])
        mail.login(account, password)
        mail.select("inbox")
        
        status, messages = mail.search(None, "UNSEEN")
        unread_ids = messages[0].split()
        unread_count = len(unread_ids)
        
        emails = []
        for num in unread_ids[:5]:
            status, msg_data = mail.fetch(num, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            subject = decode_mime_header(msg.get("Subject", "")) or "(No Subject)"
            sender = decode_mime_header(msg.get("From", ""))
            date = msg.get("Date", "")
            
            emails.append({
                "subject": subject,
                "from": sender,
                "date": date
            })
        
        mail.logout()
        
        return {
            "account": account,
            "label": config["label"],
            "unread_count": unread_count,
            "preview": emails
        }
        
    except Exception as e:
        return {
            "account": account,
            "label": config["label"],
            "error": str(e),
            "unread_count": -1,
            "preview": []
        }

def main():
    parser = argparse.ArgumentParser(description="SOL Email Monitor")
    parser.add_argument("--account", choices=list(ACCOUNTS.keys()), help="Check specific account")
    parser.add_argument("--all", action="store_true", help="Check all accounts")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    accounts_to_check = list(ACCOUNTS.keys()) if args.all else [args.account] if args.account else []
    
    if not accounts_to_check:
        parser.print_help()
        sys.exit(1)
    
    results = []
    for account in accounts_to_check:
        result = check_inbox(account)
        results.append(result)
    
    if args.json:
        print(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "accounts": results
        }, indent=2))
    else:
        print(f"📧 SOL Email Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        for r in results:
            label = r["label"]
            account = r["account"]
            if "error" in r:
                print(f"\n⚠️  {label} ({account})")
                print(f"    ERROR: {r['error']}")
            else:
                count = r["unread_count"]
                emoji = "🔴" if count > 0 else "🟢"
                print(f"\n{emoji} {label} ({account})")
                print(f"    Unread: {count}")
                if r["preview"]:
                    print(f"    Latest:")
                    for e in r["preview"]:
                        sender = e['from'].split('<')[0].strip()[:30]
                        subject = e['subject'][:50]
                        print(f"      • [{sender}] {subject}")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
