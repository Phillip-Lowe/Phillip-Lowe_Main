#!/usr/bin/env python3
import requests
import json
import psycopg2

API_KEY = open('/Users/philliplowe/.openclaw/workspaces/sol/.n8n_api_key').read().strip()
DB_CONFIG = {'host': 'localhost', 'database': 'systack_memory', 'user': 'systack'}

headers = {'X-N8N-API-KEY': API_KEY}

# Get latest execution
resp = requests.get('https://n8n.systack.net/api/v1/executions', 
    headers=headers, 
    params={'workflowId': '9I2Xk982Pw8UM9y6', 'limit': '2', 'status': 'success'})

for exec in resp.json().get('data', []):
    exec_id = exec['id']
    print(f"Execution {exec_id}: {exec['status']}")
    
    # Get full data
    resp2 = requests.get(f'https://n8n.systack.net/api/v1/executions/{exec_id}',
        headers=headers,
        params={'includeData': 'true'})
    
    execution = resp2.json()
    run_data = execution.get('data', {}).get('resultData', {}).get('runData', {})
    print(f"Nodes: {list(run_data.keys())}")
    
    for node_name, node_data in run_data.items():
        if node_name == 'Process Config':
            for run in node_data:
                if 'data' in run and run['data']:
                    main_data = run['data'].get('main', [[]])[0]
                    if main_data:
                        json_data = main_data[0].get('json', {})
                        payload = json_data.get('payload')
                        print(f"Payload: {json.dumps(payload, indent=2)[:300] if payload else 'NONE'}")
                        
                        if payload:
                            conn = psycopg2.connect(**DB_CONFIG)
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO task_queue (task_type, payload_json, priority, status, max_retries) VALUES ('DEPLOY', %s::jsonb, 9, 'PENDING', 3) RETURNING id",
                                (json.dumps(payload),)
                            )
                            task_id = cur.fetchone()[0]
                            conn.commit()
                            cur.close()
                            conn.close()
                            print(f"✅ QUEUED TASK {task_id} for {payload.get('client_id')}")