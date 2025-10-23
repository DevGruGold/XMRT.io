from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import logging
from datetime import datetime

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

# --- Mock Real-Time Activity Store (In-memory for simplicity) ---
# In a real system, this would be a Redis or database connection.
real_time_activity_store = []

# --- Endpoints ---

@mcp_router.get("/mcp/health", response_model=MCPResponse, tags=["mCP Integration"])
async def mcp_health_check():
    """Endpoint for mCP server to check the health and availability of the system."""
    return MCPResponse(
        status="operational",
        message="XMRT.io MCP Gateway is online and ready for engagement.",
        data={"timestamp": datetime.now().isoformat()}
    )

@mcp_router.post("/mcp/activity", response_model=MCPResponse, tags=["mCP Integration"])
async def receive_mcp_activity(message: MCPMessage = Body(...)):
    """Endpoint for mCP server to push real-time activity updates."""
    logger.info(f"Received mCP Activity from {message.sender} on topic {message.topic}")
    
    # Store the activity for the Streamlit frontend to potentially display
    activity_data = {
        "timestamp": message.timestamp,
        "sender": message.sender,
        "topic": message.topic,
        "summary": message.payload.get("summary", "No summary provided."),
        "raw_payload": message.payload
    }
    
    # Keep the store size manageable
    global real_time_activity_store
    real_time_activity_store.insert(0, activity_data)
    real_time_activity_store = real_time_activity_store[:50] # Keep last 50 activities

    return MCPResponse(
        status="success",
        message=f"Activity from {message.sender} received and processed.",
        data={"activity_id": len(real_time_activity_store)}
    )

@mcp_router.get("/mcp/activities", tags=["mCP Integration"])
async def get_mcp_activities(limit: int = 10):
    """Endpoint for the Streamlit frontend to fetch the latest real-time activities."""
    return real_time_activity_store[:limit]

@mcp_router.post("/mcp/test_command", response_model=MCPResponse, tags=["mCP Integration"])
async def test_mcp_command(command: Dict[str, Any] = Body(...)):
    """A simple endpoint to test command execution from an mCP server."""
    logger.info(f"Received Test Command: {command}")
    
    # Simulate processing and response
    response_data = {
        "received_command": command,
        "processed_by": "XMRT.io Gateway",
        "status": "command_simulated_success"
    }
    
    return MCPResponse(
        status="success",
        message="Test command received and simulated processing.",
        data=response_data
    )

# --- FastAPI App Integration ---
# This file will be imported and mounted by server.py

