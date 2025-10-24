# XMRT.io Real Ecosystem Setup Guide

## 🎯 Overview

This guide will help you transition from simulated data to real ecosystem activity using:
- **Supabase**: Real-time database for activity logging
- **GitHub API**: Real repository activity tracking
- **Gemini AI**: Real AI responses (no mocks)

## 📋 Prerequisites

1. **Supabase Account**: https://supabase.com
2. **GitHub Personal Access Token**: Already provided
3. **Google Gemini API Key**: https://makersuite.google.com/app/apikey

## 🔧 Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to https://supabase.com
2. Create a new project
3. Wait for it to provision (2-3 minutes)
4. Note your:
   - Project URL: `https://[project-id].supabase.co`
   - Anon Key: Found in Settings > API
   - Service Role Key: Found in Settings > API (keep secret!)

### 1.2 Create Database Tables

Go to SQL Editor in Supabase and run:

```sql
-- Ecosystem Activities Table
CREATE TABLE IF NOT EXISTS ecosystem_activities (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    activity_type TEXT NOT NULL,
    data JSONB,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_activities_timestamp 
    ON ecosystem_activities(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_activities_type 
    ON ecosystem_activities(activity_type);

-- Deployment Status Table
CREATE TABLE IF NOT EXISTS deployment_status (
    deployment TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    last_check TIMESTAMPTZ,
    metadata JSONB
);

-- AI Conversations Table
CREATE TABLE IF NOT EXISTS ai_conversations (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT,
    agent_type TEXT,
    message TEXT,
    response TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- System Metrics Table
CREATE TABLE IF NOT EXISTS system_metrics (
    id BIGSERIAL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC,
    unit TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    tags JSONB
);
```

### 1.3 Configure RLS (Optional but Recommended)

```sql
-- Enable Row Level Security
ALTER TABLE ecosystem_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE deployment_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;

-- Allow service role to do everything
CREATE POLICY "Service role bypass" ON ecosystem_activities
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role bypass" ON deployment_status
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role bypass" ON ai_conversations
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
```

## 🔑 Step 2: Get Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key (starts with `AIza...`)

## 📝 Step 3: Configure Streamlit Secrets

### 3.1 Local Development

Create `.streamlit/secrets.toml`:

```toml
[supabase]
url = "https://your-project-id.supabase.co"
key = "your-anon-key"
service_key = "your-service-role-key"

[github]
username = "DevGruGold"
token = "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"
repo = "XMRT.io"

[gemini]
api_key = "your-gemini-api-key"
model = "gemini-2.0-flash-exp"

[api]
render_url = "https://xmrt-ecosystem-0k8i.onrender.com"
xmrtnet_url = "https://xmrtnet-eliza.onrender.com"
dao_url = "https://xmrt-ecosystem-redis-langgraph.onrender.com"

[features]
enable_real_time = true
enable_github_integration = true
enable_ai_responses = true
enable_supabase_logging = true
```

### 3.2 Streamlit Cloud Deployment

1. Go to https://share.streamlit.io
2. Find your app settings
3. Click "Secrets" in the left sidebar
4. Paste the same TOML content (with your real values)
5. Click "Save"

## 🚀 Step 4: Deploy Updates

### 4.1 Update Local Repository

```bash
cd /path/to/XMRT.io

# Copy new files
cp streamlit_boardroom_real.py streamlit_boardroom.py
cp requirements_updated.txt requirements.txt
cp mcp_endpoints_real.py mcp_endpoints.py

# Create config directory if it doesn't exist
mkdir -p config
cp config/real_ecosystem_config.py config/

# Create .streamlit directory
mkdir -p .streamlit
# Add your secrets.toml here
```

### 4.2 Push to GitHub

```bash
git add .
git commit -m "🚀 Real Ecosystem Integration - Removed All Simulations"
git push origin main
```

This will automatically trigger:
- ✅ Streamlit Cloud redeployment
- ✅ Render service redeployment

### 4.3 Automated Deployment (Alternative)

Or use the automated script:

```bash
python deploy_updates.py
```

## 🔍 Step 5: Verify Deployment

### 5.1 Check Streamlit App

1. Visit: https://xmrtnet-test.streamlit.app/
2. Verify status indicators:
   - 🟢 Supabase Connected
   - 🟢 GitHub Connected
   - 🟢 Gemini AI Active

### 5.2 Test Real Features

1. **Chat with AI**: Send a message, verify real Gemini response
2. **GitHub Activity**: Click "Fetch Latest GitHub Activity"
3. **Activity Stream**: Click "Refresh Activity Stream" to see Supabase data

### 5.3 Check Render Deployment

Visit: https://xmrt-ecosystem-0k8i.onrender.com/

Should show service online.

## 🔧 Step 6: Environment Variables for Render

Add these environment variables in Render dashboard:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

GITHUB_TOKEN=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
GITHUB_USERNAME=DevGruGold
GITHUB_REPO=XMRT.io

GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.0-flash-exp

ENABLE_REAL_TIME=true
```

## 📊 Step 7: Monitor Real Activity

### View in Supabase

1. Go to Supabase Dashboard
2. Click "Table Editor"
3. Select `ecosystem_activities` table
4. Watch real-time activity as users interact!

### View in Streamlit

The dashboard now shows:
- Real AI conversations
- Real GitHub commits
- Real database activities
- Real system metrics

## 🐛 Troubleshooting

### Supabase Connection Failed

- Verify your URL and keys are correct
- Check RLS policies aren't blocking queries
- Try using service_key instead of anon key

### GitHub API Rate Limited

- The token has limited requests
- Wait an hour or use a different token
- Check token permissions include `repo` scope

### Gemini AI Not Responding

- Verify API key is valid
- Check you have API quota remaining
- Try a different model name

### Streamlit Secrets Not Loading

- Ensure file is at `.streamlit/secrets.toml`
- Check TOML syntax is valid
- Restart Streamlit app

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ All status indicators show green in dashboard
2. ✅ AI responses are contextual and detailed (not generic)
3. ✅ GitHub activity shows real commits
4. ✅ Activity stream in Supabase grows with each interaction
5. ✅ No "simulation" or "mock" messages appear

## 📚 Additional Resources

- [Supabase Docs](https://supabase.com/docs)
- [Streamlit Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Gemini API](https://ai.google.dev/docs)
- [PyGithub](https://pygithub.readthedocs.io/)

## 🆘 Support

If you encounter issues:

1. Check Streamlit logs in Cloud dashboard
2. Check Render logs in service dashboard
3. Verify all secrets are correctly configured
4. Ensure database tables were created

---

**Status**: Ready for production deployment with real ecosystem activity! 🚀
