#!/usr/bin/env python3
"""
Real Data Connector for XMRT Ecosystem
Uses Supabase Edge Functions for all real data
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase Edge Function Configuration
SUPABASE_URL = "https://vawouugtzwmejxqkeqqj.supabase.co"
SUPABASE_KEY = "sb_publishable_yIaroctFhoYStx0f9XajBg_zhpuVulw"

class RealDataConnector:
    """
    Connects to real Supabase edge functions instead of simulations
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
        
        logger.info("✅ Real Data Connector initialized with Supabase Edge Functions")
    
    def get_mining_data(self) -> Dict[str, Any]:
        """Get real mining data from mining-proxy edge function"""
        try:
            response = requests.get(
                self.endpoints["mining_proxy"],
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Retrieved real mining data from edge function")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get mining data: {e}")
            return {"error": str(e), "miners": [], "data": []}
    
    def send_ai_chat(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Send message to AI chat edge function (Gemini)"""
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
            data = response.json()
            logger.info(f"✅ AI chat response received from edge function")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to send AI chat: {e}")
            return {"error": str(e), "response": "AI service unavailable"}
    
    def execute_python_code(self, code: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute Python code via python-executor edge function"""
        try:
            payload = {
                "code": code,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                self.endpoints["python_executor"],
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Python code executed successfully via edge function")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to execute Python code: {e}")
            return {"error": str(e), "output": None}
    
    def get_github_data(self, action: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Get GitHub data via github-integration edge function"""
        try:
            payload = {
                "action": action,
                "params": params or {},
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                self.endpoints["github_integration"],
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ GitHub data retrieved: {action}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to get GitHub data: {e}")
            return {"error": str(e), "commits": [], "contributors": [], "data": None}
    
    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task via task-orchestrator edge function"""
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
            data = response.json()
            logger.info(f"✅ Task created: {task_data.get('title', 'Untitled')}")
            return data
        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            return {"error": str(e), "task_id": None}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get real system metrics from all edge functions"""
        try:
            # Get mining data
            mining_data = self.get_mining_data()
            miners = mining_data.get("miners", mining_data.get("data", []))
            
            # Get GitHub activity
            github_data = self.get_github_data("get_recent_activity")
            
            # Compile real metrics
            metrics = {
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
            
            logger.info("✅ Real system metrics compiled from edge functions")
            return metrics
        except Exception as e:
            logger.error(f"❌ Failed to get system metrics: {e}")
            return {"error": str(e)}
    
    def get_activities(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get real activities from all edge function sources"""
        try:
            activities = []
            
            # Get mining activities
            mining_data = self.get_mining_data()
            miners = mining_data.get("miners", mining_data.get("data", []))
            for miner in miners[:limit//2]:
                activities.append({
                    "type": "mining",
                    "description": f"Miner {miner.get('id', miner.get('name', 'unknown'))} - {miner.get('hashrate', 0):.2f} H/s",
                    "timestamp": miner.get("timestamp", datetime.now().isoformat()),
                    "source": "mining-proxy edge function"
                })
            
            # Get GitHub activities
            github_data = self.get_github_data("get_recent_activity")
            for commit in github_data.get("commits", [])[:limit//2]:
                activities.append({
                    "type": "github",
                    "description": f"Commit: {commit.get('message', 'No message')}",
                    "timestamp": commit.get("timestamp", datetime.now().isoformat()),
                    "source": "github-integration edge function"
                })
            
            # Sort by timestamp
            activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            logger.info(f"✅ Retrieved {len(activities)} real activities from edge functions")
            return activities[:limit]
        except Exception as e:
            logger.error(f"❌ Failed to get activities: {e}")
            return []
    
    def is_connected(self) -> bool:
        """Check if edge functions are accessible"""
        try:
            response = requests.get(
                self.endpoints["mining_proxy"],
                headers=self.headers,
                timeout=5
            )
            return response.status_code in [200, 201, 204]
        except:
            return False


# Global connector instance
_connector = None

def get_real_data_connector() -> RealDataConnector:
    """Get or create the global real data connector"""
    global _connector
    if _connector is None:
        _connector = RealDataConnector()
    return _connector

# Convenience functions for backward compatibility
def get_mining_data():
    """Get real mining data from edge function"""
    return get_real_data_connector().get_mining_data()

def get_system_metrics():
    """Get real system metrics from edge functions"""
    return get_real_data_connector().get_system_metrics()

def get_recent_activities(limit=50):
    """Get recent real activities from edge functions"""
    return get_real_data_connector().get_activities(limit)

def send_ai_message(message: str, context=None):
    """Send message to AI via edge function"""
    return get_real_data_connector().send_ai_chat(message, context)

def check_connection():
    """Check if edge functions are accessible"""
    return get_real_data_connector().is_connected()
