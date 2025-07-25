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

# Import our systems
try:
    from xmrtnet.core.eliza_core import ElizaCore
    ELIZA_CORE_AVAILABLE = True
except ImportError:
    ELIZA_CORE_AVAILABLE = False

try:
    from eliza_learning import ElizaLearningEngine
    learning_engine = ElizaLearningEngine()
    LEARNING_AVAILABLE = True
    print("🧠 Learning engine initialized")
except ImportError as e:
    learning_engine = None
    LEARNING_AVAILABLE = False
    print(f"⚠️  Learning engine not available: {e}")

app = FastAPI(title="Eliza Autonomous Learning API", version="2.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Eliza Core
eliza_core = None
if ELIZA_CORE_AVAILABLE:
    eliza_core = ElizaCore()

class ChatMessage(BaseModel):
    message: str
    user_id: str = "web_user"

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    session_id: str
    eliza_online: bool
    learning_active: bool
    response_improved: bool

@app.get("/")
async def root():
    """Root endpoint with learning status"""
    return {
        "service": "Eliza Autonomous Learning API",
        "version": "2.0.0",
        "status": "LEARNING & GROWING",
        "eliza_core": "online" if ELIZA_CORE_AVAILABLE else "simulated",
        "learning_engine": "active" if LEARNING_AVAILABLE else "offline",
        "timestamp": datetime.now().isoformat(),
        "message": "🧠 Eliza is learning from every interaction!"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_learning_eliza(message: ChatMessage):
    """Chat endpoint with learning integration"""
    start_time = time.time()
    
    # Try to get improved response from learning
    improved_response = None
    if LEARNING_AVAILABLE and learning_engine:
        improved_response = learning_engine.get_improved_response(message.message)
    
    # Generate response
    if improved_response:
        eliza_response = improved_response
        response_improved = True
    elif ELIZA_CORE_AVAILABLE and eliza_core:
        eliza_response = eliza_core.process_prompt(message.user_id, message.message)
        response_improved = False
    else:
        # Fallback responses
        user_msg = message.message.lower()
        if "learn" in user_msg:
            eliza_response = "Yes! I'm actively learning from every conversation. I analyze patterns, topics, and responses to continuously improve. Each interaction makes me smarter!"
        elif "growing" in user_msg:
            eliza_response = "I'm growing autonomously by learning from all interactions, analyzing conversation patterns, and adapting my responses based on what works best."
        else:
            eliza_response = f"I'm processing and learning from: '{message.message}'. This conversation is being analyzed to improve my future responses!"
        response_improved = False
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000
    
    # Learn from this conversation
    if LEARNING_AVAILABLE and learning_engine:
        learning_engine.learn_from_conversation(
            message.message, 
            eliza_response, 
            response_time, 
            message.user_id
        )
    
    return ChatResponse(
        response=eliza_response,
        timestamp=datetime.now().isoformat(),
        session_id=f"learning_{int(time.time())}",
        eliza_online=True,
        learning_active=LEARNING_AVAILABLE,
        response_improved=response_improved
    )

@app.get("/api/learning/stats")
async def learning_statistics():
    """Get Eliza's learning statistics"""
    if LEARNING_AVAILABLE and learning_engine:
        stats = learning_engine.get_learning_stats()
        return {
            "learning_active": True,
            **stats,
            "message": "Eliza is actively learning and improving!"
        }
    else:
        return {
            "learning_active": False,
            "message": "Learning engine not available"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🧠 Starting Eliza Learning API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
