import streamlit as st
import requests
import json
import time
import pandas as pd
from datetime import datetime
from real_data_connector import get_connector

# Page config
st.set_page_config(
    page_title="XMRT DAO - Autonomous System Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize real data connector
connector = get_connector()

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
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-active {
        background-color: #00ff88;
        box-shadow: 0 0 10px #00ff88;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .activity-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00d4ff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 XMRT DAO - Autonomous System</h1>
    <p><span class="status-indicator status-active"></span>Real-time Ecosystem Activity</p>
</div>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔴 Live Agent Activities")
    
    # Get real activities
    activities = connector.get_real_agent_activities()
    
    if activities:
        for activity in activities:
            agent_name = activity.get('agent_name', 'Unknown')
            activity_type = activity.get('activity_type', 'general')
            description = activity.get('description', '')
            timestamp = activity.get('created_at', datetime.now().isoformat())
            
            st.markdown(f"""
            <div class="activity-card">
                <strong>{agent_name}</strong> - {activity_type}<br>
                {description}<br>
                <small style="opacity: 0.7;">{timestamp}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Connecting to real-time data sources...")
    
    # GitHub Activity
    st.subheader("💻 Recent GitHub Activity")
    github_activities = connector.get_real_github_activity()
    
    if github_activities:
        for commit in github_activities:
            st.markdown(f"""
            <div class="activity-card">
                <strong>Commit {commit['sha']}</strong> by {commit['author']}<br>
                {commit['message']}<br>
                <small style="opacity: 0.7;">{commit['timestamp']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Loading GitHub activity...")

with col2:
    st.subheader("🎯 System Status")
    
    # Display connection status
    status_items = []
    if connector.supabase_client:
        status_items.append("✅ Supabase Connected")
    else:
        status_items.append("⚠️ Supabase Not Connected")
    
    if connector.github_client:
        status_items.append("✅ GitHub Connected")
    else:
        status_items.append("⚠️ GitHub Not Connected")
    
    if connector.gemini_client:
        status_items.append("✅ Gemini AI Connected")
    else:
        status_items.append("⚠️ Gemini AI Not Connected")
    
    for item in status_items:
        st.markdown(item)
    
    st.markdown("---")
    
    # AI Chat Interface
    st.subheader("💬 Chat with AI")
    user_message = st.text_input("Ask the autonomous system:")
    
    if st.button("Send") and user_message:
        with st.spinner("Thinking..."):
            response = connector.get_ai_response(
                user_message,
                context="You are an AI agent in the XMRT autonomous ecosystem."
            )
            st.markdown(f"**AI Response:**\n{response}")
            
            # Log this interaction
            connector.log_activity(
                agent_name="User",
                activity_type="chat",
                description=f"User asked: {user_message}",
                metadata={'response': response}
            )

# Auto-refresh
st.markdown("---")
if st.button("🔄 Refresh Data"):
    st.rerun()

# Auto-refresh every 30 seconds
time.sleep(30)
st.rerun()
