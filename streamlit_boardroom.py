import streamlit as st
import requests
import json
import time
import pandas as pd
from datetime import datetime
import sys
import os

# Add config directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

from real_ecosystem_config import get_ecosystem_config

# Page config with mobile optimization
st.set_page_config(
    page_title="XMRT DAO - Autonomous System Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced mobile-responsive CSS (keeping existing styles)
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #16213e 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        font-size: clamp(1.5rem, 4vw, 2.5rem);
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #00d4ff;
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 0.8rem 0;
    }
    
    .agent-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .agent-active {
        border-left-color: #00ff88 !important;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3); }
        50% { box-shadow: 0 8px 25px rgba(0, 255, 136, 0.6); }
    }
    
    .api-status {
        padding: 0.8rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .api-online {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
        border: 1px solid rgba(0, 255, 136, 0.3);
    }
    
    .api-offline {
        background: rgba(255, 107, 107, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize ecosystem config
ecosystem = get_ecosystem_config()

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'active_agents' not in st.session_state:
    st.session_state.active_agents = set()
if 'api_status' not in st.session_state:
    st.session_state.api_status = 'checking'

# Agent configurations
AGENTS = {
    'Technical_Agent': {
        'name': 'Technical Agent',
        'description': 'Code generation, APIs, debugging, system architecture',
        'color': '#00d4ff',
        'emoji': '🤖',
        'context': 'eliza'
    },
    'DAO_Agent': {
        'name': 'DAO Agent', 
        'description': 'Governance, proposals, treasury management',
        'color': '#ff6b6b',
        'emoji': '🏛️',
        'context': 'dao_governor'
    },
    'Mining_Agent': {
        'name': 'Mining Agent',
        'description': 'Mining operations, optimization, leaderboards',
        'color': '#ffa500', 
        'emoji': '⛏️',
        'context': 'defi_specialist'
    },
    'Marketing_Agent': {
        'name': 'Marketing Agent',
        'description': 'Content creation, campaigns, user acquisition',
        'color': '#ff69b4',
        'emoji': '📢',
        'context': 'community_manager'
    },
    'Security_Agent': {
        'name': 'Security Agent',
        'description': 'Security monitoring, risk assessment, protection',
        'color': '#00ff88',
        'emoji': '🛡️',
        'context': 'security_guardian'
    }
}

API_URL = 'https://xmrt-ecosystem-0k8i.onrender.com/api/chat'
STATUS_URL = 'https://xmrt-ecosystem-0k8i.onrender.com/'

def check_api_status():
    """Check if the API is online"""
    try:
        response = requests.get(STATUS_URL, timeout=10)
        if response.status_code == 200:
            st.session_state.api_status = 'online'
            ecosystem.update_deployment_status('render', 'online')
            return True
        else:
            st.session_state.api_status = 'offline'
            ecosystem.update_deployment_status('render', 'offline')
            return False
    except:
        st.session_state.api_status = 'offline'
        return False

def call_agent_real(message, agent_context="eliza"):
    """Call real AI agent using Gemini integration"""
    try:
        # Use real Gemini AI
        response = ecosystem.generate_ai_response(message, agent_context)
        
        if response['success']:
            st.session_state.api_status = 'online'
            return response
        else:
            return {'error': f'AI generation failed: {response.get("error", "Unknown error")}'}
            
    except Exception as e:
        return {'error': f'Connection error: {str(e)}'}

def add_to_chat(role, agent_type, message):
    """Add message to chat history and log to Supabase"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    chat_entry = {
        'timestamp': timestamp,
        'role': role,
        'agent_type': agent_type,
        'message': message
    }
    st.session_state.chat_history.append(chat_entry)
    
    # Log to real database
    ecosystem.log_activity('chat_message', chat_entry)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏛️ XMRT DAO - Autonomous System Dashboard</h1>
    <p>Real-time AI ecosystem with GitHub, Supabase & Gemini integration</p>
</div>
""", unsafe_allow_html=True)

# System Status Section
st.markdown("### 🔄 Real System Status")

col1, col2, col3 = st.columns(3)

with col1:
    if ecosystem.supabase:
        st.markdown('<div class="api-status api-online">🟢 Supabase Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status api-offline">🔴 Supabase Offline</div>', unsafe_allow_html=True)

with col2:
    if ecosystem.github:
        st.markdown('<div class="api-status api-online">🟢 GitHub Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status api-offline">🔴 GitHub Offline</div>', unsafe_allow_html=True)

with col3:
    if ecosystem.gemini_model:
        st.markdown('<div class="api-status api-online">🟢 Gemini AI Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status api-offline">🔴 Gemini AI Offline</div>', unsafe_allow_html=True)

# GitHub Activity Section
if ecosystem.github:
    with st.expander("📊 Real GitHub Activity", expanded=False):
        if st.button("🔄 Fetch Latest GitHub Activity"):
            with st.spinner("Fetching real GitHub data..."):
                github_data = ecosystem.get_github_activity()
                if github_data:
                    st.success("✅ GitHub data fetched successfully!")
                    
                    st.markdown("**Recent Commits:**")
                    for commit in github_data['commits'][:5]:
                        st.markdown(f"- `{commit['sha']}` - {commit['message'][:80]} by {commit['author']}")
                    
                    st.metric("Open Issues", github_data['open_issues'])
                    st.metric("Open Pull Requests", github_data['open_pulls'])
                else:
                    st.error("Failed to fetch GitHub activity")

# Agent Status Section
st.markdown("### 🎯 AI Agent Status")

col1, col2 = st.columns(2)
agents_list = list(AGENTS.items())

for i, (agent_id, agent_info) in enumerate(agents_list):
    is_active = agent_id in st.session_state.active_agents
    status_emoji = "🟢" if is_active else "⚪"
    
    target_col = col1 if i % 2 == 0 else col2
    
    with target_col:
        st.markdown(f"""
        <div class="agent-card {'agent-active' if is_active else ''}">
            <h4>{agent_info['emoji']} {agent_info['name']}</h4>
            <p>{agent_info['description']}</p>
            <p><strong>{status_emoji} {'Active' if is_active else 'Standby'}</strong></p>
        </div>
        """, unsafe_allow_html=True)

# Chat Section
st.markdown("### 💬 Real-Time AI Chat")

# Display chat history
for msg in st.session_state.chat_history[-20:]:  # Show last 20 messages
    if msg['role'] == 'user':
        st.chat_message("user").write(f"{msg['message']}")
    else:
        agent_info = AGENTS.get(msg['agent_type'], {})
        agent_emoji = agent_info.get('emoji', '🤖')
        st.chat_message("assistant", avatar=agent_emoji).write(f"{msg['message']}")

# Message input
user_message = st.chat_input("Ask the AI agents anything...")

if user_message:
    # Add user message to chat
    add_to_chat('user', 'You', user_message)
    st.chat_message("user").write(user_message)
    
    # Show progress
    with st.spinner("AI is thinking..."):
        # Determine which agent should respond based on message content
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['govern', 'dao', 'proposal', 'vote']):
            agent_id = 'DAO_Agent'
        elif any(word in message_lower for word in ['defi', 'mining', 'yield', 'stake']):
            agent_id = 'Mining_Agent'
        elif any(word in message_lower for word in ['market', 'campaign', 'community', 'grow']):
            agent_id = 'Marketing_Agent'
        elif any(word in message_lower for word in ['security', 'risk', 'audit', 'safe']):
            agent_id = 'Security_Agent'
        else:
            agent_id = 'Technical_Agent'
        
        agent_info = AGENTS[agent_id]
        agent_context = agent_info['context']
        
        # Get real AI response
        response = call_agent_real(user_message, agent_context)
        
        if 'error' not in response:
            st.session_state.active_agents.add(agent_id)
            add_to_chat('agent', agent_id, response.get('response', 'No response'))
            st.chat_message("assistant", avatar=agent_info['emoji']).write(response.get('response'))
        else:
            st.error(f"Error: {response['error']}")
    
    st.rerun()

# Real-Time Activity Stream
st.markdown("### ⚡ Real-Time Ecosystem Activity")

if st.button("🔄 Refresh Activity Stream"):
    with st.spinner("Fetching real activities from Supabase..."):
        activities = ecosystem.get_recent_activities(limit=20)
        
        if activities:
            df = pd.DataFrame(activities)
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Display in a nice format
            st.dataframe(
                df[['timestamp', 'activity_type', 'source']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No activities recorded yet. Start chatting to create activity!")

# Supabase Setup Instructions
with st.expander("🛠️ Setup Instructions", expanded=False):
    st.markdown("""
    ### Setting up Real Ecosystem Integration
    
    #### 1. Supabase Setup
    ```sql
    -- Run this in your Supabase SQL Editor:
    """)
    
    st.code(ecosystem.create_supabase_tables(), language='sql')
    
    st.markdown("""
    #### 2. Streamlit Secrets
    Create `.streamlit/secrets.toml` with:
    ```toml
    [supabase]
    url = "your-supabase-url"
    key = "your-supabase-anon-key"
    
    [github]
    username = "DevGruGold"
    token = "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"
    repo = "XMRT.io"
    
    [gemini]
    api_key = "your-gemini-api-key"
    model = "gemini-2.0-flash-exp"
    ```
    
    #### 3. Deploy to Streamlit Cloud
    - Push code to GitHub
    - Connect your Streamlit Cloud app
    - Add secrets in Streamlit Cloud dashboard
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; opacity: 0.8;">
    <p>🌟 <strong>XMRT DAO Autonomous System</strong></p>
    <p>Powered by Real AI, GitHub & Supabase</p>
</div>
""", unsafe_allow_html=True)
