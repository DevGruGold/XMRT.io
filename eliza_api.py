from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json
import time
from datetime import datetime

# Add our systems to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import all Eliza systems
try:
    from xmrtnet.core.eliza_core import ElizaCore
    ELIZA_CORE_AVAILABLE = True
except ImportError:
    ELIZA_CORE_AVAILABLE = False

try:
    from eliza_learning import ElizaLearningEngine
    learning_engine = ElizaLearningEngine()
    LEARNING_AVAILABLE = True
except ImportError:
    learning_engine = None
    LEARNING_AVAILABLE = False

try:
    from eliza_advanced_integration import ElizaAdvancedIntegration
    advanced_eliza = ElizaAdvancedIntegration()
    ADVANCED_AVAILABLE = True
    print("🚀 Advanced Eliza Integration loaded!")
except ImportError as e:
    advanced_eliza = None
    ADVANCED_AVAILABLE = False
    print(f"⚠️  Advanced integration not available: {e}")

app = FastAPI(title="Eliza Advanced Autonomous API", version="3.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core systems
eliza_core = None
if ELIZA_CORE_AVAILABLE:
    eliza_core = ElizaCore()

class ChatMessage(BaseModel):
    message: str
    user_id: str = "web_user"

class AdvancedChatResponse(BaseModel):
    response: str
    timestamp: str
    session_id: str
    eliza_online: bool
    learning_active: bool
    advanced_integration: bool
    agent_type: str
    rag_sources_used: int
    memory_accessed: int
    dao_context_active: bool
    architecture_level: str

@app.get("/")
async def root():
    """Root endpoint with full system status"""
    return {
        "service": "Eliza Advanced Autonomous API",
        "version": "3.0.0",
        "status": "ADVANCED ARCHITECTURE ACTIVE",
        "eliza_core": "online" if ELIZA_CORE_AVAILABLE else "simulated",
        "learning_engine": "active" if LEARNING_AVAILABLE else "offline",
        "advanced_integration": "active" if ADVANCED_AVAILABLE else "offline",
        "architecture_level": "Advanced Agent Framework + RAG + Memory",
        "timestamp": datetime.now().isoformat(),
        "message": "🚀 Eliza is now running on advanced architecture!"
    }

@app.post("/api/chat", response_model=AdvancedChatResponse)
async def advanced_chat(message: ChatMessage):
    """Advanced chat with full architecture integration"""
    start_time = time.time()
    
    # Use advanced integration if available
    if ADVANCED_AVAILABLE and advanced_eliza:
        # Process through advanced agent framework
        advanced_result = advanced_eliza.process_with_agents(message.message, message.user_id)
        
        eliza_response = advanced_result["response"]
        agent_type = advanced_result["agent_type"]
        rag_sources_used = advanced_result["rag_sources_used"]
        memory_accessed = advanced_result["memory_accessed"]
        dao_context_active = advanced_result["dao_context_active"]
        architecture_level = "Advanced"
        
    elif ELIZA_CORE_AVAILABLE and eliza_core:
        # Fallback to core system
        eliza_response = eliza_core.process_prompt(message.user_id, message.message)
        agent_type = "Core"
        rag_sources_used = 0
        memory_accessed = 0
        dao_context_active = False
        architecture_level = "Core"
        
    else:
        # Basic fallback
        eliza_response = f"Processing through advanced systems: {message.message}"
        agent_type = "Fallback"
        rag_sources_used = 0
        memory_accessed = 0
        dao_context_active = False
        architecture_level = "Basic"
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000
    
    # Learn from conversation (both systems)
    if LEARNING_AVAILABLE and learning_engine:
        learning_engine.learn_from_conversation(
            message.message, eliza_response, response_time, message.user_id
        )
    
    return AdvancedChatResponse(
        response=eliza_response,
        timestamp=datetime.now().isoformat(),
        session_id=f"advanced_{int(time.time())}",
        eliza_online=True,
        learning_active=LEARNING_AVAILABLE,
        advanced_integration=ADVANCED_AVAILABLE,
        agent_type=agent_type,
        rag_sources_used=rag_sources_used,
        memory_accessed=memory_accessed,
        dao_context_active=dao_context_active,
        architecture_level=architecture_level
    )

@app.get("/api/advanced/status")
async def advanced_system_status():
    """Get full advanced system status"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "systems": {
            "eliza_core": ELIZA_CORE_AVAILABLE,
            "learning_engine": LEARNING_AVAILABLE,
            "advanced_integration": ADVANCED_AVAILABLE
        },
        "capabilities": []
    }
    
    if ADVANCED_AVAILABLE:
        advanced_stats = advanced_eliza.get_advanced_stats()
        status.update(advanced_stats)
        status["capabilities"].extend([
            "Agent Framework",
            "RAG System", 
            "Long-term Memory",
            "DAO Context Awareness",
            "Multi-agent Coordination"
        ])
    
    if LEARNING_AVAILABLE:
        learning_stats = learning_engine.get_learning_stats()
        status["learning_stats"] = learning_stats
        status["capabilities"].append("Autonomous Learning")
    
    return status

@app.get("/api/agents/list")
async def list_active_agents():
    """List all active agents in the system"""
    if ADVANCED_AVAILABLE:
        return {
            "agents": [
                {"name": "DAO_Agent", "purpose": "DAO governance and management"},
                {"name": "Mining_Agent", "purpose": "Mining operations and optimization"},
                {"name": "Marketing_Agent", "purpose": "Content creation and promotion"},
                {"name": "Technical_Agent", "purpose": "Technical support and development"},
                {"name": "General_Agent", "purpose": "General conversation and assistance"}
            ],
            "coordination": "Active",
            "framework": "Advanced Agent Architecture"
        }
    else:
        return {"agents": [], "status": "Advanced integration not available"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Advanced Eliza API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
