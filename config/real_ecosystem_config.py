#!/usr/bin/env python3
"""
Real Ecosystem Configuration and Integration
Uses Supabase Edge Functions for all real data operations
"""

import os
import logging
import requests
from typing import Dict, Optional, Any, List
import streamlit as st
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase Edge Function Configuration
# Supabase Edge Function Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vawouugtzwmejxqkeqqj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_KEY", "sb_publishable_yIaroctFhoYStx0f9XajBg_zhpuVulw"))


class RealEcosystemConfig:
    """
    Real ecosystem configuration manager
    Uses Supabase edge functions for all operations
    """
    
    def __init__(self):
        self.base_url = SUPABASE_URL
        self.api_key = SUPABASE_KEY
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Edge function endpoints
        self.endpoints = {
            "ai_chat": f"{self.base_url}/functions/v1/ai-chat",
            "mining_proxy": f"{self.base_url}/functions/v1/mining-proxy",
            "python_executor": f"{self.base_url}/functions/v1/python-executor",
            "github_integration": f"{self.base_url}/functions/v1/github-integration",
            "task_orchestrator": f"{self.base_url}/functions/v1/task-orchestrator"
        }
        
        self._test_connections()
    
    def _test_connections(self):
        """Test edge function connections"""
        try:
            response = requests.get(
                self.endpoints["mining_proxy"],
                headers=self.headers,
                timeout=5
            )
            if response.status_code in [200, 201, 204]:
                logger.info("✅ Edge functions connected successfully")
            else:
                logger.warning(f"⚠️  Edge functions returned status: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Edge function connection test failed: {e}")
    
    def get_mining_data(self) -> Dict[str, Any]:
        """Get real mining data from edge function"""
        try:
            response = requests.get(
                self.endpoints["mining_proxy"],
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get mining data: {e}")
            return {"error": str(e), "miners": []}
    
    def send_ai_chat(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send message to AI via edge function"""
        try:
            payload = {
                "message": message,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                self.endpoints["ai_chat"],
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ AI chat failed: {e}")
            return {"error": str(e), "response": "AI service unavailable"}
    
    def get_github_activity(self, action: str = "get_recent_activity") -> Dict[str, Any]:
        """Get GitHub activity via edge function"""
        try:
            payload = {
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                self.endpoints["github_integration"],
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ GitHub activity fetch failed: {e}")
            return {"error": str(e), "commits": [], "contributors": []}
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task via edge function"""
        try:
            payload = {
                **task_data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                self.endpoints["task_orchestrator"],
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Task creation failed: {e}")
            return {"error": str(e), "task_id": None}
    
    def log_activity(self, activity_type: str, data: Dict[str, Any]) -> bool:
        """
        Log activity via edge function
        """
        try:
            # Use task orchestrator to log activities
            activity_record = {
                'title': f'{activity_type} Activity',
                'activity_type': activity_type,
                'data': data,
                'source': 'streamlit_boardroom'
            }
            
            result = self.create_task(activity_record)
            if not result.get('error'):
                logger.info(f"✅ Activity logged: {activity_type}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to log activity: {e}")
            return False
    
    def get_recent_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch real activities from edge functions
        """
        try:
            activities = []
            
            # Get mining activities
            mining_data = self.get_mining_data()
            miners = mining_data.get("miners", mining_data.get("data", []))
            for miner in miners[:limit//2]:
                activities.append({
                    "type": "mining",
                    "description": f"Miner {miner.get('id', 'unknown')} - {miner.get('hashrate', 0)} H/s",
                    "timestamp": miner.get("timestamp", datetime.now().isoformat()),
                    "source": "mining-proxy"
                })
            
            # Get GitHub activities
            github_data = self.get_github_activity()
            for commit in github_data.get("commits", [])[:limit//2]:
                activities.append({
                    "type": "github",
                    "description": f"Commit: {commit.get('message', 'No message')}",
                    "timestamp": commit.get("timestamp", datetime.now().isoformat()),
                    "source": "github-integration"
                })
            
            activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch activities: {e}")
            return []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics from edge functions"""
        try:
            mining_data = self.get_mining_data()
            miners = mining_data.get("miners", mining_data.get("data", []))
            
            github_data = self.get_github_activity()
            
            return {
                "mining": {
                    "active_miners": len(miners),
                    "total_hashrate": sum(m.get("hashrate", 0) for m in miners),
                    "last_updated": datetime.now().isoformat()
                },
                "github": {
                    "commits": len(github_data.get("commits", [])),
                    "contributors": len(github_data.get("contributors", [])),
                    "last_updated": datetime.now().isoformat()
                },
                "system": {
                    "status": "operational",
                    "data_source": "supabase_edge_functions",
                    "last_updated": datetime.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ Failed to get system metrics: {e}")
            return {"error": str(e)}
    
    def is_online(self) -> bool:
        """Check if edge functions are online"""
        try:
            response = requests.get(
                self.endpoints["mining_proxy"],
                headers=self.headers,
                timeout=5
            )
            return response.status_code in [200, 201, 204]
        except:
            return False


# Global instance
_config = None

def get_ecosystem_config() -> RealEcosystemConfig:
    """Get or create the global ecosystem config"""
    global _config
    if _config is None:
        _config = RealEcosystemConfig()
    return _config
