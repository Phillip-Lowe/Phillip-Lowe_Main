-- Systack CRM Database Schema
-- PostgreSQL 15+

-- Drop tables if they exist (for clean rebuild)
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS leads CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

-- =============================================
-- clients
-- =============================================
CREATE TABLE clients (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    industry        VARCHAR(100),
    website         VARCHAR(255),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_clients_name ON clients (name);
CREATE INDEX idx_clients_industry ON clients (industry);
CREATE INDEX idx_clients_created_at ON clients (created_at DESC);

-- =============================================
-- leads
-- =============================================
CREATE TABLE leads (
    id              SERIAL PRIMARY KEY,
    client_id       INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(255),
    phone           VARCHAR(50),
    source          VARCHAR(100),
    status          VARCHAR(50) DEFAULT 'new',
    notes           TEXT,
    score           INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_leads_client_id ON leads (client_id);
CREATE INDEX idx_leads_email ON leads (email);
CREATE INDEX idx_leads_status ON leads (status);
CREATE INDEX idx_leads_score ON leads (score DESC);
CREATE INDEX idx_leads_created_at ON leads (created_at DESC);

-- =============================================
-- contacts
-- =============================================
CREATE TABLE contacts (
    id              SERIAL PRIMARY KEY,
    lead_id         INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    email           VARCHAR(255),
    phone           VARCHAR(50),
    role            VARCHAR(100),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contacts_lead_id ON contacts (lead_id);
CREATE INDEX idx_contacts_email ON contacts (email);
CREATE INDEX idx_contacts_role ON contacts (role);
CREATE INDEX idx_contacts_created_at ON contacts (created_at DESC);

-- =============================================
-- invoices
-- =============================================
CREATE TABLE invoices (
    id              SERIAL PRIMARY KEY,
    client_id       INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    invoice_number  VARCHAR(100) NOT NULL UNIQUE,
    total           NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    date            DATE NOT NULL DEFAULT CURRENT_DATE,
    vendor          VARCHAR(255),
    line_items      JSONB DEFAULT '[]'::jsonb,
    status          VARCHAR(50) DEFAULT 'draft',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoices_client_id ON invoices (client_id);
CREATE INDEX idx_invoices_invoice_number ON invoices (invoice_number);
CREATE INDEX idx_invoices_status ON invoices (status);
CREATE INDEX idx_invoices_date ON invoices (date DESC);
CREATE INDEX idx_invoices_created_at ON invoices (created_at DESC);

-- GIN index for JSONB line_items queries
CREATE INDEX idx_invoices_line_items ON invoices USING GIN (line_items);

-- =============================================
-- Updated-at trigger helper
-- =============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER invoices_updated_at
    BEFORE UPDATE ON invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
