-- SAOS Customer Dashboard Chat Schema
-- Add to existing systack_memory database

-- Chat conversations (threads between client and agents)
CREATE TABLE IF NOT EXISTS chat_conversations (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES saos_clients(id),
    title VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'closed', 'archived')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

-- Individual chat messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('client', 'agent', 'system')),
    sender_name VARCHAR(50) NOT NULL,  -- 'Customer', 'SOL', 'CODY', etc.
    sender_agent VARCHAR(50),  -- NULL for client, agent ID for agents
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'task_created', 'task_update', 'file', 'system')),
    task_id INTEGER REFERENCES task_queue(id),  -- Link to task if message created one
    metadata JSONB DEFAULT '{}',  -- Extra data: file URLs, task status, etc.
    read_at TIMESTAMP,  -- When recipient read it
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Client access tokens for auth (simple token-based)
CREATE TABLE IF NOT EXISTS client_auth_tokens (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES saos_clients(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 hash
    expires_at TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_conv_client ON chat_conversations(client_id, status);
CREATE INDEX IF NOT EXISTS idx_chat_msg_conv ON chat_messages(conversation_id, created_at);
CREATE INDEX IF NOT EXISTS idx_chat_msg_unread ON chat_messages(conversation_id, read_at) WHERE read_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_auth_token ON client_auth_tokens(token_hash) WHERE revoked_at IS NULL;

-- Trigger to update conversation updated_at
CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_conversation ON chat_messages;
CREATE TRIGGER trigger_update_conversation
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();
