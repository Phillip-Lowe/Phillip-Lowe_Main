-- Utopia Deli — Message Logging Table
-- Run this in the utopia_deli database before activating the n8n workflow

CREATE TABLE IF NOT EXISTS message_logs (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
    channel VARCHAR(10) CHECK (channel IN ('email', 'sms')),
    message_type VARCHAR(50),
    content TEXT,
    status VARCHAR(20),
    twilio_sid VARCHAR(100),
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_message_logs_contact 
    ON message_logs(contact_id);

CREATE INDEX IF NOT EXISTS idx_message_logs_sent_at 
    ON message_logs(sent_at DESC);

CREATE INDEX IF NOT EXISTS idx_message_logs_channel 
    ON message_logs(channel);

CREATE INDEX IF NOT EXISTS idx_message_logs_campaign 
    ON message_logs(message_type, sent_at DESC);

-- Verify table created
SELECT COUNT(*) AS message_logs_ready FROM message_logs;
