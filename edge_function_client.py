"""
Enhanced Edge Function Client
Provides unified interface to all Supabase Edge Functions with proper error handling and logging
"""

import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.logger import edge_logger

class EdgeFunctionClient:
    """Unified client for all XMRT Supabase Edge Functions"""
    
    def __init__(self, supabase_url: str, api_key: str):
        self.supabase_url = supabase_url.rstrip('/')
        self.api_key = api_key
        
        self.headers = {
            "Content-Type": "application/json",
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}"
        }
        
        # Define all edge functions
        self.functions = {
            "ai_chat": f"{self.supabase_url}/functions/v1/ai-chat",
            "mining_proxy": f"{self.supabase_url}/functions/v1/mining-proxy",
            "github_integration": f"{self.supabase_url}/functions/v1/github-integration",
            "python_executor": f"{self.supabase_url}/functions/v1/python-executor",
            "task_orchestrator": f"{self.supabase_url}/functions/v1/task-orchestrator",
            "system_status": f"{self.supabase_url}/functions/v1/system-status",
            "ecosystem_webhook": f"{self.supabase_url}/functions/v1/ecosystem-webhook",
            "monitor_device_connections": f"{self.supabase_url}/functions/v1/monitor-device-connections"
        }
        
        edge_logger.info("EdgeFunctionClient initialized", functions=list(self.functions.keys()))
    
    def _call(self, function_name: str, method: str = "GET", payload: Optional[Dict[str, Any]] = None, 
              timeout: int = 30) -> Dict[str, Any]:
        """
        Make a call to an edge function with proper error handling
        
        Args:
            function_name: Name of the edge function
            method: HTTP method (GET, POST, etc.)
            payload: Request payload for POST requests
            timeout: Request timeout in seconds
        
        Returns:
            Response data or error dict
        """
        if function_name not in self.functions:
            error_msg = f"Unknown edge function: {function_name}"
            edge_logger.error(error_msg, available=list(self.functions.keys()))
            return {"error": error_msg, "success": False}
        
        url = self.functions[function_name]
        start_time = time.time()
        
        try:
            edge_logger.debug(f"Calling {function_name}", method=method, url=url)
            
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=timeout)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=payload, timeout=timeout)
            else:
                return {"error": f"Unsupported method: {method}", "success": False}
            
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            # Log the call
            edge_logger.edge_function_call(
                function_name=function_name,
                status=f"{response.status_code}",
                duration=duration,
                method=method
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            duration = (time.time() - start_time) * 1000
            edge_logger.error(f"Timeout calling {function_name}", duration=duration, timeout=timeout)
            return {"error": f"Request timeout after {timeout}s", "success": False}
        
        except requests.exceptions.RequestException as e:
            duration = (time.time() - start_time) * 1000
            edge_logger.error(f"Request error calling {function_name}", error=str(e), duration=duration)
            return {"error": str(e), "success": False}
        
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            edge_logger.error(f"Unexpected error calling {function_name}", error=str(e), duration=duration)
            return {"error": f"Unexpected error: {str(e)}", "success": False}
    
    # AI Chat Functions
    def send_ai_chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send message to AI chat"""
        payload = {
            "message": message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        return self._call("ai_chat", method="POST", payload=payload)
    
    # Mining Functions
    def get_mining_data(self) -> Dict[str, Any]:
        """Get real-time mining data"""
        return self._call("mining_proxy", method="GET")
    
    # GitHub Functions
    def get_github_activity(self, action: str = "get_recent_activity") -> Dict[str, Any]:
        """Get GitHub activity"""
        payload = {
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("github_integration", method="POST", payload=payload)
    
    def get_github_repo_info(self, repo: str) -> Dict[str, Any]:
        """Get specific repository information"""
        payload = {
            "action": "get_repo_info",
            "repo": repo,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("github_integration", method="POST", payload=payload)
    
    # Python Executor Functions
    def execute_python(self, code: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute Python code"""
        payload = {
            "code": code,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        return self._call("python_executor", method="POST", payload=payload)
    
    # Task Orchestrator Functions
    def create_task(self, title: str, description: str, priority: str = "medium", 
                   category: str = "general", **kwargs) -> Dict[str, Any]:
        """Create a new task"""
        payload = {
            "action": "create",
            "title": title,
            "description": description,
            "priority": priority,
            "category": category,
            "status": "pending",
            "timestamp": datetime.now().isoformat(),
            **kwargs
        }
        return self._call("task_orchestrator", method="POST", payload=payload)
    
    def get_tasks(self, status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get tasks with optional filtering"""
        payload = {
            "action": "list",
            "status": status,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("task_orchestrator", method="POST", payload=payload)
    
    def update_task(self, task_id: str, **updates) -> Dict[str, Any]:
        """Update an existing task"""
        payload = {
            "action": "update",
            "task_id": task_id,
            "updates": updates,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("task_orchestrator", method="POST", payload=payload)
    
    # System Status Functions
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return self._call("system_status", method="GET")
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a specific service"""
        payload = {
            "service": service_name,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("system_status", method="POST", payload=payload)
    
    # Ecosystem Webhook Functions
    def trigger_webhook(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger an ecosystem webhook"""
        payload = {
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("ecosystem_webhook", method="POST", payload=payload)
    
    def register_webhook_listener(self, webhook_url: str, event_types: List[str]) -> Dict[str, Any]:
        """Register a webhook listener"""
        payload = {
            "action": "register",
            "webhook_url": webhook_url,
            "event_types": event_types,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("ecosystem_webhook", method="POST", payload=payload)
    
    # Device Connection Monitoring Functions
    def get_device_connections(self) -> Dict[str, Any]:
        """Get all device connections"""
        return self._call("monitor_device_connections", method="GET")
    
    def register_device(self, device_name: str, device_type: str, **metadata) -> Dict[str, Any]:
        """Register a new device"""
        payload = {
            "action": "register",
            "device_name": device_name,
            "device_type": device_type,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("monitor_device_connections", method="POST", payload=payload)
    
    def update_device_status(self, device_id: str, status: str) -> Dict[str, Any]:
        """Update device status"""
        payload = {
            "action": "update_status",
            "device_id": device_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        return self._call("monitor_device_connections", method="POST", payload=payload)
    
    # Health Check Functions
    def health_check_all(self) -> Dict[str, bool]:
        """Check health of all edge functions"""
        results = {}
        
        for func_name, func_url in self.functions.items():
            try:
                response = requests.get(func_url, headers=self.headers, timeout=5)
                # 200 or 404 means the function exists
                results[func_name] = response.status_code in [200, 404, 405]
            except:
                results[func_name] = False
        
        edge_logger.info("Health check completed", results=results)
        return results
    
    def is_function_available(self, function_name: str) -> bool:
        """Check if a specific function is available"""
        if function_name not in self.functions:
            return False
        
        try:
            url = self.functions[function_name]
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code in [200, 404, 405]
        except:
            return False


# Singleton instance
_client_instance: Optional[EdgeFunctionClient] = None

def get_edge_client(supabase_url: str = None, api_key: str = None) -> EdgeFunctionClient:
    """
    Get or create the EdgeFunctionClient singleton
    
    Args:
        supabase_url: Supabase URL (only needed on first call)
        api_key: API key (only needed on first call)
    
    Returns:
        EdgeFunctionClient instance
    """
    global _client_instance
    
    if _client_instance is None:
        if supabase_url is None or api_key is None:
            # Use default values
            supabase_url = "https://vawouugtzwmejxqkeqqj.supabase.co"
            api_key = "sb_publishable_yIaroctFhoYStx0f9XajBg_zhpuVulw"
        
        _client_instance = EdgeFunctionClient(supabase_url, api_key)
    
    return _client_instance


__all__ = ['EdgeFunctionClient', 'get_edge_client']
