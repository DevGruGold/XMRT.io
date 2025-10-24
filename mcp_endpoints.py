from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, List
import logging
from datetime import datetime
import os

# Import real ecosystem config
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))
from real_ecosystem_config import get_ecosystem_config

logger = logging.getLogger(__name__)

# --- Data Schemas for mCP Communication ---

class MCPMessage(BaseModel):
    """Schema for incoming mCP messages."""
    sender: str
    recipient: str
    topic: str
    payload: Dict[str, Any]
    timestamp: str = datetime.now().isoformat()

class MCPResponse(BaseModel):
    """Schema for outgoing mCP responses."""
    status: str
    message: str
    data: Dict[str, Any] = {}

# --- Router Initialization ---

mcp_router = APIRouter()

# Initialize real ecosystem config
ecosystem = get_ecosystem_config()

# --- Real Data Storage ---
# All activities are now stored in Supabase, not in-memory

# --- Endpoints ---

@mcp_router.get("/mcp/health", response_model=MCPResponse, tags=["mCP Integration"])
async def mcp_health_check():
    """Endpoint for mCP server to check the health and availability of the system."""
    
    # Check real service health
    supabase_status = "connected" if ecosystem.supabase else "disconnected"
    github_status = "connected" if ecosystem.github else "disconnected"
    gemini_status = "connected" if ecosystem.gemini_model else "disconnected"
    
    return MCPResponse(
        status="operational",
        message="XMRT.io MCP Gateway is online with real integrations.",
        data={
            "timestamp": datetime.now().isoformat(),
            "supabase": supabase_status,
            "github": github_status,
            "gemini_ai": gemini_status
        }
    )

@mcp_router.post("/mcp/activity", response_model=MCPResponse, tags=["mCP Integration"])
async def receive_mcp_activity(message: MCPMessage = Body(...)):
    """Endpoint for mCP server to push real-time activity updates."""
    logger.info(f"Received mCP Activity from {message.sender} on topic {message.topic}")
    
    # Store the activity in real Supabase database
    activity_data = {
        "timestamp": message.timestamp,
        "sender": message.sender,
        "recipient": message.recipient,
        "topic": message.topic,
        "summary": message.payload.get("summary", "No summary provided."),
        "raw_payload": message.payload
    }
    
    # Log to Supabase
    success = ecosystem.log_activity('mcp_activity', activity_data)
    
    if success:
        return MCPResponse(
            status="success",
            message=f"Activity from {message.sender} received and stored in database.",
            data={"activity_logged": True, "database": "supabase"}
        )
    else:
        return MCPResponse(
            status="warning",
            message=f"Activity received but database logging failed.",
            data={"activity_logged": False}
        )

@mcp_router.get("/mcp/activities", tags=["mCP Integration"])
async def get_mcp_activities(limit: int = 10):
    """Endpoint for the Streamlit frontend to fetch the latest real-time activities."""
    
    # Fetch from real Supabase database
    activities = ecosystem.get_recent_activities(limit=limit)
    
    if activities:
        return {
            "status": "success",
            "count": len(activities),
            "activities": activities,
            "source": "supabase"
        }
    else:
        return {
            "status": "no_data",
            "count": 0,
            "activities": [],
            "message": "No activities found or database not configured"
        }

@mcp_router.post("/mcp/command", response_model=MCPResponse, tags=["mCP Integration"])
async def execute_mcp_command(command: Dict[str, Any] = Body(...)):
    """Execute real commands from mCP servers."""
    logger.info(f"Received Real Command: {command}")
    
    command_type = command.get("command_type")
    params = command.get("params", {})
    
    # Real command execution logic
    try:
        if command_type == "fetch_github_activity":
            # Execute real GitHub fetch
            github_data = ecosystem.get_github_activity()
            
            return MCPResponse(
                status="success",
                message="GitHub activity fetched successfully",
                data={"github_activity": github_data}
            )
        
        elif command_type == "generate_ai_response":
            # Execute real AI generation
            message = params.get("message", "")
            agent_context = params.get("agent", "eliza")
            
            response = ecosystem.generate_ai_response(message, agent_context)
            
            return MCPResponse(
                status="success",
                message="AI response generated",
                data=response
            )
        
        elif command_type == "log_activity":
            # Log custom activity
            activity_data = params.get("activity_data", {})
            success = ecosystem.log_activity(
                params.get("activity_type", "custom"),
                activity_data
            )
            
            return MCPResponse(
                status="success" if success else "failed",
                message="Activity logged" if success else "Failed to log activity",
                data={"logged": success}
            )
        
        else:
            return MCPResponse(
                status="unsupported",
                message=f"Command type '{command_type}' not supported",
                data={"received_command": command}
            )
            
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return MCPResponse(
            status="error",
            message=f"Command execution failed: {str(e)}",
            data={"error": str(e)}
        )

@mcp_router.get("/mcp/stats", tags=["mCP Integration"])
async def get_ecosystem_stats():
    """Get real ecosystem statistics."""
    
    try:
        # Fetch real statistics from Supabase
        activities = ecosystem.get_recent_activities(limit=100)
        
        # Calculate real stats
        activity_by_type = {}
        for activity in activities:
            act_type = activity.get('activity_type', 'unknown')
            activity_by_type[act_type] = activity_by_type.get(act_type, 0) + 1
        
        # Get GitHub stats
        github_data = None
        if ecosystem.github:
            github_data = ecosystem.get_github_activity()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "total_activities": len(activities),
            "activity_breakdown": activity_by_type,
            "github_stats": github_data,
            "services": {
                "supabase": "connected" if ecosystem.supabase else "disconnected",
                "github": "connected" if ecosystem.github else "disconnected",
                "gemini_ai": "connected" if ecosystem.gemini_model else "disconnected"
            }
        }
        
    except Exception as e:
        logger.error(f"Stats fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Webhook endpoint for GitHub ---
@mcp_router.post("/mcp/github_webhook", tags=["mCP Integration"])
async def github_webhook(payload: Dict[str, Any] = Body(...)):
    """Receive and process real GitHub webhooks."""
    
    event_type = payload.get("action", "unknown")
    repository = payload.get("repository", {}).get("full_name", "unknown")
    
    logger.info(f"GitHub webhook received: {event_type} on {repository}")
    
    # Log webhook to database
    webhook_data = {
        "event_type": event_type,
        "repository": repository,
        "payload_preview": {
            "action": payload.get("action"),
            "sender": payload.get("sender", {}).get("login"),
            "timestamp": datetime.now().isoformat()
        }
    }
    
    ecosystem.log_activity('github_webhook', webhook_data)
    
    return MCPResponse(
        status="success",
        message=f"GitHub webhook processed: {event_type}",
        data=webhook_data
    )

# --- FastAPI App Integration ---
# This file will be imported and mounted by server.py
