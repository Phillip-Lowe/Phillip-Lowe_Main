#!/usr/bin/env python3
"""
SAOS Provision Bridge — Polls task_queue for pending DEPLOY tasks
and provisions VPS via Vultr API.
"""
import os
import sys
import time
import json
import subprocess
import psycopg2
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from provision_vps import load_credentials, VultrProvisioner

DB_HOST = os.getenv('SAOS_DB_HOST', 'localhost')
DB_PORT = int(os.getenv('SAOS_DB_PORT', '5432'))
DB_NAME = os.getenv('SAOS_DB_NAME', 'systack_memory')
DB_USER = os.getenv('SAOS_DB_USER', 'systack')
DB_PASS = os.getenv('SAOS_DB_PASS', 'Systack2026!CRM')

def db_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )

def poll_pending_tasks():
    """Find PENDING DEPLOY tasks ordered by priority."""
    conn = db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, payload_json, priority, retry_count, max_retries
        FROM task_queue
        WHERE task_type = 'DEPLOY'
          AND status = 'PENDING'
          AND (next_attempt_at IS NULL OR next_attempt_at <= NOW())
        ORDER BY priority DESC, created_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    """)
    row = cur.fetchone()
    if row:
        task_id, payload, priority, retry_count, max_retries = row
        return {
            'id': task_id,
            'payload': payload,
            'priority': priority,
            'retry_count': retry_count,
            'max_retries': max_retries
        }
    cur.close()
    conn.close()
    return None

def update_task(task_id, status, error=None, assigned_agent='SOL-BRIDGE'):
    conn = db_conn()
    cur = conn.cursor()
    if status == 'DONE':
        cur.execute("""
            UPDATE task_queue
            SET status=%s, assigned_agent=%s, completed_at=NOW(), updated_at=NOW()
            WHERE id=%s
        """, (status, assigned_agent, task_id))
    elif status == 'FAILED':
        cur.execute("""
            UPDATE task_queue
            SET status=%s, assigned_agent=%s, error_message=%s,
                retry_count = retry_count + 1,
                next_attempt_at = NOW() + INTERVAL '5 minutes',
                updated_at=NOW()
            WHERE id=%s
        """, (status, assigned_agent, error, task_id))
    else:
        cur.execute("""
            UPDATE task_queue
            SET status=%s, assigned_agent=%s, updated_at=NOW()
            WHERE id=%s
        """, (status, assigned_agent, task_id))
    conn.commit()
    cur.close()
    conn.close()

def provision_from_task(task):
    """Provision VPS for a DEPLOY task."""
    payload = task['payload']
    client_id = payload.get('client_id') or payload.get('goal', '').replace(' ', '-')
    if not client_id or client_id == '':
        client_id = 'SAOS-Client'
    customer_email = payload.get('customer_email', 'unknown@systack.net')
    tier = payload.get('tier', 'business')
    agent_name = payload.get('customer_name', 'SAOS-Client').replace(' ', '')
    if not agent_name or agent_name == '':
        agent_name = 'SAOSAgent'
    
    print(f"[BRIDGE] Task {task['id']}: Provisioning {client_id} (tier={tier})")
    
    creds = load_credentials()
    prov = VultrProvisioner(creds['vultr'])
    ts_key = creds.get('tailscale_auth', '')
    
    try:
        result = prov.create_instance(
            client_id=client_id,
            tier=tier,
            agent_name=agent_name,
            tailscale_auth_key=ts_key
        )
        if 'error' in result:
            raise Exception(result['error'])
        
        # create_instance returns the instance dict directly
        instance_id = result.get('id') or result.get('instance', {}).get('id')
        if not instance_id:
            raise Exception(f"No instance ID in response: {result}")
        print(f"[BRIDGE] VPS created: {instance_id}")
        return instance_id
    except Exception as e:
        raise Exception(f"Vultr provisioning failed: {e}")

def run_once():
    task = poll_pending_tasks()
    if not task:
        return False
    
    print(f"[BRIDGE] Found task {task['id']}, retry={task['retry_count']}/{task['max_retries']}")
    
    if task['retry_count'] >= task['max_retries']:
        print(f"[BRIDGE] Task {task['id']} exceeded max retries, marking DEAD")
        update_task(task['id'], 'FAILED', 'Max retries exceeded')
        return True
    
    update_task(task['id'], 'RUNNING')
    
    try:
        instance_id = provision_from_task(task)
        update_task(task['id'], 'DONE', assigned_agent=f'SOL-BRIDGE:{instance_id}')
        print(f"[BRIDGE] Task {task['id']} COMPLETE -> {instance_id}")
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"[BRIDGE] Task {task['id']} FAILED: {error_msg}")
        update_task(task['id'], 'FAILED', error_msg)
        return True

def run_daemon(poll_interval=30):
    print(f"[BRIDGE] Starting SAOS provision bridge (poll={poll_interval}s)")
    while True:
        try:
            processed = run_once()
            if not processed:
                time.sleep(poll_interval)
            else:
                time.sleep(5)  # Brief pause between tasks
        except KeyboardInterrupt:
            print("\n[BRIDGE] Stopping")
            break
        except Exception as e:
            print(f"[BRIDGE] ERROR: {e}")
            time.sleep(poll_interval)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='SAOS Provision Bridge')
    parser.add_argument('--once', action='store_true', help='Run one poll cycle')
    parser.add_argument('--interval', type=int, default=30, help='Poll interval seconds')
    args = parser.parse_args()
    
    if args.once:
        run_once()
    else:
        run_daemon(args.interval)
