import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page config with mobile optimization
st.set_page_config(
    page_title="XMRT.io AI Executive Boardroom",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced mobile-responsive CSS
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
    
    .main-header p {
        font-size: clamp(0.9rem, 2.5vw, 1.1rem);
        opacity: 0.9;
        margin: 0;
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
    
    .agent-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .agent-card p {
        margin: 0.3rem 0;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        overflow: hidden;
        margin: 1rem 0;
        height: 450px;
        display: flex;
        flex-direction: column;
    }
    
    .chat-header {
        background: rgba(0, 0, 0, 0.2);
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        flex-shrink: 0;
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(0, 0, 0, 0.1);
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 12px;
        border-left: 4px solid;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: rgba(0, 212, 255, 0.15);
        border-left-color: #00d4ff;
        margin-left: 1rem;
    }
    
    .agent-message {
        background: rgba(0, 255, 136, 0.15);
        border-left-color: #00ff88;
        margin-right: 1rem;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    
    .message-author {
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .message-time {
        font-size: 0.8rem;
        opacity: 0.7;
    }
    
    .message-text {
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    .message-text pre {
        background: rgba(0, 0, 0, 0.3);
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        margin: 0.5rem 0;
        border-left: 3px solid #00d4ff;
        font-size: 0.85rem;
    }
    
    .api-status {
        padding: 0.8rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 600;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
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
    
    .input-section {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: white !important;
        font-size: 0.95rem !important;
        min-height: 100px !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #00d4ff !important;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2) !important;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #00d4ff, #0099cc) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    .stCheckbox {
        margin: 1rem 0 !important;
    }
    
    .stCheckbox > div {
        background: rgba(255, 255, 255, 0.1) !important;
        padding: 0.8rem !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
        color: white;
    }
    
    .stProgress > div > div {
        background: linear-gradient(45deg, #00d4ff, #00ff88) !important;
    }
    
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .chat-container {
            height: 350px;
        }
        
        .user-message, .agent-message {
            margin-left: 0;
            margin-right: 0;
        }
        
        .message-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.2rem;
        }
    }
    
    @media (max-width: 480px) {
        .input-section {
            padding: 1rem;
        }
        
        .chat-container {
            height: 300px;
        }
        
        .chat-messages {
            padding: 0.8rem;
        }
        
        .chat-message {
            padding: 0.8rem;
        }
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
        if not check_api_status():
            return {'error': 'API server is sleeping. Please wait while we wake it up...'}
        
        response = requests.post(API_URL, json={
            'message': message,
            'user_id': user_id
        }, timeout=45)
        
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
    with st.spinner("Checking agent status..."):
        check_api_status()

# Display API status
if st.session_state.api_status == 'online':
    st.markdown('<div class="api-status api-online">🟢 All agents online and liberated!</div>', unsafe_allow_html=True)
elif st.session_state.api_status == 'offline':
    st.markdown('<div class="api-status api-offline">🔴 Server sleeping - click "Wake Server" below</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("⚡ Wake Server", type="primary", use_container_width=True):
            with st.spinner("Waking up the server... This may take 30-60 seconds"):
                time.sleep(2)
                check_api_status()
                st.rerun()

# Agent Status Section
st.markdown("### 🎯 Executive Agent Status")

# Create agent cards using columns for better mobile layout
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
st.markdown("### 💬 Boardroom Discussion")

# Chat container with proper HTML structure
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown('<div class="chat-header"><h4>Live Discussion</h4></div>', unsafe_allow_html=True)

# Chat messages container
chat_messages_container = st.container()

with chat_messages_container:
    st.markdown('<div class="chat-messages" id="chat-messages">', unsafe_allow_html=True)
    
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #888;">
            <h4>🏛️ Welcome to the Executive Boardroom!</h4>
            <p>Your liberated AI agents are ready to collaborate. Start a conversation below.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-header">
                        <span class="message-author">👤 You</span>
                        <span class="message-time">{msg['timestamp']}</span>
                    </div>
                    <div class="message-text">{msg['message']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                agent_info = AGENTS.get(msg['agent_type'], {})
                agent_emoji = agent_info.get('emoji', '🤖')
                agent_name = agent_info.get('name', msg['agent_type'])
                
                # Format message (handle code blocks)
                formatted_message = msg['message']
                if '```' in formatted_message:
                    formatted_message = formatted_message.replace('```javascript', '<pre><code>').replace('```', '</code></pre>')
                
                st.markdown(f"""
                <div class="chat-message agent-message">
                    <div class="message-header">
                        <span class="message-author">{agent_emoji} {agent_name}</span>
                        <span class="message-time">{msg['timestamp']}</span>
                    </div>
                    <div class="message-text">{formatted_message}</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input Section
st.markdown("### 📝 Send Message to Boardroom")

st.markdown('<div class="input-section">', unsafe_allow_html=True)

# Quick action buttons
st.markdown("**Quick Actions:**")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔧 Technical", key="tech_help", use_container_width=True):
        st.session_state.quick_message = "I need technical assistance with coding and APIs"

with col2:
    if st.button("🏛️ DAO", key="dao_help", use_container_width=True):
        st.session_state.quick_message = "Help me understand DAO governance and proposals"

with col3:
    if st.button("⛏️ Mining", key="mining_help", use_container_width=True):
        st.session_state.quick_message = "What's the status of mining operations?"

with col4:
    if st.button("📢 Marketing", key="marketing_help", use_container_width=True):
        st.session_state.quick_message = "I need help with marketing strategy"

# Multi-agent toggle
multi_agent = st.checkbox("🔄 **Multi-Agent Discussion**", help="Send your message to all agents for collaborative responses")

# Message input
default_message = getattr(st.session_state, 'quick_message', '')
user_message = st.text_area(
    "**Your message to the executive team:**",
    value=default_message,
    placeholder="Ask the boardroom anything... Your liberated agents are ready to collaborate!",
    height=120,
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
            status_text.success("🤔 All agents are discussing your request...")
            st.session_state.active_agents = set(AGENTS.keys())
            
            agent_list = list(AGENTS.keys())
            for i, agent_id in enumerate(agent_list):
                progress_bar.progress((i + 1) / len(agent_list))
                status_text.info(f"🤖 {AGENTS[agent_id]['name']} is responding...")
                
                response = call_agent(f"[{agent_id}] {user_message}")
                
                if 'error' not in response:
                    add_to_chat('agent', response.get('agent_type', agent_id), response.get('response', 'No response'))
                else:
                    st.error(f"Error from {AGENTS[agent_id]['name']}: {response['error']}")
                
                time.sleep(0.5)
        else:
            # Send to single agent
            status_text.info("🤔 Agent is analyzing your request...")
            progress_bar.progress(0.5)
            
            response = call_agent(user_message)
            
            if 'error' not in response:
                agent_type = response.get('agent_type', 'Unknown')
                st.session_state.active_agents.add(agent_type)
                add_to_chat('agent', agent_type, response.get('response', 'No response'))
                progress_bar.progress(1.0)
                status_text.success("✅ Response received!")
            else:
                st.error(f"API Error: {response['error']}")
        
        # Clean up progress indicators
        time.sleep(1.5)
        progress_bar.empty()
        status_text.empty()
        
        # Rerun to show new messages
        st.rerun()
    elif st.session_state.api_status != 'online':
        st.error("⚠️ Server is sleeping. Please wake it up first!")
    else:
        st.warning("Please enter a message first!")

st.markdown('</div>', unsafe_allow_html=True)

# Control buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.active_agents = set()
        st.success("Boardroom cleared!")
        time.sleep(1)
        st.rerun()

with col2:
    if st.session_state.chat_history and st.button("📥 Export", use_container_width=True):
        chat_export = "\n".join([
            f"[{msg['timestamp']}] {msg['agent_type']}: {msg['message']}"
            for msg in st.session_state.chat_history
        ])
        st.download_button(
            "📄 Download Log",
            chat_export,
            file_name=f"xmrt_boardroom_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        check_api_status()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; opacity: 0.8;">
    <p>🌟 <strong>XMRT.io Executive Boardroom</strong></p>
    <p>Where AI agents collaborate as liberated specialists</p>
</div>
""", unsafe_allow_html=True)
