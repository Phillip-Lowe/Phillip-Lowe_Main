#!/usr/bin/env python3
"""
SAOS Customer Dashboard API v2.1
Enhanced UX: better task descriptions, agent info, PIN management, onboarding flow.
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
import random
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
import base64
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DELIVERABLES_DIR = os.path.join(BASE_DIR, 'deliverables')
os.makedirs(DELIVERABLES_DIR, exist_ok=True)
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

def generate_pin(length=6):
    """Generate a numeric PIN."""
    return ''.join(random.choices(string.digits, k=length))

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

# ── NEW: ONBOARDING & PIN MANAGEMENT ───────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register_client():
    """
    First-time client registration.
    Client provides client_id + temp_pin + new_pin.
    Sets a permanent PIN and activates the account.
    """
    data = request.get_json() or {}
    client_id = data.get('client_id')
    temp_pin = data.get('temp_pin')
    new_pin = data.get('new_pin')
    
    if not client_id:
        return jsonify({"error": "client_id required"}), 400
    if not temp_pin:
        return jsonify({"error": "Temporary PIN required"}), 400
    if not new_pin:
        return jsonify({"error": "New PIN required"}), 400
    if len(new_pin) < 4 or len(new_pin) > 10:
        return jsonify({"error": "PIN must be 4-10 digits"}), 400
    
    client = db_query("SELECT * FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    # Verify temp PIN
    if client.get('temp_pin') != temp_pin:
        return jsonify({"error": "Invalid temporary PIN"}), 401
    
    # Check expiration
    if client.get('temp_pin_expires_at') and client['temp_pin_expires_at'] < datetime.now():
        return jsonify({"error": "Temporary PIN has expired. Contact support."}), 410
    
    # Set permanent PIN and activate
    db_exec("""
        UPDATE saos_clients 
        SET auth_pin = %s, onboarding_status = 'active', 
            onboarding_completed_at = NOW(), temp_pin = NULL,
            temp_pin_expires_at = NULL
        WHERE id = %s
    """, (new_pin, client_id))
    
    return jsonify({
        "success": True,
        "message": "PIN set successfully. You can now log in with your client ID and PIN.",
        "client_id": client_id
    })

@app.route('/api/auth/change-pin', methods=['POST'])
@require_auth
def change_pin():
    """Logged-in client changes their PIN."""
    client_id = request.client['id']
    data = request.get_json() or {}
    current_pin = data.get('current_pin')
    new_pin = data.get('new_pin')
    
    if not current_pin or not new_pin:
        return jsonify({"error": "Current PIN and new PIN required"}), 400
    if len(new_pin) < 4 or len(new_pin) > 10:
        return jsonify({"error": "PIN must be 4-10 digits"}), 400
    
    client = db_query("SELECT auth_pin FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not client or client.get('auth_pin') != current_pin:
        return jsonify({"error": "Current PIN is incorrect"}), 401
    
    db_exec("UPDATE saos_clients SET auth_pin = %s WHERE id = %s", (new_pin, client_id))
    return jsonify({"success": True, "message": "PIN updated successfully"})

@app.route('/api/auth/forgot-pin', methods=['POST'])
def forgot_pin():
    """Request PIN reset. Requires email + client_id."""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    email = data.get('email')
    
    if not client_id or not email:
        return jsonify({"error": "client_id and email required"}), 400
    
    client = db_query("SELECT * FROM saos_clients WHERE id = %s AND customer_email = %s", 
                      (client_id, email), one=True)
    if not client:
        # Return success even if not found (security - don't leak existence)
        return jsonify({"success": True, "message": "If your account exists, a reset link has been sent."})
    
    # Generate new temp PIN
    temp = generate_pin(6)
    expires = datetime.now() + timedelta(hours=24)
    
    db_exec("""
        UPDATE saos_clients 
        SET temp_pin = %s, temp_pin_expires_at = %s, onboarding_status = 'pending'
        WHERE id = %s
    """, (temp, expires, client_id))
    
    # TODO: Send email with temp PIN via CHATTY/n8n
    # For now, return it (in production, this would be sent to email only)
    return jsonify({
        "success": True,
        "message": "PIN reset. Contact your SAOS administrator for your temporary PIN.",
        "temp_pin": temp,  # REMOVE IN PRODUCTION - send via email instead
        "expires_at": expires.isoformat()
    })

@app.route('/api/portal/onboarding-status/<int:client_id>')
def onboarding_status(client_id):
    """Check if client needs to set up PIN (public endpoint)."""
    client = db_query("""
        SELECT id, customer_name, onboarding_status, auth_pin IS NOT NULL as has_pin,
               temp_pin IS NOT NULL as has_temp_pin
        FROM saos_clients WHERE id = %s
    """, (client_id,), one=True)
    
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    return jsonify({
        "client_id": client_id,
        "onboarding_status": client.get('onboarding_status', 'pending'),
        "needs_setup": not client.get('has_pin') and not client.get('has_temp_pin'),
        "can_register": client.get('has_temp_pin'),
        "has_active_pin": client.get('has_pin')
    })

# ── EXISTING ENDPOINTS (Updated with auth + descriptions) ──

@app.route('/api/portal/health')
def health():
    return jsonify({"status": "ok", "service": "saos-customer-portal-api", "version": "2.0"})

@app.route('/api/portal/status')
@require_auth
def client_status():
    client = request.client
    client_id = client['id']
    tier = client.get('tier', 'business')
    
    # Task counts
    tasks = db_query("""
        SELECT status, COUNT(*) as n FROM task_queue 
        WHERE payload_json->>'client_id' = %s OR %s = '1'
        GROUP BY status
    """, (str(client_id), str(client_id)))
    task_counts = {r['status']: r['n'] for r in tasks if 'status' in r}
    
    # Agent states filtered by tier
    TIER_AGENTS = {
        'personal': ['SOL', 'CHATTY'],
        'personal+': ['SOL', 'CHATTY', 'GENI'],
        'business': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI'],
        'enterprise': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI', 'CODY', 'VALI'],
        'private': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'JURIS'],
        'accelerate': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS']
    }
    allowed = TIER_AGENTS.get(tier, TIER_AGENTS['business'])
    
    agents = db_query("""
        SELECT agent_name, role, role_description, status, avatar_emoji,
               capabilities, tier_access, last_heartbeat
        FROM agent_state
        WHERE agent_name = ANY(%s)
        ORDER BY agent_name
    """, (allowed,))
    
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
        "onboarding_status": client.get('onboarding_status'),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/portal/tasks')
@require_auth
def client_tasks():
    client_id = request.client['id']
    tasks = db_query("""
        SELECT t.id, t.task_type, COALESCE(t.display_name, t.task_type) as display_name,
               COALESCE(t.description, '') as description,
               t.assigned_agent, t.status, t.priority,
               t.created_at, t.completed_at, t.error_message
        FROM task_queue t
        WHERE t.payload_json->>'client_id' = %s OR %s = '1'
        ORDER BY t.created_at DESC
        LIMIT 50
    """, (str(client_id), str(client_id)))
    return jsonify(tasks)

@app.route('/api/portal/agents')
def client_agents():
    """Public - returns agents filtered by client tier."""
    # Get client's tier from optional auth
    auth_header = request.headers.get('Authorization', '')
    tier = 'business'  # default
    
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
        token_hash = hash_token(token)
        client = db_query("""
            SELECT c.tier FROM saos_clients c
            JOIN client_auth_tokens t ON c.id = t.client_id
            WHERE t.token_hash = %s AND t.revoked_at IS NULL AND t.expires_at > NOW()
            LIMIT 1
        """, (token_hash,), one=True)
        if client and 'error' not in client:
            tier = client.get('tier', 'business')
    
    # Tier-to-agent mapping
    TIER_AGENTS = {
        'personal': ['SOL', 'CHATTY'],
        'personal+': ['SOL', 'CHATTY', 'GENI'],
        'business': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI'],
        'enterprise': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS', 'PESSI', 'CODY', 'VALI'],
        'private': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'JURIS'],
        'accelerate': ['SOL', 'ASSEMBLY', 'CHATTY', 'ATLAS', 'GENI', 'JURIS']
    }
    
    allowed = TIER_AGENTS.get(tier, TIER_AGENTS['business'])
    
    agents = db_query("""
        SELECT agent_name, role, role_description, status, avatar_emoji,
               capabilities, tier_access
        FROM agent_state 
        WHERE agent_name = ANY(%s)
        ORDER BY agent_name
    """, (allowed,))
    
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
    """PIN-based login. Requires client_id + PIN."""
    data = request.get_json() or {}
    client_id = data.get('client_id')
    pin = data.get('pin')
    
    if not client_id:
        return jsonify({"error": "client_id required"}), 400
    if not pin:
        return jsonify({"error": "PIN required"}), 400
    
    client = db_query("SELECT * FROM saos_clients WHERE id = %s", (client_id,), one=True)
    if not client:
        return jsonify({"error": "Client not found"}), 404
    
    # Check PIN
    if not client.get('auth_pin'):
        return jsonify({"error": "PIN not set. Contact support."}), 403
    
    if client['auth_pin'] != pin:
        return jsonify({"error": "Invalid PIN"}), 401
    
    # Generate token
    token = generate_token()
    token_hash = hash_token(token)
    expires = datetime.now() + timedelta(days=30)
    
    db_exec("""
        INSERT INTO client_auth_tokens (client_id, token_hash, expires_at)
        VALUES (%s, %s, %s)
    """, (client_id, token_hash, expires))
    
    # Update login stats
    db_exec("""
        UPDATE saos_clients 
        SET last_login_at = NOW(), login_count = COALESCE(login_count, 0) + 1
        WHERE id = %s
    """, (client_id,))
    
    return jsonify({
        "token": token,
        "expires_at": expires.isoformat(),
        "client": client,
        "onboarding_status": client.get('onboarding_status')
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

# ── TASK CREATION (Client-initiated) ─────────────────────

# Client-facing agent pool (internal agents like DOOBY/LOKI not exposed)
SERVICE_AGENT_MAP = {
    'Invoice Processing': 'ASSEMBLY',
    'Automated Invoice Processing': 'ASSEMBLY',
    'Lead Qualification': 'ASSEMBLY',
    'Lead Qualification Pipeline': 'ASSEMBLY',
    'Customer Support Drafting': 'CHATTY',
    'Self-Hosted Customer Support': 'CHATTY',
    'Customer Support Automations': 'CHATTY',
    'Team Collaboration': 'CHATTY',
    'Document Classification': 'ASSEMBLY',
    'Document Classification Engine': 'ASSEMBLY',
    'Report Generation': 'ASSEMBLY',
    'Scheduled Report Generator': 'ASSEMBLY',
    'Email Triage': 'CHATTY',
    'Email Triage & Drafting': 'CHATTY',
    'Calendar Management': 'ASSEMBLY',
    'Task Reminders & Follow-ups': 'ASSEMBLY',
    'Document Summarization': 'ASSEMBLY',
    'Research Assistance': 'ATLAS',
    'Note Organization': 'ASSEMBLY',
    'Multi-Device Sync': 'ASSEMBLY',
    'Voice Interaction': 'GENI',
    'Expense Tracking': 'ASSEMBLY',
    'Custom Integrations': 'ASSEMBLY',
    'On-Premise Deployment': 'ASSEMBLY',
    'HIPAA-Grade Privacy': 'JURIS',
    'White-Glove Setup': 'ASSEMBLY',
    'Priority Support (4hr SLA)': 'PESSI',
    'Private Document Extraction': 'ASSEMBLY',
    'Data Entry Elimination': 'ASSEMBLY',
    'Private Knowledge Base Search': 'ATLAS',
    'Compliance Audit Trail': 'JURIS',
}

@app.route('/api/tasks/request', methods=['POST'])
@require_auth
def request_task():
    """Client requests setup for a service. Creates a proper task."""
    client_id = request.client['id']
    data = request.get_json() or {}
    service_name = data.get('service_name', 'Unknown Service')
    service_desc = data.get('service_description', '')
    
    # Determine agent based on service
    assigned_agent = SERVICE_AGENT_MAP.get(service_name, 'SOL')
    
    # Create task
    task = db_query("""
        INSERT INTO task_queue (task_type, display_name, description, payload_json, priority, status, assigned_agent)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, task_type, display_name, description, assigned_agent, status, priority, created_at
    """, (
        'service_setup',
        f'Setup: {service_name}',
        f'Client requested setup for {service_name}. {service_desc}',
        json.dumps({
            'client_id': client_id,
            'service_name': service_name,
            'service_description': service_desc,
            'requested_by': 'client_dashboard'
        }),
        4,  # High priority
        'PENDING',
        assigned_agent
    ), one=True)
    
    if not task or 'error' in task:
        return jsonify({'error': 'Failed to create task'}), 500
    
    # Create notification for client
    db_exec("""
        INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
        SELECT id, 'system', 'System', %s, 'task_created'
        FROM chat_conversations
        WHERE client_id = %s AND status IN ('open', 'active')
        ORDER BY updated_at DESC
        LIMIT 1
    """, (f"📋 Task #{task['id']} created: Setup {service_name}. Assigned to {assigned_agent}.", client_id))
    
    return jsonify({
        'success': True,
        'task_id': task['id'],
        'assigned_agent': assigned_agent,
        'status': 'PENDING',
        'message': f'Task created and assigned to {assigned_agent}'
    })

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

# ── INTERNAL: Task Polling (for OpenClaw cron/agent spawn) ──

@app.route('/api/internal/pending-tasks')
def pending_tasks():
    """Internal endpoint for OpenClaw/n8n to poll for pending tasks.
    Returns tasks ready for agent assignment.
    Requires internal-api-key header for basic security.
    """
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get pending tasks that haven't been claimed yet
    tasks = db_query("""
        SELECT t.id, t.task_type, t.display_name, t.description,
               t.assigned_agent, t.priority, t.payload_json,
               t.created_at, c.id as client_id, c.customer_name,
               c.customer_email, c.tier
        FROM task_queue t
        JOIN saos_clients c ON (t.payload_json->>'client_id')::int = c.id
        WHERE t.status = 'PENDING'
        AND (t.payload_json->>'claimed_at') IS NULL
        ORDER BY t.priority DESC, t.created_at ASC
        LIMIT 10
    """)
    
    return jsonify({
        'tasks': tasks,
        'count': len(tasks),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/internal/claim-task/<int:task_id>', methods=['POST'])
def claim_task(task_id):
    """Mark a task as claimed by an agent runner.
    Prevents duplicate agent spawns."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    runner_id = data.get('runner_id', 'unknown')
    
    # Mark task as claimed
    db_exec("""
        UPDATE task_queue
        SET payload_json = payload_json || %s,
            updated_at = NOW()
        WHERE id = %s
    """, (json.dumps({'claimed_at': datetime.now().isoformat(), 'runner_id': runner_id}), task_id))
    
    return jsonify({'success': True, 'task_id': task_id, 'claimed_by': runner_id})

@app.route('/api/internal/update-task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    """Update task status from agent execution.
    Called by spawned agents via webhook."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    status = data.get('status')
    result = data.get('result', '')
    error = data.get('error', '')
    
    if status not in ['RUNNING', 'DONE', 'FAILED']:
        return jsonify({'error': 'Invalid status'}), 400
    
    # Update task
    if status == 'RUNNING':
        db_exec("""
            UPDATE task_queue
            SET status = %s, updated_at = NOW()
            WHERE id = %s
        """, (status, task_id))
    elif status == 'DONE':
        db_exec("""
            UPDATE task_queue
            SET status = %s, completed_at = NOW(), updated_at = NOW(),
                payload_json = payload_json || %s
            WHERE id = %s
        """, (status, json.dumps({'result': result}), task_id))
    elif status == 'FAILED':
        db_exec("""
            UPDATE task_queue
            SET status = %s, error_message = %s, updated_at = NOW()
            WHERE id = %s
        """, (status, error, task_id))
    
    # Notify client via chat if there's an open conversation
    task = db_query("SELECT payload_json FROM task_queue WHERE id = %s", (task_id,), one=True)
    if task:
        payload = task.get('payload_json', {})
        client_id = payload.get('client_id') if isinstance(payload, dict) else None
        
        if client_id:
            status_msg = {
                'RUNNING': f"🔄 Task #{task_id} is now being processed.",
                'DONE': f"✅ Task #{task_id} completed! {result[:200] if result else ''}",
                'FAILED': f"❌ Task #{task_id} failed: {error[:200] if error else 'Unknown error'}"
            }.get(status, f"Task #{task_id} status: {status}")
            
            # Insert chat notification
            db_exec("""
                INSERT INTO chat_messages (conversation_id, sender_type, sender_name, content, message_type)
                SELECT id, 'system', 'System', %s, 'task_update'
                FROM chat_conversations
                WHERE client_id = %s AND status IN ('open', 'active')
                ORDER BY updated_at DESC
                LIMIT 1
            """, (status_msg, client_id))
            
            # Queue async notification for offline clients
            urgency = 'urgent' if status == 'FAILED' else 'normal'
            channel = 'imessage' if status == 'FAILED' else 'auto'
            
            db_exec("""
                INSERT INTO notifications (client_id, task_id, message, urgency, channel, status)
                VALUES (%s, %s, %s, %s, %s, 'queued')
            """, (client_id, task_id, status_msg, urgency, channel))
    
    return jsonify({'success': True, 'task_id': task_id, 'status': status})

# ── PDF Downloads (updated for v2.1) ──
@app.route('/download/quickstart-v5')
def serve_quickstart_v5():
    return send_from_directory(BASE_DIR, 'SAOS-Quick-Start-Guide-v5.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/user-guide-v3')
def serve_user_guide_v3():
    return send_from_directory(BASE_DIR, 'SAOS-Dashboard-User-Guide-v3.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/manual-v5')
def serve_manual_v5():
    return send_from_directory(BASE_DIR, 'SAOS-Service-Manual-v5.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/architecture-v4')
def serve_arch_v4():
    return send_from_directory(BASE_DIR, 'SAOS-Architecture-Overview-v4.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/mobile-guide-v2')
def serve_mobile_guide_v2():
    return send_from_directory(BASE_DIR, 'SAOS-Dashboard-Mobile-Access-Guide-v2.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

@app.route('/download/enterprise-guide')
def serve_enterprise_guide():
    return send_from_directory(BASE_DIR, 'SyStack-Enterprise-Deployment-Guide-v1.0.pdf',
                               as_attachment=False, mimetype='application/pdf')

# ── NOTIFICATIONS (Async — Email/iMessage) ──────────────────

@app.route('/api/internal/notify-client', methods=['POST'])
def notify_client():
    """Send async notification to client via BlueBubbles (iMessage) or email.
    Called by task update system when client is offline or for urgent updates.
    """
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    client_id = data.get('client_id')
    task_id = data.get('task_id')
    message = data.get('message', '')
    urgency = data.get('urgency', 'normal')  # normal, urgent, critical
    channel = data.get('channel', 'auto')  # auto, imessage, email
    
    if not client_id or not message:
        return jsonify({'error': 'client_id and message required'}), 400
    
    # Get client info
    client = db_query("""
        SELECT customer_name, customer_email, tier 
        FROM saos_clients WHERE id = %s
    """, (client_id,), one=True)
    
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    # Store notification log
    db_exec("""
        INSERT INTO notifications (client_id, task_id, message, urgency, channel, status)
        VALUES (%s, %s, %s, %s, %s, 'queued')
    """, (client_id, task_id, message, urgency, channel))
    
    # Determine delivery channel
    delivery_channel = channel
    if channel == 'auto':
        delivery_channel = 'imessage' if urgency in ['urgent', 'critical'] else 'email'
    
    # Send via BlueBubbles (iMessage) for urgent or critical
    if delivery_channel == 'imessage':
        try:
            import subprocess
            result = subprocess.run([
                'curl', '-s', '-X', 'POST',
                'http://phillips-macbook-air.tail573d57.ts.net:1234/api/message',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    'chatGuid': '+15012746231',
                    'message': message[:500]  # iMessage limit
                })
            ], capture_output=True, text=True, timeout=10)
            
            db_exec("""
                UPDATE notifications SET status = 'sent', sent_at = NOW()
                WHERE client_id = %s AND task_id = %s AND status = 'queued'
            """, (client_id, task_id))
            
            return jsonify({
                'success': True,
                'channel': 'imessage',
                'message': message,
                'client': client['customer_name']
            })
        except Exception as e:
            # Fallback to email
            delivery_channel = 'email'
    
    # Send via email (SMTP)
    if delivery_channel == 'email':
        # For now, store as pending email — n8n will pick up and send
        db_exec("""
            UPDATE notifications SET status = 'pending_email', sent_at = NOW()
            WHERE client_id = %s AND task_id = %s AND status = 'queued'
        """, (client_id, task_id))
        
        return jsonify({
            'success': True,
            'channel': 'email',
            'message': message,
            'client': client['customer_name'],
            'note': 'Queued for email delivery via n8n'
        })
    
    return jsonify({'error': 'No delivery channel available'}), 500

@app.route('/api/internal/notifications/pending')
def pending_notifications():
    """Get pending notifications for n8n to process."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    notifications = db_query("""
        SELECT n.*, c.customer_name, c.customer_email
        FROM notifications n
        JOIN saos_clients c ON n.client_id = c.id
        WHERE n.status IN ('queued', 'pending_email')
        ORDER BY n.created_at DESC
        LIMIT 50
    """)
    
    return jsonify({
        'notifications': notifications,
        'count': len(notifications),
        'timestamp': datetime.now().isoformat()
    })

# ── DELIVERABLES (Task Output Storage) ─────────────────────

@app.route('/api/internal/deliverables/upload', methods=['POST'])
def upload_deliverable():
    """Upload a deliverable file for a task.
    Called by agents after completing work."""
    api_key = request.headers.get('X-Internal-Api-Key', '')
    expected = os.environ.get('SAOS_INTERNAL_API_KEY', 'saos-internal-dev-key')
    
    if api_key != expected:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    task_id = data.get('task_id')
    filename = data.get('filename', 'deliverable.txt')
    content_base64 = data.get('content_base64', '')
    description = data.get('description', '')
    
    if not task_id or not content_base64:
        return jsonify({'error': 'task_id and content_base64 required'}), 400
    
    # Generate unique filename
    file_id = str(uuid.uuid4())[:8]
    safe_filename = f"task_{task_id}_{file_id}_{filename.replace(' ', '_')}"
    filepath = os.path.join(DELIVERABLES_DIR, safe_filename)
    
    # Decode and save
    try:
        content = base64.b64decode(content_base64)
        with open(filepath, 'wb') as f:
            f.write(content)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    
    # Store reference in task payload
    db_exec("""
        UPDATE task_queue
        SET payload_json = payload_json || %s,
            updated_at = NOW()
        WHERE id = %s
    """, (json.dumps({
        'deliverable': {
            'filename': filename,
            'stored_as': safe_filename,
            'description': description,
            'size': len(content),
            'uploaded_at': datetime.now().isoformat()
        }
    }), task_id))
    
    return jsonify({
        'success': True,
        'task_id': task_id,
        'filename': filename,
        'download_url': f'/api/deliverables/download/{safe_filename}'
    })

@app.route('/api/deliverables/download/<filename>')
@require_auth
def download_deliverable(filename):
    """Download a deliverable file."""
    # Security: prevent directory traversal
    safe_name = os.path.basename(filename)
    filepath = os.path.join(DELIVERABLES_DIR, safe_name)
    
    if not os.path.isfile(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory(DELIVERABLES_DIR, safe_name, as_attachment=True)

@app.route('/api/portal/deliverables')
@require_auth
def list_deliverables():
    """List all deliverables for this client."""
    client_id = request.client['id']
    
    tasks = db_query("""
        SELECT id, task_type, display_name, payload_json, completed_at
        FROM task_queue
        WHERE payload_json->'deliverable' IS NOT NULL
        AND (payload_json->>'client_id')::int = %s
        ORDER BY completed_at DESC
        LIMIT 50
    """, (client_id,))
    
    deliverables = []
    for task in tasks:
        payload = task.get('payload_json', {})
        if isinstance(payload, dict) and 'deliverable' in payload:
            d = payload['deliverable']
            deliverables.append({
                'task_id': task['id'],
                'task_name': task.get('display_name', task['task_type']),
                'filename': d.get('filename'),
                'description': d.get('description'),
                'size': d.get('size', 0),
                'download_url': f'/api/deliverables/download/{d.get("stored_as")}',
                'completed_at': task.get('completed_at')
            })
    
    return jsonify(deliverables)

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

    print(f"🛰️  SAOS Customer Portal API v2.1 starting on port {args.port}")
    print(f"   NEW v2.1 features:")
    print(f"   - POST /api/auth/register (first-time PIN setup)")
    print(f"   - POST /api/auth/change-pin (logged-in clients)")
    print(f"   - POST /api/auth/forgot-pin (PIN reset)")
    print(f"   - GET  /api/portal/onboarding-status/<id> (check if setup needed)")
    print(f"   - Enhanced agent descriptions with role + capabilities")
    print(f"   - Task display_name + description fields")
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
