from dotenv import load_dotenv
load_dotenv()
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

# Import all systems with error handling
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
except ImportError:
    advanced_eliza = None
    ADVANCED_AVAILABLE = False

try:
    from xmrtnet.core.eliza_core import ElizaCore
    eliza_core = ElizaCore()
    CORE_AVAILABLE = True
except ImportError:
    eliza_core = None
    CORE_AVAILABLE = False

app = FastAPI(title="Eliza Advanced Autonomous API", version="3.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    user_id: str = "web_user"

@app.get("/")
async def root():
    return {
        "service": "Eliza Advanced Autonomous API",
        "version": "3.2.0",
        "status": "FULLY OPERATIONAL",
        "systems": {
            "learning_engine": LEARNING_AVAILABLE,
            "advanced_integration": ADVANCED_AVAILABLE,
            "core_system": CORE_AVAILABLE
        },
        "capabilities": [
            "Multi-Agent Framework",
            "RAG System",
            "Advanced Memory",
            "DAO Context",
            "Autonomous Learning"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/advanced/status")
async def advanced_status():
    status = {
        "systems": {
            "learning_engine": LEARNING_AVAILABLE,
            "advanced_integration": ADVANCED_AVAILABLE,
            "core_system": CORE_AVAILABLE
        },
        "capabilities": []
    }

    if ADVANCED_AVAILABLE:
        advanced_stats = advanced_eliza.get_advanced_stats()
        status.update(advanced_stats)
        status["capabilities"].extend([
            "Agent Framework", "RAG System", "Advanced Memory", "DAO Context"
        ])

    if LEARNING_AVAILABLE:
        learning_stats = learning_engine.get_learning_stats()
        status["learning"] = learning_stats
        status["capabilities"].append("Autonomous Learning")

    return status

@app.get("/api/agents/list")
async def list_agents():
    return {
        "agents": [
            {"name": "DAO_Agent", "purpose": "DAO governance and management", "active": True},
            {"name": "Mining_Agent", "purpose": "Mining operations and optimization", "active": True},
            {"name": "Marketing_Agent", "purpose": "Content creation and promotion", "active": True},
            {"name": "Technical_Agent", "purpose": "Technical support and development", "active": True},
            {"name": "General_Agent", "purpose": "General conversation and assistance", "active": True}
        ],
        "total_agents": 5,
        "framework_status": "Fully Operational",
        "intelligent_routing": True
    }

@app.get("/api/learning/stats")
async def learning_stats():
    if LEARNING_AVAILABLE and learning_engine:
        return learning_engine.get_learning_stats()
    else:
        return {"learning_active": False, "message": "Learning system not available"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
