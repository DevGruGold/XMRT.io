from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json
from datetime import datetime

# Add our Eliza Core to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import Eliza Core
try:
    from xmrtnet.core.eliza_core import ElizaCore
    ELIZA_AVAILABLE = True
    print("✅ Eliza Core imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Eliza Core: {e}")
    ELIZA_AVAILABLE = False

app = FastAPI(title="Eliza API Backend", version="1.0.0")

# Configure CORS to allow the React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://xmrteliza.vercel.app", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Eliza
eliza_core = None
if ELIZA_AVAILABLE:
    eliza_core = ElizaCore()

class ChatMessage(BaseModel):
    message: str
    user_id: str = "api_user"

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    session_id: str
    eliza_online: bool

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Eliza API Backend",
        "version": "1.0.0",
        "eliza_online": ELIZA_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "eliza_core": "online" if ELIZA_AVAILABLE else "offline",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_eliza(message: ChatMessage):
    """Main chat endpoint for React app"""
    
    if not ELIZA_AVAILABLE or not eliza_core:
        return ChatResponse(
            response="Eliza Core is currently offline. Please try again later.",
            timestamp=datetime.now().isoformat(),
            session_id="offline",
            eliza_online=False
        )
    
    try:
        # Process message through Eliza Core
        eliza_response = eliza_core.process_prompt(message.user_id, message.message)
        
        return ChatResponse(
            response=eliza_response,
            timestamp=datetime.now().isoformat(),
            session_id=eliza_core.session_id,
            eliza_online=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/eliza/status")
async def eliza_status():
    """Get Eliza's current status"""
    return {
        "online": ELIZA_AVAILABLE,
        "model_version": "eliza-v1.0.0-production" if ELIZA_AVAILABLE else None,
        "session_active": eliza_core.session_id if eliza_core else None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/eliza/message")
async def send_message(message: ChatMessage):
    """Alternative message endpoint"""
    return await chat_with_eliza(message)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Eliza API Backend...")
    print("🌐 React app can connect to: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
