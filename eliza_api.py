from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json
import traceback
from datetime import datetime

app = FastAPI(title="Eliza Debug API", version="3.1.0-debug")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Debug info storage
debug_info = {
    "startup_time": datetime.now().isoformat(),
    "import_attempts": [],
    "errors": [],
    "system_info": {
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "files_present": []
    }
}

# Try to import each system with debug info
print("🔍 DEBUG: Starting import attempts...")

# Check what files exist
try:
    files_in_dir = os.listdir('.')
    debug_info["system_info"]["files_present"] = [f for f in files_in_dir if f.endswith('.py')]
    print(f"📁 Files found: {debug_info['system_info']['files_present']}")
except Exception as e:
    debug_info["errors"].append(f"File listing error: {str(e)}")

# Try basic learning import
try:
    from eliza_learning import ElizaLearningEngine
    learning_engine = ElizaLearningEngine()
    debug_info["import_attempts"].append({"module": "eliza_learning", "status": "SUCCESS"})
    LEARNING_AVAILABLE = True
    print("✅ Learning engine imported successfully")
except Exception as e:
    debug_info["import_attempts"].append({"module": "eliza_learning", "status": "FAILED", "error": str(e)})
    debug_info["errors"].append(f"Learning import error: {str(e)}")
    learning_engine = None
    LEARNING_AVAILABLE = False
    print(f"❌ Learning engine failed: {e}")

# Try advanced integration import
try:
    from eliza_advanced_integration import ElizaAdvancedIntegration
    advanced_eliza = ElizaAdvancedIntegration()
    debug_info["import_attempts"].append({"module": "eliza_advanced_integration", "status": "SUCCESS"})
    ADVANCED_AVAILABLE = True
    print("✅ Advanced integration imported successfully")
except Exception as e:
    debug_info["import_attempts"].append({"module": "eliza_advanced_integration", "status": "FAILED", "error": str(e)})
    debug_info["errors"].append(f"Advanced integration error: {str(e)}")
    advanced_eliza = None
    ADVANCED_AVAILABLE = False
    print(f"❌ Advanced integration failed: {e}")
    print(f"📋 Full traceback: {traceback.format_exc()}")

# Try core system import
try:
    from xmrtnet.core.eliza_core import ElizaCore
    eliza_core = ElizaCore()
    debug_info["import_attempts"].append({"module": "eliza_core", "status": "SUCCESS"})
    CORE_AVAILABLE = True
    print("✅ Eliza core imported successfully")
except Exception as e:
    debug_info["import_attempts"].append({"module": "eliza_core", "status": "FAILED", "error": str(e)})
    debug_info["errors"].append(f"Core system error: {str(e)}")
    eliza_core = None
    CORE_AVAILABLE = False
    print(f"❌ Eliza core failed: {e}")

class ChatMessage(BaseModel):
    message: str
    user_id: str = "debug_user"

@app.get("/")
async def debug_root():
    """Debug root with full diagnostic info"""
    return {
        "service": "Eliza Debug API",
        "version": "3.1.0-debug",
        "status": "DEBUGGING ACTIVE",
        "systems_available": {
            "learning_engine": LEARNING_AVAILABLE,
            "advanced_integration": ADVANCED_AVAILABLE,
            "core_system": CORE_AVAILABLE
        },
        "debug_info": debug_info,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/full")
async def full_debug_info():
    """Get complete debug information"""
    return {
        "debug_session": debug_info,
        "current_status": {
            "learning_available": LEARNING_AVAILABLE,
            "advanced_available": ADVANCED_AVAILABLE,
            "core_available": CORE_AVAILABLE
        },
        "file_system": {
            "working_dir": os.getcwd(),
            "python_files": [f for f in os.listdir('.') if f.endswith('.py')]
        }
    }

@app.post("/api/chat")
async def debug_chat(message: ChatMessage):
    """Debug chat endpoint"""
    
    response_info = {
        "message_received": message.message,
        "systems_tried": [],
        "final_response": "",
        "debug_notes": []
    }
    
    # Try advanced system first
    if ADVANCED_AVAILABLE and advanced_eliza:
        try:
            result = advanced_eliza.process_with_agents(message.message, message.user_id)
            response_info["systems_tried"].append("advanced_integration")
            response_info["final_response"] = result["response"]
            response_info["debug_notes"].append("Advanced system working!")
            
            return {
                "response": result["response"],
                "system_used": "advanced",
                "debug_info": response_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            response_info["debug_notes"].append(f"Advanced system error: {str(e)}")
    
    # Try core system
    if CORE_AVAILABLE and eliza_core:
        try:
            core_response = eliza_core.process_prompt(message.user_id, message.message)
            response_info["systems_tried"].append("core_system")
            response_info["final_response"] = core_response
            response_info["debug_notes"].append("Core system working!")
            
            return {
                "response": core_response,
                "system_used": "core",
                "debug_info": response_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            response_info["debug_notes"].append(f"Core system error: {str(e)}")
    
    # Fallback response
    response_info["final_response"] = f"DEBUG MODE: Received '{message.message}' - All systems being debugged"
    response_info["debug_notes"].append("Using fallback response")
    
    return {
        "response": response_info["final_response"],
        "system_used": "fallback",
        "debug_info": response_info,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🐛 Starting Eliza Debug API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
