# XMRT Boardroom Deployment Guide

## Overview
The XMRT Boardroom serves as the orchestration hub for the XMRT ecosystem, coordinating between:
- XMRT-Dashboard (Operator's Console)
- XMRT DAO Hub (Community Portal)
- XMRT.io Boardroom System

## Deployment on Render

1. **Connect Repository**: Connect this GitHub repository to Render
2. **Select Service Type**: Choose "Web Service"
3. **Configure Build**: 
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app`
4. **Environment Variables**:
   - `PYTHON_VERSION`: 3.11.0
   - `FLASK_ENV`: production
   - `SECRET_KEY`: (auto-generated)
   - `REDIS_URL`: (from Redis service)

## Features

### Real-time Orchestration
- Synchronizes data between all XMRT systems every 30 seconds
- WebSocket connections for real-time updates
- Event bus for cross-system communication

### System Monitoring
- Health checks for all connected systems
- Performance metrics tracking
- System uptime monitoring

### API Endpoints
- `/health` - Health check
- `/api/system/status` - Current system status
- `/api/systems/connected` - Connected systems status
- `/api/orchestration/sync` - Manual sync trigger
- `/api/events/publish` - Publish events
- `/api/events/history` - Event history

### WebSocket Events
- `system_update` - Real-time system state updates
- `event` - Custom events from other systems

## Integration

Once deployed, the boardroom will automatically:
1. Connect to the existing XMRT systems
2. Start synchronizing data in real-time
3. Provide a unified orchestration interface
4. Enable cross-system communication

The deployed systems will begin showing real backend data once the boardroom is active and synchronized.
