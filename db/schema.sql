-- MODUS 100 Process Intelligence Engine
-- Database schema (PostgreSQL)

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS processes (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,          -- e.g. Merchandising, Fulfillment, Marketing
    description TEXT,
    status TEXT DEFAULT 'pending',   -- pending | analyzed | failed
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- One-to-one structured intelligence per process
CREATE TABLE IF NOT EXISTS process_analysis (
    id SERIAL PRIMARY KEY,
    process_id INTEGER REFERENCES processes(id) ON DELETE CASCADE UNIQUE,
    business_purpose TEXT,
    key_activities TEXT,
    current_challenges TEXT,
    ai_opportunity TEXT,
    automation_potential TEXT,       -- Low | Medium | High
    human_involvement TEXT,
    technologies TEXT,               -- comma separated / json array as text
    business_benefit TEXT,
    risks TEXT,
    rationale TEXT,                  -- short "why we concluded this"
    confidence TEXT DEFAULT 'grounded', -- grounded | insufficient_evidence
    created_at TIMESTAMP DEFAULT NOW()
);

-- Raw evidence / research snippets backing an analysis
CREATE TABLE IF NOT EXISTS evidence (
    id SERIAL PRIMARY KEY,
    process_id INTEGER REFERENCES processes(id) ON DELETE CASCADE,
    source_title TEXT,
    source_url TEXT,
    snippet TEXT,
    retrieved_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_processes_org ON processes(organization_id);
CREATE INDEX IF NOT EXISTS idx_processes_category ON processes(category);
CREATE INDEX IF NOT EXISTS idx_analysis_automation ON process_analysis(automation_potential);
CREATE INDEX IF NOT EXISTS idx_evidence_process ON evidence(process_id);
