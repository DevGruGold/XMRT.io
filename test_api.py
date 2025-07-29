# Simple test API for XMRT.io deployment verification
from fastapi import FastAPI

app = FastAPI(title="XMRT Test API", version="1.0.0")

@app.get("/")
async def root():
    return {
        "message": "XMRT Knowledge Bridge Test API",
        "status": "operational",
        "test": "deployment_successful"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "xmrt-test-api"}
