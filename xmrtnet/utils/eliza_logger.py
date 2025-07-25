import json
import sys
import uuid
from datetime import datetime, timezone

class ElizaLogger:
    """
    Eliza Standard Log Protocol (ESLP) - Her digital memory system
    """
    
    def __init__(self, service_name: str):
        if not service_name:
            raise ValueError("service_name required")
        self.service_name = service_name
    
    def log(self, event_type: str, session_info: dict, payload: dict, 
            performance: dict = None, analysis: dict = None):
        """Log structured events for Eliza's progress tracking"""
        
        log_entry = {
            "eventId": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": self.service_name,
            "eventType": event_type,
            "session": session_info,
            "performance": performance or {},
            "payload": payload,
            "analysis": analysis or {}
        }
        
        print(json.dumps(log_entry))
        sys.stdout.flush()

# Demo usage
if __name__ == "__main__":
    logger = ElizaLogger("ElizaCore.Demo")
    logger.log(
        event_type="SYSTEM_INITIALIZED",
        session_info={"userId": "DevGruGold", "sessionId": "demo"},
        payload={"message": "Eliza logging system online"}
    )
