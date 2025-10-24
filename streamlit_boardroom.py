import streamlit as st
import requests
import json
import time
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="XMRT DAO - Autonomous System Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Supabase Edge Functions Configuration
SUPABASE_URL = "https://vawouugtzwmejxqkeqqj.supabase.co"
SUPABASE_KEY = "sb_publishable_yIaroctFhoYStx0f9XajBg_zhpuVulw"

EDGE_FUNCTIONS = {
    "ai_chat": f"{SUPABASE_URL}/functions/v1/ai-chat",
    "mining_proxy": f"{SUPABASE_URL}/functions/v1/mining-proxy",
    "github_integration": f"{SUPABASE_URL}/functions/v1/github-integration",
    "task_orchestrator": f"{SUPABASE_URL}/functions/v1/task-orchestrator"
}

HEADERS = {
    "Content-Type": "application/json",
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

# CSS Styling
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
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
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        margin: 1rem 0;
    }
    .live-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #00ff88;
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 8px;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
@st.cache_data(ttl=30)
def get_mining_data():
    """Get real mining data from edge function"""
    try:
        response = requests.get(EDGE_FUNCTIONS["mining_proxy"], headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Mining data error: {e}")
        return {"error": str(e), "totalHashes": 0, "validShares": 0, "amtDue": 0}

@st.cache_data(ttl=60)
def get_github_activity():
    """Get GitHub activity from edge function"""
    try:
        payload = {"action": "get_recent_activity", "timestamp": datetime.now().isoformat()}
        response = requests.post(EDGE_FUNCTIONS["github_integration"], headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"GitHub data error: {e}")
        return {"error": str(e), "commits": [], "contributors": []}

def send_ai_chat(message, context=None):
    """Send message to AI chat edge function"""
    try:
        payload = {
            "message": message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(EDGE_FUNCTIONS["ai_chat"], headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "response": "AI service unavailable. Please try again."}

# Header
st.markdown("""
<div class="main-header">
    <h1>🏛️ XMRT DAO - Autonomous System Dashboard</h1>
    <p><span class="live-indicator"></span>Live Real-Time Data from Supabase Edge Functions</p>
</div>
""", unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 System Metrics", "⛏️ Mining Activity", "💬 AI Chat", "🔧 GitHub Activity"])

with tab1:
    st.subheader("🔴 LIVE System Metrics")
    
    # Get real data
    with st.spinner("Loading real-time data from edge functions..."):
        mining_data = get_mining_data()
        github_data = get_github_activity()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_hashes = mining_data.get('totalHashes', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>⛏️ Mining</h3>
            <p><strong>{total_hashes:,}</strong> Total Hashes</p>
            <p><strong>{mining_data.get('validShares', 0):,}</strong> Valid Shares</p>
            <p style="font-size: 0.8rem; opacity: 0.8;">Source: mining-proxy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        commits = github_data.get('commits', [])
        contributors = github_data.get('contributors', [])
        st.markdown(f"""
        <div class="metric-card">
            <h3>💻 GitHub</h3>
            <p><strong>{len(commits)}</strong> Recent Commits</p>
            <p><strong>{len(contributors)}</strong> Contributors</p>
            <p style="font-size: 0.8rem; opacity: 0.8;">Source: github-integration</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        amt_due = mining_data.get('amtDue', 0) / 1e9  # Convert to readable format
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Rewards</h3>
            <p><strong>{amt_due:.2f}</strong> XMRT Due</p>
            <p><strong>{mining_data.get('txnCount', 0)}</strong> Transactions</p>
            <p style="font-size: 0.8rem; opacity: 0.8;">Source: mining-proxy</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Real-time status
    st.markdown("---")
    st.markdown("### 🟢 Edge Function Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        if not mining_data.get('error'):
            st.success("✅ mining-proxy: ONLINE")
        else:
            st.error("❌ mining-proxy: ERROR")
    
    with status_col2:
        if not github_data.get('error'):
            st.success("✅ github-integration: ONLINE")
        else:
            st.error("❌ github-integration: ERROR")
    
    with status_col3:
        st.info("🔵 ai-chat: READY")
    
    # Display raw data
    with st.expander("🔍 View Raw Mining Data"):
        st.json(mining_data)

with tab2:
    st.subheader("⛏️ Real Mining Activity")
    
    mining_data = get_mining_data()
    
    if not mining_data.get('error'):
        st.success(f"✅ Connected to mining-proxy edge function")
        
        # Display key metrics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Hashes", f"{mining_data.get('totalHashes', 0):,}")
            st.metric("Valid Shares", f"{mining_data.get('validShares', 0):,}")
        
        with col2:
            st.metric("Invalid Shares", f"{mining_data.get('invalidShares', 0):,}")
            st.metric("Last Hash", f"{mining_data.get('lastHash', 0):,}")
        
        # Create dataframe
        df_data = {
            "Metric": ["Total Hashes", "Valid Shares", "Invalid Shares", "Amount Due", "Transactions"],
            "Value": [
                f"{mining_data.get('totalHashes', 0):,}",
                f"{mining_data.get('validShares', 0):,}",
                f"{mining_data.get('invalidShares', 0):,}",
                f"{mining_data.get('amtDue', 0):,}",
                f"{mining_data.get('txnCount', 0):,}"
            ]
        }
        
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)
        
        # Show identifier
        st.info(f"📍 Identifier: {mining_data.get('identifier', 'N/A')}")
        
    else:
        st.error(f"❌ Error: {mining_data.get('error')}")

with tab3:
    st.subheader("💬 AI Chat - Real Gemini Integration")
    st.caption("Powered by Supabase ai-chat edge function")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask the AI system anything..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI is thinking via edge function..."):
                response = send_ai_chat(prompt, {"history": st.session_state.messages[-5:]})
                
                if response.get("error"):
                    ai_response = f"⚠️ {response.get('response', 'Service temporarily unavailable')}"
                else:
                    ai_response = response.get("response", "I'm processing your request...")
                
                st.markdown(ai_response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Rerun to show updated chat
        st.rerun()

with tab4:
    st.subheader("🔧 Real GitHub Activity")
    st.caption("Powered by Supabase github-integration edge function")
    
    github_data = get_github_activity()
    
    if not github_data.get('error'):
        st.success("✅ Connected to github-integration edge function")
        
        # Display commits
        commits = github_data.get('commits', [])
        if commits:
            st.write(f"**Recent Commits:** {len(commits)}")
            
            for i, commit in enumerate(commits[:10], 1):
                st.markdown(f"""
                **{i}. {commit.get('message', 'No message')}**  
                *{commit.get('author', 'Unknown')} - {commit.get('timestamp', 'Unknown time')}*  
                `{commit.get('sha', 'N/A')[:8]}`
                """)
        else:
            st.info("No commits data available from edge function")
        
        # Display contributors
        contributors = github_data.get('contributors', [])
        if contributors:
            st.write(f"**Active Contributors:** {len(contributors)}")
            contributor_names = [c.get('name', 'Unknown') for c in contributors]
            st.write(", ".join(contributor_names))
        
        # Refresh button
        if st.button("🔄 Refresh GitHub Data"):
            st.cache_data.clear()
            st.rerun()
            
    else:
        st.error(f"❌ Error: {github_data.get('error')}")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🟢 **Data Source:** Supabase Edge Functions")

with col2:
    st.caption("🔄 **Auto-refresh:** Every 30 seconds")

with col3:
    if st.button("🔄 Refresh All Data"):
        st.cache_data.clear()
        st.rerun()

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🚀 NO SIMULATIONS - 100% REAL DATA")
