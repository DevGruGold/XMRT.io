"""
Webhook Endpoints for XMRT Ecosystem Inter-System Communication
===============================================================

This module provides webhook endpoints that can be added to the XMRT DAO
ecosystem to enable real-time communication.

Rewritten for FastAPI.
"""

from fastapi import APIRouter, HTTPException, Request, Body, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Initialize Router
webhook_router = APIRouter(
    prefix="/api",
    tags=["Ecosystem Webhooks"]
)

# In-memory storage for received activities (simulating database for this example)
# In production, this should be replaced with a real database connection
received_activities: List[Dict[str, Any]] = []
ecosystem_state: Dict[str, Any] = {}

# --- Pydantic Models ---

class WebhookData(BaseModel):
    source_system: str
    event_type: str
    data: Dict[str, Any]
    timestamp: str
    event_id: str

class EcosystemSyncData(BaseModel):
    # Flexible dict updates
    pass 

# --- Routes ---

@webhook_router.post("/webhook/receive")
async def receive_webhook(webhook_data: WebhookData):
    """Receive webhook from other systems in the ecosystem"""
    try:
        # Store the activity
        activity = webhook_data.model_dump()
        activity["received_at"] = datetime.now().isoformat()
        
        received_activities.append(activity)
        
        # Keep only last 100 activities
        if len(received_activities) > 100:
            received_activities.pop(0)
        
        logger.info(f"📨 Received {webhook_data.event_type} from {webhook_data.source_system}")
        
        return {
            "success": True,
            "message": "Activity received successfully",
            "event_id": webhook_data.event_id
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/ecosystem/sync")
async def sync_ecosystem_state(data: Dict[str, Any] = Body(...)):
    """Receive ecosystem state synchronization"""
    try:
        # Update ecosystem state
        ecosystem_state.update(data)
        ecosystem_state['last_sync'] = datetime.now().isoformat()
        
        logger.info("🔄 Ecosystem state synchronized")
        
        return {
            "success": True,
            "message": "Ecosystem state synchronized",
            "timestamp": ecosystem_state['last_sync']
        }
        
    except Exception as e:
        logger.error(f"Error syncing ecosystem state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.get("/ecosystem/activities")
async def get_ecosystem_activities(
    event_type: Optional[str] = Query(None),
    source_system: Optional[str] = Query(None),
    limit: int = Query(50)
):
    """Get received activities from other systems"""
    try:
        filtered_activities = received_activities
        
        if event_type:
            filtered_activities = [a for a in filtered_activities if a['event_type'] == event_type]
        
        if source_system:
            filtered_activities = [a for a in filtered_activities if a['source_system'] == source_system]
        
        # Apply limit
        filtered_activities = filtered_activities[-limit:]
        
        return {
            "success": True,
            "activities": filtered_activities,
            "total_count": len(filtered_activities),
            "ecosystem_state": ecosystem_state
        }
        
    except Exception as e:
        logger.error(f"Error getting ecosystem activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.get("/ecosystem/status")
async def get_ecosystem_status():
    """Get current ecosystem coordination status"""
    try:
        status = {
            "webhook_active": True,
            "received_activities_count": len(received_activities),
            "last_activity": received_activities[-1] if received_activities else None,
            "ecosystem_state": ecosystem_state,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting ecosystem status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.get("/activity/feed")
async def get_activity_feed(limit: int = Query(20)):
    """Get activity feed for frontend display"""
    try:
        # Get recent activities formatted for frontend
        recent_activities = received_activities[-limit:]
        
        # Format activities for display
        formatted_activities = []
        for activity in recent_activities:
            formatted_activity = {
                "id": activity['event_id'],
                "title": _format_activity_title(activity),
                "description": _format_activity_description(activity),
                "source": activity['source_system'],
                "timestamp": activity['timestamp'],
                "type": activity['event_type'],
                "data": activity['data']
            }
            formatted_activities.append(formatted_activity)
        
        return {
            "success": True,
            "activities": formatted_activities,
            "total_count": len(formatted_activities)
        }
        
    except Exception as e:
        logger.error(f"Error getting activity feed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _format_activity_title(activity: Dict[str, Any]) -> str:
    """Format activity title for display"""
    event_type = activity.get('event_type', 'unknown')
    source = activity.get('source_system', 'unknown')
    
    titles = {
        'growth_update': f"📈 Growth Metrics Updated",
        'system_status': f"🔧 System Status from {source.title()}",
        'agent_discussion': f"💬 Agent Discussion in {source.title()}",
        'mining_update': f"⛏️ Mining Stats Updated",
        'meshnet_update': f"📡 MESHNET Status Updated"
    }
    
    return titles.get(event_type, f"🔔 {event_type.replace('_', ' ').title()}")

def _format_activity_description(activity: Dict[str, Any]) -> str:
    """Format activity description for display"""
    event_type = activity.get('event_type', 'unknown')
    data = activity.get('data', {})
    
    if event_type == 'growth_update':
        health = data.get('overall_health', 'Unknown')
        return f"Overall health: {health}, Motivation level updated"
    
    elif event_type == 'agent_discussion':
        agent_name = data.get('agent_name', 'Agent')
        message = data.get('message', '')
        if len(message) > 100:
            message = message[:100] + '...'
        return f"{agent_name}: {message}"
    
    elif event_type == 'mining_update':
        hashrate = data.get('total_hashrate', 'Unknown')
        miners = data.get('active_miners', 'Unknown')
        return f"Hashrate: {hashrate}, Active miners: {miners}"
    
    elif event_type == 'meshnet_update':
        nodes = data.get('active_nodes', 'Unknown')
        coverage = data.get('network_coverage', 'Unknown')
        return f"Active nodes: {nodes}, Coverage: {coverage}"
    
    else:
        return f"Activity from {activity.get('source_system', 'unknown')}"
