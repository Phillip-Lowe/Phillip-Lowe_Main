#!/usr/bin/env python3
import json, psycopg2, psycopg2.extras
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import logging

logging.basicConfig(level=logging.DEBUG)
DB_CONFIG = {'host': 'localhost', 'database': 'systack_memory', 'user': 'systack'}
PORT = 9876

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): 
        logging.info(format % args)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        logging.info("OPTIONS request")
    
    def do_POST(self):
        logging.info(f"POST request to {self.path}")
        if self.path != '/queue':
            self.send_error(404); return
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body_raw = self.rfile.read(content_length)
            logging.info(f"Body raw: {body_raw}")
            body = json.loads(body_raw.decode())
            logging.info(f"Body parsed: {body}")
            
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("INSERT INTO task_queue (task_type, payload_json, priority, status, max_retries) VALUES ('DEPLOY', %s::jsonb, 9, 'PENDING', 3) RETURNING id", (json.dumps(body),))
            result = cur.fetchone()
            conn.commit(); cur.close(); conn.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'success': True, 'task_id': result['id']}
            self.wfile.write(json.dumps(response).encode())
            logging.info(f"Task {result['id']} queued")
        except Exception as e:
            logging.error(f"Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

socketserver.TCPServer.allow_reuse_address = True
server = HTTPServer(('0.0.0.0', PORT), Handler)
print(f"[Task Queue API] http://0.0.0.0:{PORT}/queue")
server.serve_forever()