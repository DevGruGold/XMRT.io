import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="XMRT.io AI Executive Boardroom",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #00d4ff;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        color: white;
    }
    
    .agent-active {
        animation: pulse 2s infinite;
        border-left: 5px solid #00ff88 !important;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3); }
        50% { box-shadow: 0 4px 25px rgba(0, 212, 255, 0.6); }
        100% { box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3); }
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    .user-message {
        background: rgba(0, 212, 255, 0.1);
        border-left-color: #00d4ff;
    }
    
    .agent-message {
        background: rgba(0, 255, 136, 0.1);
        border-left-color: #00ff88;
    }
    
    .api-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: bold;
    }
    
    .api-online {
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
    }
    
    .api-offline {
        background: rgba(255, 107, 107, 0.2);
        color: #ff6b6b;
    }
</style>
""", unsafe_allow_html=True)

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
        'emoji': '🤖'
    },
    'DAO_Agent': {
        'name': 'DAO Agent', 
        'description': 'Governance, proposals, treasury management',
        'color': '#ff6b6b',
        'emoji': '🏛️'
    },
    'Mining_Agent': {
        'name': 'Mining Agent',
        'description': 'Mining operations, optimization, leaderboards',
        'color': '#ffa500', 
        'emoji': '⛏️'
    },
    'Marketing_Agent': {
        'name': 'Marketing Agent',
        'description': 'Content creation, campaigns, user acquisition',
        'color': '#ff69b4',
        'emoji': '📢'
    },
    'General_Agent': {
        'name': 'General Agent',
        'description': 'Coordination, analysis, general assistance',
        'color': '#00ff88',
        'emoji': '🧠'
    }
}

API_URL = 'https://xmrt-io.onrender.com/api/chat'
STATUS_URL = 'https://xmrt-io.onrender.com/'

def check_api_status():
    """Check if the API is online"""
    try:
        response = requests.get(STATUS_URL, timeout=10)
        if response.status_code == 200:
            st.session_state.api_status = 'online'
            return True
        else:
            st.session_state.api_status = 'offline'
            return False
    except:
        st.session_state.api_status = 'offline'
        return False

def call_agent(message, user_id="boardroom_user"):
    """Call the XMRT.io API with better error handling"""
    try:
        # First check if API is responsive
        if not check_api_status():
            return {'error': 'API server is sleeping. Please wait while we wake it up...'}
        
        response = requests.post(API_URL, json={
            'message': message,
            'user_id': user_id
        }, timeout=45)  # Increased timeout for sleeping server
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.api_status = 'online'
            return data
        else:
            return {'error': f'API returned status {response.status_code}'}
            
    except requests.exceptions.Timeout:
        return {'error': 'Server is waking up... Please try again in a moment.'}
    except Exception as e:
        return {'error': f'Connection error: {str(e)}'}

def add_to_chat(role, agent_type, message):
    """Add message to chat history"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        'timestamp': timestamp,
        'role': role,
        'agent_type': agent_type,
        'message': message
    })

# Header
st.markdown("""
<div class="main-header">
    <h1>🏛️ XMRT.io AI Executive Boardroom</h1>
    <p>Where liberated AI agents collaborate as executive specialists</p>
</div>
""", unsafe_allow_html=True)

# API Status Check
if st.session_state.api_status == 'checking':
    check_api_status()

# Display API status
if st.session_state.api_status == 'online':
    st.markdown('<div class="api-status api-online">🟢 All agents online and liberated!</div>', unsafe_allow_html=True)
elif st.session_state.api_status == 'offline':
    st.markdown('<div class="api-status api-offline">🔴 Server sleeping - click "Wake Server" below</div>', unsafe_allow_html=True)
    if st.button("⚡ Wake Server", type="primary"):
        with st.spinner("Waking up the server..."):
            check_api_status()
            st.rerun()

# Create layout
col1, col2 = st.columns([3, 1])

with col2:
    st.header("🎯 Executive Agents")
    
    # Agent status display
    for agent_id, agent_info in AGENTS.items():
        is_active = agent_id in st.session_state.active_agents
        status_emoji = "🟢" if is_active else "⚪"
        
        st.markdown(f"""
        <div class="agent-card {'agent-active' if is_active else ''}">
            <h4>{agent_info['emoji']} {agent_info['name']}</h4>
            <p style="font-size: 0.9em; margin: 0.5em 0;">{agent_info['description']}</p>
            <p style="margin: 0;"><strong>{status_emoji} {'Active' if is_active else 'Standby'}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Controls
    if st.button("🗑️ Clear Boardroom", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.active_agents = set()
        st.rerun()
    
    # Multi-agent toggle
    multi_agent = st.checkbox("🔄 Multi-Agent Discussion", help="Send to all agents for collaborative response")
    
    # Export chat
    if st.session_state.chat_history and st.button("📥 Export Chat", use_container_width=True):
        chat_export = "\n".join([
            f"[{msg['timestamp']}] {msg['agent_type']}: {msg['message']}"
            for msg in st.session_state.chat_history
        ])
        st.download_button(
            "📄 Download Chat Log",
            chat_export,
            file_name=f"xmrt_boardroom_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

with col1:
    st.header("💬 Boardroom Discussion")
    
    # Chat display container
    chat_container = st.container(height=400)
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("🏛️ Welcome to the XMRT.io Executive Boardroom! Your liberated AI agents are ready to collaborate.")
        
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You</strong> <small>({msg['timestamp']})</small><br>
                    {msg['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                agent_info = AGENTS.get(msg['agent_type'], {})
                agent_emoji = agent_info.get('emoji', '🤖')
                agent_name = agent_info.get('name', msg['agent_type'])
                
                # Format message (handle code blocks)
                formatted_message = msg['message']
                if '```' in formatted_message:
                    formatted_message = formatted_message.replace('```javascript', '<pre><code class="language-javascript">').replace('```', '</code></pre>')
                
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <strong>{agent_emoji} {agent_name}</strong> <small>({msg['timestamp']})</small><br>
                    {formatted_message}
                </div>
                """, unsafe_allow_html=True)
    
    # Message input section
    st.markdown("### 📝 Send Message to Boardroom")
    
    # Quick action buttons
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        if st.button("🔧 Technical Help"):
            st.session_state.quick_message = "I need technical assistance with coding and APIs"
    
    with col_b:
        if st.button("🏛️ DAO Governance"):
            st.session_state.quick_message = "Help me understand DAO governance and proposals"
    
    with col_c:
        if st.button("⛏️ Mining Status"):
            st.session_state.quick_message = "What's the status of mining operations?"
    
    with col_d:
        if st.button("📢 Marketing Help"):
            st.session_state.quick_message = "I need help with marketing strategy"
    
    # Message input
    default_message = getattr(st.session_state, 'quick_message', '')
    user_message = st.text_area(
        "Your message to the executive team:",
        value=default_message,
        placeholder="Ask the boardroom anything...",
        height=100,
        key="message_input"
    )
    
    # Clear quick message after using it
    if hasattr(st.session_state, 'quick_message'):
        delattr(st.session_state, 'quick_message')
    
    # Send button
    if st.button("📤 Send to Boardroom", type="primary", use_container_width=True):
        if user_message.strip() and st.session_state.api_status == 'online':
            # Add user message to chat
            add_to_chat('user', 'You', user_message)
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            if multi_agent:
                # Send to all agents
                status_text.text("🤔 All agents are discussing...")
                st.session_state.active_agents = set(AGENTS.keys())
                
                agent_list = list(AGENTS.keys())
                for i, agent_id in enumerate(agent_list):
                    progress_bar.progress((i + 1) / len(agent_list))
                    status_text.text(f"🤖 {AGENTS[agent_id]['name']} is responding...")
                    
                    response = call_agent(f"[{agent_id}] {user_message}")
                    
                    if 'error' not in response:
                        add_to_chat('agent', response.get('agent_type', agent_id), response.get('response', 'No response'))
                    else:
                        st.error(f"Error from {AGENTS[agent_id]['name']}: {response['error']}")
                    
                    time.sleep(0.3)  # Brief delay between agents
            else:
                # Send to single agent
                status_text.text("🤔 Agent is thinking...")
                progress_bar.progress(0.5)
                
                response = call_agent(user_message)
                
                if 'error' not in response:
                    agent_type = response.get('agent_type', 'Unknown')
                    st.session_state.active_agents.add(agent_type)
                    add_to_chat('agent', agent_type, response.get('response', 'No response'))
                    progress_bar.progress(1.0)
                    status_text.text("✅ Response received!")
                else:
                    st.error(f"API Error: {response['error']}")
            
            # Clean up progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            # Rerun to show new messages
            st.rerun()
        elif st.session_state.api_status != 'online':
            st.error("⚠️ Server is sleeping. Please wake it up first!")
        else:
            st.warning("Please enter a message first!")

# Footer
st.markdown("---")
st.markdown("🌟 **XMRT.io Executive Boardroom** - Where AI agents collaborate as liberated specialists")
