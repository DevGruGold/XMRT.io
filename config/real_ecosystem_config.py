#!/usr/bin/env python3
"""
Real Ecosystem Configuration and Integration
Replaces all simulations with real connections to Supabase, GitHub, and Gemini
"""

import os
import logging
from typing import Dict, Optional, Any
import streamlit as st
from datetime import datetime
from github import Github
from supabase import create_client, Client
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealEcosystemConfig:
    """
    Real ecosystem configuration manager
    Handles all real connections to external services
    """
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.github: Optional[Github] = None
        self.gemini_model = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all real services"""
        try:
            # Initialize Supabase
            if hasattr(st, 'secrets') and 'supabase' in st.secrets:
                supabase_url = st.secrets['supabase']['url']
                supabase_key = st.secrets['supabase']['key']
                self.supabase = create_client(supabase_url, supabase_key)
                logger.info("✅ Supabase connected")
            else:
                logger.warning("⚠️  Supabase credentials not found in secrets")
            
            # Initialize GitHub
            if hasattr(st, 'secrets') and 'github' in st.secrets:
                github_token = st.secrets['github']['token']
                self.github = Github(github_token)
                logger.info("✅ GitHub connected")
            else:
                logger.warning("⚠️  GitHub credentials not found in secrets")
            
            # Initialize Gemini
            if hasattr(st, 'secrets') and 'gemini' in st.secrets:
                genai.configure(api_key=st.secrets['gemini']['api_key'])
                model_name = st.secrets['gemini'].get('model', 'gemini-2.0-flash-exp')
                self.gemini_model = genai.GenerativeModel(model_name)
                logger.info("✅ Gemini AI connected")
            else:
                logger.warning("⚠️  Gemini credentials not found in secrets")
                
        except Exception as e:
            logger.error(f"❌ Service initialization error: {e}")
    
    def log_activity(self, activity_type: str, data: Dict[str, Any]) -> bool:
        """
        Log real activity to Supabase
        """
        if not self.supabase:
            logger.warning("Supabase not available, skipping activity log")
            return False
        
        try:
            activity_record = {
                'timestamp': datetime.now().isoformat(),
                'activity_type': activity_type,
                'data': data,
                'source': 'streamlit_boardroom'
            }
            
            result = self.supabase.table('ecosystem_activities').insert(activity_record).execute()
            logger.info(f"✅ Activity logged: {activity_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to log activity: {e}")
            return False
    
    def get_recent_activities(self, limit: int = 50):
        """
        Fetch real activities from Supabase
        """
        if not self.supabase:
            return []
        
        try:
            result = self.supabase.table('ecosystem_activities')\
                .select('*')\
                .order('timestamp', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch activities: {e}")
            return []
    
    def get_github_activity(self, repo_name: str = "XMRT.io"):
        """
        Fetch real GitHub activity
        """
        if not self.github:
            return None
        
        try:
            username = st.secrets['github'].get('username', 'DevGruGold')
            repo = self.github.get_repo(f"{username}/{repo_name}")
            
            # Get recent commits
            commits = list(repo.get_commits()[:10])
            
            # Get open issues
            issues = list(repo.get_issues(state='open')[:10])
            
            # Get recent pull requests
            pulls = list(repo.get_pulls(state='open')[:10])
            
            activity_data = {
                'commits': [{
                    'sha': c.sha[:7],
                    'message': c.commit.message,
                    'author': c.commit.author.name,
                    'date': c.commit.author.date.isoformat()
                } for c in commits],
                'open_issues': len(issues),
                'open_pulls': len(pulls),
                'last_updated': datetime.now().isoformat()
            }
            
            # Log this activity to Supabase
            self.log_activity('github_sync', activity_data)
            
            return activity_data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch GitHub activity: {e}")
            return None
    
    def generate_ai_response(self, message: str, agent_context: str = "eliza") -> Dict:
        """
        Generate real AI response using Gemini
        """
        if not self.gemini_model:
            return {
                'success': False,
                'error': 'Gemini AI not configured'
            }
        
        try:
            # Build context-aware prompt
            agent_personas = {
                'eliza': "You are Eliza, a helpful and friendly AI assistant in the XMRT ecosystem. Respond naturally and helpfully.",
                'dao_governor': "You are the DAO Governor, responsible for governance and decision-making. Be authoritative and diplomatic.",
                'defi_specialist': "You are the DeFi Specialist, an expert in decentralized finance. Be technical and precise.",
                'community_manager': "You are the Community Manager, enthusiastic about growing and engaging the community.",
                'security_guardian': "You are the Security Guardian, focused on safety and risk management. Be cautious and protective."
            }
            
            prompt = f"{agent_personas.get(agent_context, agent_personas['eliza'])}\n\nUser message: {message}\n\nRespond naturally:"
            
            response = self.gemini_model.generate_content(prompt)
            
            response_data = {
                'success': True,
                'response': response.text,
                'agent_type': agent_context,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log AI interaction
            self.log_activity('ai_interaction', {
                'agent': agent_context,
                'user_message': message,
                'ai_response': response.text[:200]  # Store preview
            })
            
            return response_data
            
        except Exception as e:
            logger.error(f"❌ AI response generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_deployment_status(self, deployment: str, status: str):
        """
        Update deployment status in Supabase
        """
        if not self.supabase:
            return False
        
        try:
            status_record = {
                'deployment': deployment,
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'last_check': datetime.now().isoformat()
            }
            
            # Upsert deployment status
            result = self.supabase.table('deployment_status').upsert(
                status_record,
                on_conflict='deployment'
            ).execute()
            
            logger.info(f"✅ Deployment status updated: {deployment} -> {status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update deployment status: {e}")
            return False
    
    def create_supabase_tables(self):
        """
        SQL commands to create necessary Supabase tables
        Run these in your Supabase SQL editor
        """
        sql_commands = """
        -- Ecosystem Activities Table
        CREATE TABLE IF NOT EXISTS ecosystem_activities (
            id BIGSERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            activity_type TEXT NOT NULL,
            data JSONB,
            source TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Index for faster queries
        CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON ecosystem_activities(timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_activities_type ON ecosystem_activities(activity_type);
        
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
        
        -- Enable Row Level Security (optional but recommended)
        ALTER TABLE ecosystem_activities ENABLE ROW LEVEL SECURITY;
        ALTER TABLE deployment_status ENABLE ROW LEVEL SECURITY;
        ALTER TABLE ai_conversations ENABLE ROW LEVEL SECURITY;
        ALTER TABLE system_metrics ENABLE ROW LEVEL SECURITY;
        
        -- Create policies for authenticated access
        CREATE POLICY "Enable read access for authenticated users" ON ecosystem_activities
            FOR SELECT USING (auth.role() = 'authenticated');
        
        CREATE POLICY "Enable insert for authenticated users" ON ecosystem_activities
            FOR INSERT WITH CHECK (auth.role() = 'authenticated');
        """
        
        return sql_commands


# Global instance
_ecosystem_config = None

def get_ecosystem_config() -> RealEcosystemConfig:
    """
    Get or create ecosystem config singleton
    """
    global _ecosystem_config
    if _ecosystem_config is None:
        _ecosystem_config = RealEcosystemConfig()
    return _ecosystem_config
