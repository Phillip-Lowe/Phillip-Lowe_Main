#!/usr/bin/env python3
"""
SAOS Task Queue API — Simple HTTP endpoint for n8n to queue DEPLOY tasks

Usage:
    python3 task_queue_api.py
    
Endpoint: POST http://localhost:8765/queue
Payload: Any JSON (stored as payload_json)

This avoids n8n Postgres credential issues by providing a simple HTTP interface.
"""

import json
import psycopg2
import psycopg2.extras
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'database': 'systack_memory',
    'user': 'systack',
    # No password needed for local Unix socket auth
}

class TaskQueueHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_POST(self):
        if self.path != '/queue':
            self.send_error(404)
            return
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Connect to database
            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Insert task
            cursor.execute("""
                INSERT INTO task_queue (task_type, payload_json, priority, status, max_retries)
                VALUES ('DEPLOY', %s::jsonb, 9, 'PENDING', 3)
                RETURNING id
            """, (json.dumps(data),))
            
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            # Return success
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'task_id': result['id'],
                'message': 'DEPLOY task queued'
            }
            self.wfile.write(json.dumps(response).encode())
            
            print(f"[✓] Queued DEPLOY task #{result['id']} for client: {data.get('client_id', 'unknown')}")
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"[✗] Error: {e}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server(port=8766):
    server = HTTPServer(("0.0.0.0", port), TaskQueueHandler)
    print(f"[Task Queue API] Listening on http://localhost:{port}/queue")
    print(f"[Task Queue API] POST JSON payload to queue DEPLOY tasks")
    server.serve_forever()

if __name__ == '__main__':
    run_server()