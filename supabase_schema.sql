-- XMRT Ecosystem Database Schema
-- Run this in your Supabase SQL Editor

-- Agent Activities Table
CREATE TABLE IF NOT EXISTS agent_activities (
    id BIGSERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_activities_created_at ON agent_activities(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_activities_agent_name ON agent_activities(agent_name);

-- System Metrics Table
CREATE TABLE IF NOT EXISTS system_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_type TEXT NOT NULL,
    metric_value NUMERIC,
    metadata JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_metrics_recorded_at ON system_metrics(recorded_at DESC);

-- Agent Communications Table
CREATE TABLE IF NOT EXISTS agent_communications (
    id BIGSERIAL PRIMARY KEY,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    message_type TEXT NOT NULL,
    content TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_comms_created_at ON agent_communications(created_at DESC);

-- User Interactions Table
CREATE TABLE IF NOT EXISTS user_interactions (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT,
    interaction_type TEXT NOT NULL,
    content TEXT,
    ai_response TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_interactions_created_at ON user_interactions(created_at DESC);

-- Enable Row Level Security
ALTER TABLE agent_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_communications ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated access
CREATE POLICY "Enable read access for all users" ON agent_activities FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON agent_activities FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON system_metrics FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON system_metrics FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON agent_communications FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON agent_communications FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON user_interactions FOR SELECT USING (true);
CREATE POLICY "Enable insert for all users" ON user_interactions FOR INSERT WITH CHECK (true);
