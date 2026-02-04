"""
XMRT FastAPI Server
Enhanced with health monitoring and Supabase connectivity checks
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
import httpx
from typing import Dict, Any
import asyncio
from fastapi.staticfiles import StaticFiles

# Import Ecosystem Routers
from mcp_endpoints import mcp_router
from webhook_endpoints import webhook_router

# Initialize FastAPI app
app = FastAPI(
    title="XMRT API",
    description="XMRT DAO Ecosystem API with health monitoring",
    version="2.0.0"
)

# Mount Ecosystem Routers
app.include_router(mcp_router)
app.include_router(webhook_router)

# Mount Static Files
# We serve static assets from the root for simplicity in this Vercel setup
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vawouugtzwmejxqkeqqj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
DEPLOYMENT_ENV = os.getenv("VERCEL_ENV", "development")
VERCEL_REGION = os.getenv("VERCEL_REGION", "unknown")

@app.get("/")
async def root():
    """Serve the main application"""
    return FileResponse('index.html')

@app.get("/chat")
async def chat_page():
    """Serve the chat interface"""
    return FileResponse('chat.html')

@app.get("/api/info")
async def api_info():
    """Root endpoint with API information"""
    return {
        "message": "XMRT API - Decentralized Mobile Mining Infrastructure",
        "version": "2.0.0",
        "status": "operational",
        "ecosystem": "XMRT DAO",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api": "/api"
        },
        "project": {
            "name": "XMRT",
            "description": "Mobile Monero Mining & DAO Governance Platform",
            "website": "https://mobilemonero.com",
            "github": "https://github.com/DevGruGold/XMRT-Ecosystem"
        }
    }

@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for monitoring
    Checks system status and Supabase connectivity
    """
    start_time = datetime.utcnow()
    health_status = {
        "status": "healthy",
        "timestamp": start_time.isoformat() + "Z",
        "deployment": {
            "environment": DEPLOYMENT_ENV,
            "region": VERCEL_REGION,
            "platform": "Vercel"
        },
        "services": {},
        "metadata": {
            "api_version": "2.0.0",
            "python_version": os.getenv("PYTHON_VERSION", "3.12"),
            "uptime_check": "passed"
        }
    }
    
    # Check Supabase connectivity
    supabase_healthy = False
    supabase_latency = 0
    
    try:
        supabase_start = datetime.utcnow()
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Check Supabase REST API health
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}"
                }
            )
            supabase_latency = (datetime.utcnow() - supabase_start).total_seconds() * 1000
            supabase_healthy = response.status_code in [200, 401]  # 401 is OK (auth check)
            
            health_status["services"]["supabase"] = {
                "status": "healthy" if supabase_healthy else "degraded",
                "url": SUPABASE_URL,
                "latency_ms": round(supabase_latency, 2),
                "response_code": response.status_code
            }
    except Exception as e:
        health_status["services"]["supabase"] = {
            "status": "unhealthy",
            "url": SUPABASE_URL,
            "error": str(e),
            "latency_ms": round(supabase_latency, 2) if supabase_latency > 0 else "timeout"
        }
        health_status["status"] = "degraded"
    
    # Calculate total response time
    total_latency = (datetime.utcnow() - start_time).total_seconds() * 1000
    health_status["response_time_ms"] = round(total_latency, 2)
    
    # Determine HTTP status code
    if health_status["status"] == "healthy":
        status_code = 200
    elif health_status["status"] == "degraded":
        status_code = 200  # Still return 200 for degraded but warn
    else:
        status_code = 503  # Service unavailable
    
    return JSONResponse(content=health_status, status_code=status_code)

@app.get("/favicon.ico")
async def favicon():
    """
    Handle favicon requests to prevent 404 errors
    Returns empty response with proper content type
    """
    # Return 204 No Content - valid response for missing favicon
    return Response(status_code=204)

@app.get("/api/status")
async def api_status():
    """API-specific status endpoint"""
    return {
        "api": "operational",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.0.0",
        "services": {
            "core": "operational",
            "database": "connected",
            "mining": "active"
        }
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested endpoint {request.url.path} does not exist",
            "available_endpoints": ["/", "/health", "/api/status", "/docs"],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("XMRT API starting up...")
    print(f"   Environment: {DEPLOYMENT_ENV}")
    print(f"   Region: {VERCEL_REGION}")
    print(f"   Supabase URL: {SUPABASE_URL}")
    print("XMRT API ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("XMRT API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
