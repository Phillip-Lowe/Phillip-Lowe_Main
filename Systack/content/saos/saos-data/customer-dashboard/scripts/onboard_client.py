#!/usr/bin/env python3
"""
SAOS Client Onboarding Script
Automates first-time client setup: creates client record, generates temp PIN,
sets up default conversations, assigns agent fleet, sends welcome notification.

Usage:
    python3 scripts/onboard_client.py --name "Client Name" --email "client@email.com" --tier business
    python3 scripts/onboard_client.py --name "Client Name" --email "client@email.com" --tier enterprise --role customer
"""

import psycopg2
import os
import sys
import json
import random
import string
import argparse
from datetime import datetime, timedelta

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")

def get_db():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER)

def generate_pin(length=6):
    return ''.join(random.choices(string.digits, k=length))

def onboard_client(name, email, tier='business', role='customer', stripe_sub_id=None):
    """Onboard a new SAOS client end-to-end."""
    print(f"\n{'='*60}")
    print(f"SAOS Client Onboarding")
    print(f"{'='*60}")
    print(f"Name:  {name}")
    print(f"Email: {email}")
    print(f"Tier:  {tier}")
    print(f"Role:  {role}")
    print(f"{'='*60}\n")
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Step 1: Create client record
        print("[1/6] Creating client record...")
        temp_pin = generate_pin(6)
        temp_pin_expires = datetime.now() + timedelta(hours=24)
        
        cur.execute("""
            INSERT INTO saos_clients 
            (customer_name, customer_email, tier, role, onboarding_status, 
             temp_pin, temp_pin_expires_at, vps_status, created_at)
            VALUES (%s, %s, %s, %s, 'pending', %s, %s, 'pending', NOW())
            RETURNING id
        """, (name, email, tier, role, temp_pin, temp_pin_expires))
        
        client_id = cur.fetchone()[0]
        print(f"  ✅ Client ID: {client_id}")
        
        # Step 2: Create welcome conversation
        print("[2/6] Creating welcome conversation...")
        cur.execute("""
            INSERT INTO chat_conversations (client_id, title, status)
            VALUES (%s, 'Welcome to SAOS', 'active')
            RETURNING id
        """, (client_id,))
        
        conv_id = cur.fetchone()[0]
        print(f"  ✅ Conversation ID: {conv_id}")
        
        # Welcome message from SOL
        mfa_notice = ""
        if tier == 'enterprise':
            mfa_notice = """

🔐 IMPORTANT: Your Enterprise account requires Multi-Factor Authentication (MFA).
After setting your PIN, you'll be prompted to set up MFA before your first login.
This keeps your account secure."""
        
        welcome_msg = f"""👋 Welcome to SAOS, {name}!

I'm SOL, your System Operations Liaison. I'll be your primary point of contact.

Here's what happens next:
1. Set your permanent PIN using the temporary PIN I've generated for you
2. Explore your dashboard — you'll see your agent fleet, services, and usage
3. Request any service setup from the Services tab
4. Chat with me anytime — I'm always here

Your temporary PIN is: {temp_pin}
It expires in 24 hours. Set your permanent PIN at the login screen.{mfa_notice}

Your tier: {tier}
Your agent fleet: depends on your tier

Let's get started! 🚀"""
        
        cur.execute("""
            INSERT INTO chat_messages (conversation_id, sender_type, sender_name, sender_agent, content, message_type)
            VALUES (%s, 'agent', 'SOL', 'SOL', %s, 'text')
        """, (conv_id, welcome_msg))
        print(f"  ✅ Welcome message sent")
        
        # Step 3: Create default service setup tasks based on tier
        print("[3/6] Creating service setup tasks...")
        
        TIER_SERVICES = {
            'business': [
                'Invoice Processing Pipeline',
                'Lead Qualification System', 
                'Customer Support Drafting',
                'Document Classification Engine',
                'Scheduled Report Generator',
            ],
            'enterprise': [
                'Invoice Processing Pipeline',
                'Lead Qualification System',
                'Customer Support Drafting',
                'Document Classification Engine',
                'Scheduled Report Generator',
            ],
            'private': [
                'Private Document Extraction Pipeline',
                'Automated Invoice Processing System',
                'Self-Hosted Customer Support Automations',
            ],
            'accelerate': [
                'Automated Invoice Processing System',
                'Self-Hosted Customer Support Automations',
                'Local Data Entry Elimination System',
            ],
        }
        
        SERVICE_AGENT_MAP = {
            'Invoice Processing Pipeline': 'ASSEMBLY',
            'Lead Qualification System': 'ASSEMBLY',
            'Customer Support Drafting': 'CHATTY',
            'Document Classification Engine': 'ASSEMBLY',
            'Scheduled Report Generator': 'ASSEMBLY',
            'Private Document Extraction Pipeline': 'ASSEMBLY',
            'Automated Invoice Processing System': 'ASSEMBLY',
            'Self-Hosted Customer Support Automations': 'CHATTY',
            'Local Data Entry Elimination System': 'ASSEMBLY',
        }
        
        services = TIER_SERVICES.get(tier, TIER_SERVICES['business'])
        
        for svc in services:
            agent = SERVICE_AGENT_MAP.get(svc, 'SOL')
            cur.execute("""
                INSERT INTO task_queue 
                (task_type, display_name, description, payload_json, priority, status, assigned_agent)
                VALUES ('service_setup', %s, %s, %s, 3, 'PENDING', %s)
            """, (
                f'Setup: {svc}',
                f'Initial setup for {svc} — client onboarding',
                json.dumps({'client_id': client_id, 'service_name': svc, 'source': 'onboarding'}),
                agent
            ))
        
        # Enterprise: Add MFA setup task
        if tier == 'enterprise':
            cur.execute("""
                INSERT INTO task_queue 
                (task_type, display_name, description, payload_json, priority, status, assigned_agent)
                VALUES ('mfa_setup', 'Setup: Multi-Factor Authentication', 
                        'Configure MFA for Enterprise account security',
                        %s, 1, 'PENDING', 'SOL')
            """, (json.dumps({'client_id': client_id, 'tier': tier, 'required': True}),))
            print(f"  ✅ MFA setup task added (Enterprise requirement)")
        
        print(f"  ✅ {len(services)} service setup tasks created")
        
        # Step 4: Record usage metric
        print("[4/6] Recording onboarding usage metric...")
        cur.execute("""
            INSERT INTO usage_metrics (client_id, metric_type, metric_name, quantity, metadata)
            VALUES (%s, 'task_created', 'client_onboarding', 1, %s)
        """, (client_id, json.dumps({'tier': tier, 'services_count': len(services)})))
        print(f"  ✅ Usage recorded")
        
        # Step 5: Log audit
        print("[5/6] Logging audit trail...")
        cur.execute("""
            INSERT INTO audit_log (client_id, action, entity_type, entity_id, new_value)
            VALUES (%s, 'client_onboarded', 'client', %s, %s)
        """, (client_id, str(client_id), json.dumps({'tier': tier, 'role': role, 'services': len(services)})))
        print(f"  ✅ Audit logged")
        
        # Step 6: Commit
        print("[6/6] Committing transaction...")
        conn.commit()
        print(f"  ✅ All changes committed\n")
        
        # Summary
        print(f"{'='*60}")
        print(f"✅ ONBOARDING COMPLETE")
        print(f"{'='*60}")
        print(f"Client ID:       {client_id}")
        print(f"Temporary PIN:   {temp_pin}")
        print(f"PIN expires:     {temp_pin_expires.strftime('%Y-%m-%d %H:%M')}")
        print(f"Conversation ID: {conv_id}")
        print(f"Setup tasks:     {len(services)}")
        print(f"")
        print(f"Next steps for client:")
        print(f"  1. Go to dashboard login")
        print(f"  2. Enter Client ID: {client_id}")
        print(f"  3. Enter temp PIN: {temp_pin}")
        print(f"  4. Set permanent PIN")
        print(f"  5. Explore dashboard")
        print(f"{'='*60}")
        
        return {
            'client_id': client_id,
            'temp_pin': temp_pin,
            'conversation_id': conv_id,
            'services_count': len(services)
        }
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ONBOARDING FAILED: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SAOS Client Onboarding")
    parser.add_argument('--name', required=True, help='Client name')
    parser.add_argument('--email', required=True, help='Client email')
    parser.add_argument('--tier', default='business', choices=['business', 'enterprise', 'private', 'accelerate'])
    parser.add_argument('--role', default='customer', choices=['customer', 'support', 'billing', 'ops', 'admin'])
    parser.add_argument('--stripe-sub', default=None, help='Stripe subscription ID')
    
    args = parser.parse_args()
    
    onboard_client(args.name, args.email, args.tier, args.role, args.stripe_sub)