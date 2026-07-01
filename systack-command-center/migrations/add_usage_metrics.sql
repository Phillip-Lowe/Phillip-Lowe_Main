-- Migration: Add usage_metrics table for per-client billing tracking
-- Run: psql -h localhost -U philliplowe -d systack_memory -f add_usage_metrics.sql

-- Drop if exists (careful in production)
DROP TABLE IF EXISTS usage_metrics CASCADE;

CREATE TABLE usage_metrics (
    id          serial PRIMARY KEY,
    client_id   integer NOT NULL REFERENCES saos_clients(id) ON DELETE CASCADE,
    metric_type varchar(50) NOT NULL,  -- 'api_call', 'task_created', 'task_completed', 'chat_message', 'agent_spawned', 'deliverable_uploaded', 'workflow_run', 'email_sent', 'sms_sent'
    metric_name varchar(255),           -- e.g. '/api/portal/status', 'invoice_parser', 'agent_dooby'
    quantity    integer DEFAULT 1,        -- usually 1, but can be batch count
    metadata    jsonb,                    -- extra context: { endpoint: 'GET', agent: 'dooby', workflow_id: '...' }
    recorded_at timestamptz DEFAULT now()
);

-- Indexes for fast queries
CREATE INDEX idx_usage_metrics_client ON usage_metrics(client_id);
CREATE INDEX idx_usage_metrics_type ON usage_metrics(metric_type);
CREATE INDEX idx_usage_metrics_recorded ON usage_metrics(recorded_at);
CREATE INDEX idx_usage_metrics_client_type_date ON usage_metrics(client_id, metric_type, recorded_at);

-- Daily rollup table (pre-aggregated for billing)
DROP TABLE IF EXISTS usage_daily_rollup CASCADE;

CREATE TABLE usage_daily_rollup (
    id          serial PRIMARY KEY,
    client_id   integer NOT NULL REFERENCES saos_clients(id) ON DELETE CASCADE,
    metric_type varchar(50) NOT NULL,
    metric_date date NOT NULL,
    total_count integer DEFAULT 0,
    total_quantity integer DEFAULT 0,
    UNIQUE(client_id, metric_type, metric_date)
);

CREATE INDEX idx_rollup_lookup ON usage_daily_rollup(client_id, metric_type, metric_date);

-- Function to auto-update daily rollup on insert
CREATE OR REPLACE FUNCTION upsert_usage_rollup()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO usage_daily_rollup (client_id, metric_type, metric_date, total_count, total_quantity)
    VALUES (NEW.client_id, NEW.metric_type, DATE(NEW.recorded_at), 1, NEW.quantity)
    ON CONFLICT (client_id, metric_type, metric_date)
    DO UPDATE SET
        total_count = usage_daily_rollup.total_count + 1,
        total_quantity = usage_daily_rollup.total_quantity + NEW.quantity;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usage_metrics_rollup
AFTER INSERT ON usage_metrics
FOR EACH ROW
EXECUTE FUNCTION upsert_usage_rollup();

-- View: current month usage per client
CREATE OR REPLACE VIEW v_current_month_usage AS
SELECT
    client_id,
    metric_type,
    SUM(total_quantity) as total,
    SUM(total_count) as calls
FROM usage_daily_rollup
WHERE metric_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY client_id, metric_type;

-- Test insert (optional, remove after first run)
-- INSERT INTO usage_metrics (client_id, metric_type, metric_name, quantity)
-- VALUES (1, 'api_call', '/api/portal/status', 1);
-- SELECT * FROM v_current_month_usage WHERE client_id = 1;
