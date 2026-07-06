-- SAOS Workflow Delivery Tables
-- Phase 1: Shared n8n with customer isolation
-- Created: 2026-07-06 per ORACLE directive

-- ════════════════════════════════════════════════════════════════
-- customer_workflows: First-class workflow tracking
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS customer_workflows (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES saos_clients(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    service_type TEXT NOT NULL DEFAULT 'n8n',
    workflow_name TEXT NOT NULL,
    n8n_workflow_id TEXT,
    deployment_mode TEXT NOT NULL DEFAULT 'shared',
    environment TEXT NOT NULL DEFAULT 'production',
    status TEXT NOT NULL DEFAULT 'draft',
    webhook_url TEXT,
    test_payload JSONB,
    expected_result TEXT,
    last_run_at TIMESTAMP,
    last_success_at TIMESTAMP,
    last_error_at TIMESTAMP,
    error_count INTEGER NOT NULL DEFAULT 0,
    backup_file_path TEXT,
    readme_file_path TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Status constraint
    CONSTRAINT valid_workflow_status CHECK (status IN (
        'draft', 'building', 'deployed', 'testing', 
        'active', 'failed', 'paused', 'archived', 'needs_review'
    )),
    CONSTRAINT valid_deployment_mode CHECK (deployment_mode IN (
        'shared', 'dedicated', 'byo'
    ))
);

-- ════════════════════════════════════════════════════════════════
-- workflow_events: Audit trail for workflow lifecycle
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS workflow_events (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES customer_workflows(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_event_type CHECK (event_type IN (
        'created', 'building', 'deployed', 'test_started', 'test_passed',
        'test_failed', 'activated', 'paused', 'failed', 'retried',
        'notification_sent', 'notification_failed', 'archived'
    )),
    CONSTRAINT valid_event_severity CHECK (severity IN (
        'debug', 'info', 'warning', 'error', 'critical'
    ))
);

-- ════════════════════════════════════════════════════════════════
-- workflow_test_runs: Individual test execution records
-- ════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS workflow_test_runs (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES customer_workflows(id) ON DELETE CASCADE,
    test_payload JSONB,
    response_status INTEGER,
    response_body TEXT,
    success BOOLEAN,
    duration_ms INTEGER,
    error_message TEXT,
    run_at TIMESTAMP DEFAULT NOW()
);

-- ════════════════════════════════════════════════════════════════
-- Indexes for performance
-- ════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_workflows_client ON customer_workflows(client_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON customer_workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflows_task ON customer_workflows(task_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_workflow ON workflow_events(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_events_type ON workflow_events(event_type);
CREATE INDEX IF NOT EXISTS idx_test_runs_workflow ON workflow_test_runs(workflow_id);

-- ════════════════════════════════════════════════════════════════
-- RLS: Client isolation (same pattern as existing tables)
-- ════════════════════════════════════════════════════════════════

ALTER TABLE customer_workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_test_runs ENABLE ROW LEVEL SECURITY;

-- Client policy: customers see only their own workflows
CREATE POLICY client_workflows_isolation ON customer_workflows
    FOR SELECT USING (client_id = current_setting('app.current_client_id', true)::integer);

-- Admin bypass
CREATE POLICY admin_workflows_all ON customer_workflows
    FOR ALL TO admin_role USING (true) WITH CHECK (true);

-- Events: client sees events for their workflows
CREATE POLICY client_events_isolation ON workflow_events
    FOR SELECT USING (
        workflow_id IN (
            SELECT id FROM customer_workflows 
            WHERE client_id = current_setting('app.current_client_id', true)::integer
        )
    );

-- Admin bypass for events
CREATE POLICY admin_events_all ON workflow_events
    FOR ALL TO admin_role USING (true) WITH CHECK (true);

-- Test runs: same pattern
CREATE POLICY client_testruns_isolation ON workflow_test_runs
    FOR SELECT USING (
        workflow_id IN (
            SELECT id FROM customer_workflows 
            WHERE client_id = current_setting('app.current_client_id', true)::integer
        )
    );

CREATE POLICY admin_testruns_all ON workflow_test_runs
    FOR ALL TO admin_role USING (true) WITH CHECK (true);

-- ════════════════════════════════════════════════════════════════
-- Migration: Mark existing tasks with workflow deliverables
-- Note: task_queue replaces tasks table in current schema
-- ════════════════════════════════════════════════════════════════

-- Check if tasks or task_queue table exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        -- Legacy tasks table exists
        INSERT INTO customer_workflows (
            client_id, task_id, service_type, workflow_name, 
            status, deployment_mode, backup_file_path, created_at
        )
        SELECT 
            t.client_id,
            t.id as task_id,
            'n8n' as service_type,
            COALESCE(t.display_name, t.task_type) as workflow_name,
            'deployed' as status,
            'shared' as deployment_mode,
            d.file_path as backup_file_path,
            t.created_at
        FROM tasks t
        JOIN deliverables d ON d.task_id = t.id
        WHERE d.file_name LIKE '%.json'
          AND t.status = 'completed'
          AND NOT EXISTS (
              SELECT 1 FROM customer_workflows cw WHERE cw.task_id = t.id
          )
        ON CONFLICT DO NOTHING;
    ELSIF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'task_queue') THEN
        -- task_queue table exists
        INSERT INTO customer_workflows (
            client_id, task_id, service_type, workflow_name, 
            status, deployment_mode, backup_file_path, created_at
        )
        SELECT 
            1 as client_id,  -- default client for migration
            t.id as task_id,
            'n8n' as service_type,
            COALESCE(t.display_name, t.task_type) as workflow_name,
            'deployed' as status,
            'shared' as deployment_mode,
            NULL as backup_file_path,
            t.created_at
        FROM task_queue t
        WHERE t.task_type LIKE '%n8n%'
          AND t.status = 'completed'
          AND NOT EXISTS (
              SELECT 1 FROM customer_workflows cw WHERE cw.task_id = t.id
          )
        ON CONFLICT DO NOTHING;
    END IF;
END $$;

-- Count migrated
SELECT COUNT(*) as migrated_workflows FROM customer_workflows;
