# XMRT Ecosystem - Real Integration Setup Guide

## 🎯 Overview

This guide will help you set up real data connections for the XMRT autonomous ecosystem, replacing all simulations with actual Supabase, GitHub, and Gemini AI integrations.

**Updated:** 2025-10-24 20:06:34

## 🚀 Quick Start

### 1. Supabase Setup

1. Go to [Supabase](https://supabase.com) and create a new project
2. Once created, get your credentials:
   - Project URL: Found in Settings > API
   - Anon/Public Key: Found in Settings > API
3. Run the SQL schema in your Supabase SQL Editor (see `supabase_schema.sql`)

### 2. GitHub Token Setup

1. Go to GitHub Settings > Developer Settings > Personal Access Tokens
2. Generate a new token (classic) with these scopes:
   - `repo` (full control of private repositories)
   - `read:org` (read organization data)
3. Copy the token (you'll only see it once!)

### 3. Gemini AI Setup

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 4. Configure Streamlit Secrets

For **Streamlit Cloud** deployment:

1. Go to your app dashboard: https://share.streamlit.io/
2. Click on your app: `xmrtnet-test`
3. Go to Settings > Secrets
4. Add the following configuration:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-supabase-anon-key"

[github]
token = "github_pat_YOUR_TOKEN_HERE"
username = "DevGruGold"
repo = "XMRT.io"

[gemini]
api_key = "your-gemini-api-key"
```

5. Save and your app will automatically restart

### 5. Configure Render Deployment

For **Render** deployment (https://xmrt-ecosystem-0k8i.onrender.com/):

1. Go to your Render dashboard
2. Select your service
3. Go to Environment
4. Add environment variables:
   - `SUPABASE_URL` = your Supabase URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `GITHUB_TOKEN` = your GitHub token
   - `GEMINI_API_KEY` = your Gemini API key
5. Save and trigger a manual deploy

## 📊 Database Schema

The Supabase database includes these tables:

### `agent_activities`
Tracks all agent activities in real-time
- `id`: Unique identifier
- `agent_name`: Name of the agent
- `activity_type`: Type of activity (chat, action, analysis, etc.)
- `description`: Activity description
- `metadata`: Additional JSON data
- `created_at`: Timestamp

### `system_metrics`
Stores system performance metrics
- `id`: Unique identifier
- `metric_type`: Type of metric
- `metric_value`: Numeric value
- `metadata`: Additional context
- `recorded_at`: Timestamp

### `agent_communications`
Logs inter-agent communications
- `id`: Unique identifier
- `from_agent`: Sender agent
- `to_agent`: Recipient agent
- `message_type`: Type of message
- `content`: Message content
- `metadata`: Additional data
- `created_at`: Timestamp

### `user_interactions`
Records user interactions with the system
- `id`: Unique identifier
- `user_id`: User identifier
- `interaction_type`: Type of interaction
- `content`: User input
- `ai_response`: AI response
- `metadata`: Additional context
- `created_at`: Timestamp

## 🔧 Architecture

### Real Data Flow

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│  Streamlit Dashboard    │
│  (xmrtnet-test)         │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Real Data Connector    │
│  - Supabase Client      │
│  - GitHub Client        │
│  - Gemini AI Client     │
└──┬────┬─────┬───────────┘
   │    │     │
   ▼    ▼     ▼
┌────┐ ┌────┐ ┌────┐
│ DB │ │ GH │ │ AI │
└────┘ └────┘ └────┘
```

## 📝 File Structure

```
XMRT.io/
├── real_data_connector.py      # Main connector for all real integrations
├── streamlit_boardroom.py      # Updated dashboard using real data
├── .streamlit/
│   └── secrets.toml.template   # Template for secrets
├── requirements.txt            # Updated with new dependencies
└── README_SETUP.md            # This file
```

## 🧪 Testing the Integration

After setup, you should see:

1. **Real Agent Activities**: Live data from Supabase
2. **GitHub Commits**: Recent commits from your repository
3. **AI Responses**: Real responses from Gemini AI
4. **Connection Status**: Green checkmarks for all services

## 🔍 Troubleshooting

### Supabase Connection Issues
- Verify your URL format: `https://xxx.supabase.co`
- Check that anon key is correct
- Ensure RLS policies are set up correctly

### GitHub Connection Issues
- Verify token has correct permissions
- Check token hasn't expired
- Ensure repository name is correct

### Gemini AI Issues
- Verify API key is valid
- Check you have API quota available
- Ensure you're using a supported region

## 📈 Monitoring

Monitor your real-time system:

1. **Supabase Dashboard**: View database records
2. **Streamlit Logs**: Check application logs
3. **Render Logs**: Monitor server logs
4. **GitHub Actions**: Track deployments

## 🎉 Success Indicators

Your real integration is working when you see:

- ✅ All connection status indicators are green
- ✅ Real-time activities appear in the dashboard
- ✅ GitHub commits are displayed correctly
- ✅ AI chat provides real responses
- ✅ Activities are logged to Supabase database

## 🔐 Security Best Practices

1. **Never commit secrets** to the repository
2. Use environment variables for all credentials
3. Rotate tokens periodically
4. Use read-only tokens where possible
5. Enable RLS in Supabase for production

## 📞 Support

If you encounter issues:

1. Check Streamlit logs for errors
2. Verify all secrets are correctly configured
3. Test each integration individually
4. Review Supabase logs for database errors

## 🚀 Next Steps

After successful setup:

1. Monitor real-time activities
2. Add custom agent behaviors
3. Extend database schema as needed
4. Implement additional AI features
5. Scale up based on usage

---

**Last Updated:** 2025-10-24 20:06:34
**Version:** 1.0.0 - Real Integrations
