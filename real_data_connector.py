#!/usr/bin/env python3
"""
Real Data Connector for XMRT Ecosystem
Replaces all simulations with real Supabase, GitHub, and Gemini integrations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealDataConnector:
    """
    Connects to real data sources instead of simulations
    """
    
    def __init__(self):
        self.supabase_client = None
        self.github_client = None
        self.gemini_client = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize all real connections using Streamlit secrets"""
        try:
            # Supabase connection
            if 'supabase' in st.secrets:
                from supabase import create_client
                supabase_url = st.secrets["supabase"]["url"]
                supabase_key = st.secrets["supabase"]["key"]
                self.supabase_client = create_client(supabase_url, supabase_key)
                logger.info("✅ Supabase connected")
            
            # GitHub connection
            if 'github' in st.secrets:
                from github import Github
                github_token = st.secrets["github"]["token"]
                self.github_client = Github(github_token)
                logger.info("✅ GitHub connected")
            
            # Gemini connection
            if 'gemini' in st.secrets:
                import google.generativeai as genai
                gemini_key = st.secrets["gemini"]["api_key"]
                genai.configure(api_key=gemini_key)
                self.gemini_client = genai.GenerativeModel('gemini-pro')
                logger.info("✅ Gemini AI connected")
                
        except Exception as e:
            logger.error(f"❌ Connection initialization failed: {e}")
    
    def get_real_agent_activities(self) -> List[Dict]:
        """Get real agent activities from Supabase"""
        try:
            if self.supabase_client:
                response = self.supabase_client.table('agent_activities').select('*').order('created_at', desc=True).limit(10).execute()
                return response.data
            else:
                return self._fallback_activities()
        except Exception as e:
            logger.error(f"Error fetching real activities: {e}")
            return self._fallback_activities()
    
    def get_real_github_activity(self) -> List[Dict]:
        """Get real GitHub repository activity"""
        try:
            if self.github_client:
                repo = self.github_client.get_repo("DevGruGold/XMRT.io")
                commits = repo.get_commits()[:10]
                
                activities = []
                for commit in commits:
                    activities.append({
                        'type': 'github_commit',
                        'message': commit.commit.message,
                        'author': commit.commit.author.name,
                        'timestamp': commit.commit.author.date.isoformat(),
                        'sha': commit.sha[:7]
                    })
                return activities
            else:
                return []
        except Exception as e:
            logger.error(f"Error fetching GitHub activity: {e}")
            return []
    
    def get_ai_response(self, prompt: str, context: str = "") -> str:
        """Get real AI response from Gemini"""
        try:
            if self.gemini_client:
                full_prompt = f"{context}\n\nUser: {prompt}\n\nAssistant:"
                response = self.gemini_client.generate_content(full_prompt)
                return response.text
            else:
                return "AI not available - please configure Gemini API key"
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return f"Error: {str(e)}"
    
    def log_activity(self, agent_name: str, activity_type: str, description: str, metadata: Dict = None):
        """Log real activity to Supabase"""
        try:
            if self.supabase_client:
                data = {
                    'agent_name': agent_name,
                    'activity_type': activity_type,
                    'description': description,
                    'metadata': json.dumps(metadata) if metadata else '{}',
                    'created_at': datetime.now().isoformat()
                }
                self.supabase_client.table('agent_activities').insert(data).execute()
                logger.info(f"✅ Activity logged: {agent_name} - {activity_type}")
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    def _fallback_activities(self) -> List[Dict]:
        """Fallback activities when database is not available"""
        return [
            {
                'agent_name': 'System',
                'activity_type': 'status',
                'description': 'Waiting for real data connections...',
                'created_at': datetime.now().isoformat()
            }
        ]

# Singleton instance
_connector = None

def get_connector() -> RealDataConnector:
    """Get or create the real data connector instance"""
    global _connector
    if _connector is None:
        _connector = RealDataConnector()
    return _connector
