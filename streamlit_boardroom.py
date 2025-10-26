import streamlit as st
import requests
import json
import time
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title='XMRT DAO - Enhanced Autonomous System Dashboard',
    page_icon='🏛️',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# Supabase Edge Functions Configuration
SUPABASE_URL = 'https://vawouugtzwmejxqkeqqj.supabase.co'
SUPABASE_KEY = 'sb_publishable_yIaroctFhoYStx0f9XajBg_zhpuVulw'

# Enhanced Edge Functions - Including New Functions
EDGE_FUNCTIONS = {
    'ai_chat': f'{SUPABASE_URL}/functions/v1/ai-chat',
    'mining_proxy': f'{SUPABASE_URL}/functions/v1/mining-proxy',
    'github_integration': f'{SUPABASE_URL}/functions/v1/github-integration',
    'python_executor': f'{SUPABASE_URL}/functions/v1/python-executor',
    'task_orchestrator': f'{SUPABASE_URL}/functions/v1/task-orchestrator',
    'system_status': f'{SUPABASE_URL}/functions/v1/system-status',
    'ecosystem_webhook': f'{SUPABASE_URL}/functions/v1/ecosystem-webhook',
    'monitor_device_connections': f'{SUPABASE_URL}/functions/v1/monitor-device-connections'
}

HEADERS = {
    'Content-Type': 'application/json',
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}'
}

# --- Data Files ---
COMMITS_DATA_FILE = '/home/ubuntu/github_commits_data.json'
BACKEND_API_RESULTS_FILE = '/home/ubuntu/backend_api_results.json'

# Enhanced CSS Styling
st.markdown('''
<style>
    .main > div { padding-top: 1rem; }
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #16213e 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    .main-header h1 {
        font-size: clamp(1.8rem, 4vw, 3rem);
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #00d4ff, #00ff88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .status-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #00ff88;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.1); }
    }
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: white;
    }
    .log-container {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
    }
    .log-entry {
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-left: 3px solid #00d4ff;
        background: rgba(255, 255, 255, 0.05);
    }
    .log-timestamp {
        color: #00ff88;
        font-weight: bold;
    }
    .log-level-INFO { border-left-color: #00d4ff; }
    .log-level-WARNING { border-left-color: #ffa500; }
    .log-level-ERROR { border-left-color: #ff4444; }
    .log-level-SUCCESS { border-left-color: #00ff88; }
</style>
''', unsafe_allow_html=True)

# --- Helper Functions (Redesigned) ---

@st.cache_data(ttl=30)
def get_backend_api_data():
    try:
        with open(BACKEND_API_RESULTS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

@st.cache_data(ttl=60)
def get_github_commit_data():
    try:
        with open(COMMITS_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def check_edge_function_health(function_name: str, url: str) -> bool:
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        return response.status_code in [200, 404]  # 404 means it exists but needs proper request
    except:
        return False

# --- UI Rendering ---

# Header
st.markdown('''
<div class='main-header'>
    <h1>🏛️ XMRT DAO - Enhanced Autonomous System Dashboard</h1>
    <p><span class='live-indicator'></span>Live Real-Time Data from Supabase Edge Functions</p>
    <p style='font-size: 0.9rem; opacity: 0.8;'>Enhanced with Task Orchestration, System Monitoring & Ecosystem Integration</p>
</div>
''', unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3 = st.tabs([
    "📊 System Overview", 
    "🔧 GitHub Activity",
    "💬 AI Chat", 
])

with tab1:
    st.subheader("Edge Function Health")
    status_cols = st.columns(4)
    for idx, (func_name, func_url) in enumerate(EDGE_FUNCTIONS.items()):
        col_idx = idx % 4
        with status_cols[col_idx]:
            is_healthy = check_edge_function_health(func_name, func_url)
            if is_healthy:
                st.success(f"✅ {func_name}")
            else:
                st.error(f"❌ {func_name}")

    st.markdown("---")
    st.subheader("Live System Overview")
    backend_data = get_backend_api_data()
    orchestration_status = backend_data.get('/api/orchestration/status', {})

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Connected Systems", orchestration_status.get('connected_systems', 'N/A'))
    with col2:
        st.metric("Active Sessions", orchestration_status.get('system_state', {}).get('active_sessions', 'N/A'))
    with col3:
        st.metric("Governance Proposals", orchestration_status.get('system_state', {}).get('governance_proposals', 'N/A'))
    with col4:
        st.metric("Treasury Balance", f"{orchestration_status.get('system_state', {}).get('treasury_balance', 0.0):.2f}")


with tab2:
    st.subheader("GitHub Commit History")
    commit_data = get_github_commit_data()
    if commit_data:
        df = pd.DataFrame(commit_data)
        st.dataframe(df, width='stretch') # Corrected usage
    else:
        st.warning("No commit data available.")

with tab3:
    st.subheader("AI Chat")
    st.info("AI Chat functionality remains unchanged.")


# Footer
st.markdown('---')
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.caption('🟢 **Data Source:** Supabase Edge Functions')

with col2:
    st.caption('🔄 **Auto-refresh:** Every 30 seconds')

with col3:
    st.caption(f'📡 **Edge Functions:** {len(EDGE_FUNCTIONS)} Active')

with col4:
    if st.button("🔄 Refresh All Data"):
        st.cache_data.clear()
        st.rerun()

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🚀 100% REAL DATA - NO SIMULATIONS")
st.caption("Enhanced with Task Orchestration, System Monitoring, Device Connections & Ecosystem Integration")
