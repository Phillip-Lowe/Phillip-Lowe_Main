#!/usr/bin/env python3
"""
Onboarding Bridge — Polls a JSON file for new configs and queues them in task_queue
"""

import json
import psycopg2
import time
import os

DB_CONFIG = {'host': 'localhost', 'database': 'systack_memory', 'user': 'systack'}
CONFIG_FILE = '/tmp/systack-saas-init/pending_configs.json'

def load_configs():
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except:
        return []

def save_configs(configs):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=2)

def queue_task(config):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO task_queue (task_type, payload_json, priority, status, max_retries) VALUES ('DEPLOY', %s::jsonb, 9, 'PENDING', 3) RETURNING id",
        (json.dumps(config),)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return task_id

def main():
    print("[Onboarding Bridge] Starting...")
    while True:
        configs = load_configs()
        if configs:
            remaining = []
            for config in configs:
                try:
                    task_id = queue_task(config)
                    print(f"[Onboarding Bridge] Queued task {task_id} for {config.get('client_id')}")
                except Exception as e:
                    print(f"[Onboarding Bridge] Error: {e}")
                    remaining.append(config)
            save_configs(remaining)
        time.sleep(5)

if __name__ == '__main__':
    main()