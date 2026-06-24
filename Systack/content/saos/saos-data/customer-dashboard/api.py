#!/usr/bin/env python3
"""
SAOS Customer Dashboard API v2.0
Serves client-scoped fleet data + REAL-TIME CHAT for the customer-facing portal.

Usage:
    python3 api.py --port 8768
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)
CORS(app)

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5432"))
DB_NAME = os.environ.get("PGDATABASE", "systack_memory")
DB_USER = os.environ.get("PGUSER", "philliplowe")

# ── DB HELPERS ─────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER
    )

def db_query(sql, params=(), one=False):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.commit()
        if one:
            return dict(rows[0]) if rows else None
        return [dict(r) for r in rows]
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def db_exec(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return str(e)
    finally:
        cur.close()
        conn.close()

# ── AUTH ───────────────────────────────────────────────────────

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

def generate_token():
    return secrets.token_urlsafe(32)

def get_auth_client():
    """Extract client from Authorization: Bearer <token> header."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:].strip()
    token_hash = hash_token(token)
    
    client = db_query("""
        SELECT c.* FROM saos_clients c
        JOIN client_auth_tokens t ON c.id = t.client_id
        WHERE t.token_hash = %s 
        AND t.revoked_at IS NULL 
        AND t.expires_at > NOW()
        LIMIT 1
    """, (token_hash,), one=True)
    
    if client and 'error' not in client:
        # Update last_used
        db_exec("UPDATE client_auth_tokens SET last_used_at = NOW() WHERE token_hash = %s", (token_hash,))
        return client
    return None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client = get_auth_client()
        if not client:
            return jsonify({"error": "Unauthorized", "message": "Valid Bearer token required"}), 401
        request.client = client
        return f(*args, **kwargs)
    return decorated

def require_auth_optional(f):
    """Auth optional - sets request.client if available."""
    @wraps(f)
    def decorated(*args, **kwargs):
        request.client = get_auth_client()
        return f(*args, **kwargs)
    return decorated

# ── EXISTING ENDPOINTS (Updated with auth) ─────────────────────

@app.route('/api/portal/health')
def health():
    return jsonify({"status": "ok", "service": "saos-customer-portal-api", "version": "2.0"})

@app.route('/api/portal/status')
@require_auth
def client_status():
    client = request.client
    client_id = client['id']
    
    # Task counts
    tasks = db_query("""
        SELECT status, COUNT(*) as n FROM task_queue 
        WHERE payload_json->>'client_id' = %s OR %s = '1'
        GROUP BY status
    """, (str(client_id), str(client_id)))
    task_counts = {r['status']: r['n'] for r in tasks if 'status' in r}
    
    # Agent states
    agents = db_query("SELECT * FROM agent_state ORDER BY agent_name")
    
    # Recent chat activity
    recent_chat = db_query("""
        SELECT COUNT(*) as unread FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        WHERE c.client_id = %s AND m.sender_type = 'agent' AND m.read_at IS NULL
    """, (client_id,), one=True)
    
    return jsonify({
        "client": client,
        "tasks": task_counts,
        "agents": agents,
        "unread_messages": recent_chat.get('unread', 0) if recent_chat else 0,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/portal/tasks')
@require_auth
def client_tasks():
    client_id = request.client['id']
    tasks = db_query("""
        SELECT t.id, t.task_type, t.assigned_agent, t.status, t.priority,
               t.created_at, t.completed_at, t.error_message
        FROM task_queue t
        WHERE t.payload_json->>'client_id' = %s OR %s = '1'
        ORDER BY t.created_at DESC
        LIMIT 50
    """, (str(client_id), str(client_id)))
    return jsonify(tasks)

@app.route('/api/portal/agents')
def client_agents():
    """Public - no auth required for agent list."""
    agents = db_query("SELECT * FROM agent_state ORDER BY agent_name")
    return jsonify(agents)

@app.route('/api/portal/client')
@require_auth
def client_info():
    return jsonify(request.client)

# ── CHAT ENDPOINTS ─────────────────────────────────────────────

@app.route('/api/chat/conversations', methods=['GET'])
@require_auth
def list_conversations():
    """Get all conversations for this client."""
    client_id = request.client['id']
    conversations = db_query("""
        SELECT c.*, 
               (SELECT COUNT(*) FROM chat_messages WHERE conversation_id = c.id AND sender_type = 'agent' AND read_at IS NULL) as unread_count,
               (SELECT content FROM chat_messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message,
               (SELECT created_at FROM chat_messages WHERE conversation_id = c.id ORDER BY created_at DESC LIMIT 1) as last_message_at
        FROM chat_conversations c
        WHERE c.client_id = %s
        ORDER BY c.updated_at DESC
    """, (client_id,))
    return jsonify(conversations)

@app.route('/api/chat/conversations', methods=['POST'])
@require_auth
def create_conversation():
    """Create a new chat conversation."""
    client_id = request.client['id']
    data = request.get_json() or {}
    title = data.get('title', 'New Conversation')
    
    result = db_query("""
        INSERT INTO chat_conversations (client_id, title)
        VALUES (%s, %s)
        RETURNING *
    """, (client_id, title), one=True)
    
    # Add system welcome message
    if result and 'error' not in result:
        db_exec("""
            INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
            VALUES (%s, 'system', 'System', 'Conversation started. An agent will respond shortly.', 'system')
        """, (result['id'],))
    
    return jsonify(result or {"error": "Failed to create conversation"})

@app.route('/api/chat/conversations/<int:conv_id>/messages', methods=['GET'])
@require_auth
def get_messages(conv_id):
    """Get messages for a conversation."""
    client_id = request.client['id']
    
    # Verify conversation belongs to client
    conv = db_query("SELECT * FROM chat_conversations WHERE id = %s AND client_id = %s", 
                    (conv_id, client_id), one=True)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404
    
    messages = db_query("""
        SELECT m.*, 
               CASE WHEN m.sender_type = 'agent' THEN m.created_at END as delivered_at
        FROM chat_messages m
        WHERE m.conversation_id = %s
        ORDER BY m.created_at DESC
        LIMIT 100
    """, (conv_id,))
    # Reverse to show oldest first in UI
    messages = list(reversed(messages))
    
    # Mark agent messages as read
    db_exec("""
        UPDATE chat_messages SET read_at = NOW()
        WHERE conversation_id = %s AND sender_type = 'agent' AND read_at IS NULL
    """, (conv_id,))
    
    return jsonify(messages)

@app.route('/api/chat/conversations/<int:conv_id>/messages', methods=['POST'])
@require_auth
def send_message(conv_id):
    """Send a message from client to agents."""
    client_id = request.client['id']
    data = request.get_json() or {}
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({"error": "Message content required"}), 400
    
    # Verify conversation belongs to client
    conv = db_query("SELECT * FROM chat_conversations WHERE id = %s AND client_id = %s", 
                    (conv_id, client_id), one=True)
    if not conv:
        return jsonify({"error": "Conversation not found"}), 404
    if conv.get('status') == 'closed':
        return jsonify({"error": "Conversation is closed. Start a new conversation."}), 400
    
    # Insert client message
    msg = db_query("""
        INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
        VALUES (%s, 'client', 'You', %s, 'text')
        RETURNING *
    """, (conv_id, content), one=True)
    
    # Auto-create task from message if it looks like a request
    task_keywords = ['create', 'build', 'make', 'deploy', 'fix', 'update', 'help', 'need', 'want']
    is_task_request = any(kw in content.lower() for kw in task_keywords)
    
    if is_task_request:
        # Create task in queue
        task = db_query("""
            INSERT INTO task_queue (task_type, payload_json, priority, status, assigned_agent)
            VALUES ('client_request', %s, 5, 'PENDING', 'SOL')
            RETURNING id
        """, (json.dumps({"client_id": client_id, "conversation_id": conv_id, "request": content}),), one=True)
        
        if task and 'error' not in task:
            # Link message to task
            db_exec("UPDATE chat_messages SET task_id = %s WHERE id = %s", (task['id'], msg['id']))
            
            # Add system message about task creation
            db_exec("""
                INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type, task_id)
                VALUES (%s, 'system', 'System', %s, 'task_created', %s)
            """, (conv_id, f"Task #{task['id']} created. SOL will handle this request.", task['id']))
    
    return jsonify(msg or {"error": "Failed to send message"})

@app.route('/api/chat/conversations/<int:conv_id>/close', methods=['POST'])
@require_auth
def close_conversation(conv_id):
    """Close a conversation."""
    client_id = request.client['id']
    db_exec("""
        UPDATE chat_conversations 
        SET status = 'closed', closed_at = NOW()
        WHERE id = %s AND client_id = %s
    """, (conv_id, client_id))
    return jsonify({"success": True})

# ── AUTH ENDPOINTS ─────────────────────────────────────────────

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Simple token-based login. In production, validate against your auth system."""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    
    # For now, accept any valid client_id and issue token
    # In production, validate password/SAML/OAuth here
    if not client_id:
        return jsonify({"error": "client_id required"}), 400
    
    client = db_query("SELECT * FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    # Generate token
    token = generate_token()
    token_hash = hash_token(token)
    expires = datetime.now() + timedelta(days=30)
    
    db_exec("""
        INSERT INTO client_auth_tokens (client_id, token_hash, expires_at)
        VALUES (%s, %s, %s)
    """, (client_id, token_hash, expires))
    
    return jsonify({
        "token": token,
        "expires_at": expires.isoformat(),
        "client": client
    })

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Revoke current token."""
    auth_header = request.headers.get('Authorization', '')
    token = auth_header[7:].strip()
    token_hash = hash_token(token)
    db_exec("UPDATE client_auth_tokens SET revoked_at = NOW() WHERE token_hash = %s", (token_hash,))
    return jsonify({"success": True})

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def me():
    """Get current client info."""
    return jsonify(request.client)

# ── AGENT RESPONSE WEBHOOK (for n8n/OpenClaw to call) ────────

@app.route('/api/chat/webhook/agent-response', methods=['POST'])
def agent_response_webhook():
    """Webhook for agents to send responses back to chat.
    Called by n8n workflow or OpenClaw integration."""
    data = request.get_json() or {}
    
    conversation_id = data.get('conversation_id')
    agent_name = data.get('agent_name', 'SOL')
    content = data.get('content', '')
    task_id = data.get('task_id')
    
    if not conversation_id or not content:
        return jsonify({"error": "conversation_id and content required"}), 400
    
    msg = db_query("""
        INSERT INTO chat_messages (conversation_id, sender_type, sender_name, sender_agent, content, task_id)
        VALUES (%s, 'agent', %s, %s, %s, %s)
        RETURNING *
    """, (conversation_id, agent_name, agent_name, content, task_id), one=True)
    
    return jsonify(msg or {"error": "Failed to save message"})

# ── POLLING ENDPOINT (for real-time updates) ─────────────────

@app.route('/api/chat/poll')
@require_auth
def poll_updates():
    """Poll for new messages/tasks since last check."""
    client_id = request.client['id']
    last_check = request.args.get('since', datetime.now().isoformat())
    
    # New messages
    new_messages = db_query("""
        SELECT m.* FROM chat_messages m
        JOIN chat_conversations c ON m.conversation_id = c.id
        WHERE c.client_id = %s AND m.created_at > %s AND m.sender_type != 'client'
        ORDER BY m.created_at ASC
    """, (client_id, last_check))
    
    # Task updates
    task_updates = db_query("""
        SELECT t.id, t.status, t.assigned_agent, t.completed_at, t.error_message
        FROM task_queue t
        WHERE t.payload_json->>'client_id' = %s 
        AND t.updated_at > %s
        ORDER BY t.updated_at DESC
        LIMIT 10
    """, (str(client_id), last_check))
    
    return jsonify({
        "messages": new_messages,
        "task_updates": task_updates,
        "timestamp": datetime.now().isoformat()
    })

# ── Static file serving ──
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_dashboard(path):
    if not path:
        return send_from_directory(BASE_DIR, 'index.html')
    full_path = os.path.join(BASE_DIR, path)
    if os.path.isfile(full_path):
        return send_from_directory(BASE_DIR, path)
    return send_from_directory(BASE_DIR, 'index.html')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8768)
    args = parser.parse_args()

    print(f"🛰️  SAOS Customer Portal API v2.0 starting on port {args.port}")
    print(f"   Endpoints:")
    print(f"   - GET /                  (dashboard HTML)")
    print(f"   - POST /api/auth/login   (get Bearer token)")
    print(f"   - GET /api/portal/status (client fleet overview)")
    print(f"   - GET /api/chat/conversations (list chats)")
    print(f"   - POST /api/chat/conversations (create chat)")
    print(f"   - GET /api/chat/conversations/<id>/messages")
    print(f"   - POST /api/chat/conversations/<id>/messages")
    print(f"   - POST /api/chat/webhook/agent-response")
    print(f"   - GET /api/chat/poll")
    print(f"")
    print(f"   Auth: Bearer <token> header")

    app.run(host='0.0.0.0', port=args.port, debug=False)
