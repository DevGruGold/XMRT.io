"""
Vercel Serverless Entry Point for XMRT.io
Wraps the FastAPI application for Vercel deployment
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import server.py
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Import the FastAPI app from server.py
try:
    from server import app
    print("✅ FastAPI app imported successfully")
except ImportError as e:
    print(f"❌ Failed to import FastAPI app: {e}")
    # Create minimal fallback app
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return JSONResponse({
            "status": "error",
            "message": "Failed to load main application",
            "error": str(e)
        })
    
    @app.get("/health")
    async def health():
        return JSONResponse({
            "status": "degraded",
            "message": "Running in fallback mode"
        })

# Vercel serverless handler
# This is the entry point that Vercel will call
handler = app

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
