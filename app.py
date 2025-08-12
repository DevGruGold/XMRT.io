#!/usr/bin/env python3
"""
XMRT Boardroom Flask Application - Enhanced with Growth System
==============================================================

Enhanced version of the XMRT.io boardroom system with optional
Eliza's autonomous growth system integration.

All original functionality is preserved. Growth system is optional
and controlled by environment variables for safety.

Author: Manus AI
Date: 2025-08-12
"""

import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, render_template_string, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import redis
from threading import Thread
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Growth System Feature Flags (SAFE DEFAULTS)
ENABLE_GROWTH_SYSTEM = os.environ.get('ENABLE_GROWTH_SYSTEM', 'false').lower() == 'true'
GROWTH_SYSTEM_LOG_LEVEL = os.environ.get('GROWTH_SYSTEM_LOG_LEVEL', 'INFO')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xmrt-boardroom-secret-key')

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Redis connection for event bus and caching
redis_client = None
REDIS_AVAILABLE = False

try:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    if redis_url.startswith('redis://default:'):
        # Parse Redis Cloud URL
        parts = redis_url.replace('redis://default:', '').split('@')
        password = parts[0]
        host_port = parts[1].split(':')
        host = host_port[0]
        port = int(host_port[1])
        
        redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True
        )
    else:
        redis_client = redis.from_url(redis_url, decode_responses=True)
    
    redis_client.ping()
    logger.info("Connected to Redis successfully")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis connection failed: {e}")
    redis_client = None
    REDIS_AVAILABLE = False

# Initialize Eliza's Growth System (Optional)
eliza_growth = None
GROWTH_SYSTEM_AVAILABLE = False

if ENABLE_GROWTH_SYSTEM:
    try:
        from eliza_growth_system import ElizaGrowthMotivation
        eliza_growth = ElizaGrowthMotivation()
        GROWTH_SYSTEM_AVAILABLE = True
        logger.info("🤖 Eliza's Growth System Initialized")
    except ImportError as e:
        logger.warning(f"Growth system module not found: {e}")
        GROWTH_SYSTEM_AVAILABLE = False
    except Exception as e:
        logger.error(f"Growth system initialization failed: {e}")
        GROWTH_SYSTEM_AVAILABLE = False
else:
    logger.info("Growth system disabled via environment variable")

DEPLOYED_SYSTEMS = {
    'dashboard': {
        'name': 'XMRT-Dashboard (Operator\'s Console)',
        'url': 'https://xmrt-ecosystem-redis-langgraph.onrender.com',
        'status': 'active',
        'last_sync': None
    },
    'dao_hub': {
        'name': 'XMRT DAO Hub (Community Portal)',
        'url': 'https://xmrtnet-eliza.onrender.com',
        'status': 'active',
        'last_sync': None
    }
}

# Global state management
system_state = {
    'boardroom_status': 'active',
    'last_update': datetime.utcnow().isoformat(),
    'connected_systems': 0,
    'total_agents': 5,
    'active_sessions': 0,
    'governance_proposals': 0,
    'treasury_balance': 0.0,
    'mining_hashrate': 0.0,
    'system_uptime': 0
}

class XMRTOrchestrator:
    """
    Main orchestration class for coordinating XMRT ecosystem
    """
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.sync_interval = 30  # seconds
        self.is_running = True
        
    def start_orchestration(self):
        """Start the orchestration process"""
        logger.info("Starting XMRT Orchestration...")
        
        # Start background sync thread
        sync_thread = Thread(target=self._sync_loop, daemon=True)
        sync_thread.start()
        
        # Start system monitoring
        monitor_thread = Thread(target=self._monitor_systems, daemon=True)
        monitor_thread.start()
        
    def _sync_loop(self):
        """Main synchronization loop"""
        while self.is_running:
            try:
                self._sync_with_deployed_systems()
                self._update_system_state()
                self._broadcast_updates()
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"Sync loop error: {e}")
                time.sleep(5)
    
    def _sync_with_deployed_systems(self):
        """Synchronize with deployed systems"""
        for system_key, system_info in DEPLOYED_SYSTEMS.items():
            try:
                # Health check
                response = requests.get(f"{system_info['url']}/health", timeout=10)
                if response.status_code == 200:
                    system_info['status'] = 'active'
                    system_info['last_sync'] = datetime.utcnow().isoformat()
                    
                    # Try to get system data
                    if system_key == 'dao_hub':
                        self._sync_dao_hub_data(system_info['url'])
                    elif system_key == 'dashboard':
                        self._sync_dashboard_data(system_info['url'])
                        
                else:
                    system_info['status'] = 'degraded'
                    
            except requests.RequestException as e:
                logger.warning(f"Failed to sync with {system_key}: {e}")
                system_info['status'] = 'offline'
    
    def _sync_dao_hub_data(self, base_url: str):
        """Sync data from DAO Hub"""
        try:
            # Get agent status
            response = requests.get(f"{base_url}/api/agent/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                system_state['total_agents'] = data.get('total_agents', 5)
            
            # Get dashboard data
            response = requests.get(f"{base_url}/api/dashboard", timeout=5)
            if response.status_code == 200:
                data = response.json()
                system_state['active_sessions'] = data.get('active_sessions', 0)
                
        except Exception as e:
            logger.warning(f"Failed to sync DAO Hub data: {e}")
    
    def _sync_dashboard_data(self, base_url: str):
        """Sync data from Dashboard"""
        try:
            # Try to get system metrics (may not exist yet)
            response = requests.get(f"{base_url}/api/metrics", timeout=5)
            if response.status_code == 200:
                data = response.json()
                system_state['mining_hashrate'] = data.get('hashrate', 0.0)
                system_state['system_uptime'] = data.get('uptime', 0)
                
        except Exception as e:
            logger.debug(f"Dashboard metrics not available: {e}")
    
    def _update_system_state(self):
        """Update global system state"""
        system_state['last_update'] = datetime.utcnow().isoformat()
        system_state['connected_systems'] = sum(
            1 for sys in DEPLOYED_SYSTEMS.values() 
            if sys['status'] == 'active'
        )
        
        # Calculate uptime
        uptime_delta = datetime.utcnow() - self.start_time
        system_state['system_uptime'] = int(uptime_delta.total_seconds())
        
        # Cache state in Redis if available
        if redis_client:
            try:
                redis_client.setex('xmrt:system_state', 60, json.dumps(system_state, default=str))
            except Exception as e:
                logger.warning(f"Failed to cache system state: {e}")
    
    def _broadcast_updates(self):
        """Broadcast updates to connected clients"""
        try:
            socketio.emit('system_update', system_state, namespace='/')
        except Exception as e:
            logger.warning(f"Failed to broadcast updates: {e}")
    
    def _monitor_systems(self):
        """Monitor system health and performance"""
        while self.is_running:
            try:
                # Monitor memory usage, connections, etc.
                # This is a placeholder for more sophisticated monitoring
                time.sleep(60)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")

# Initialize orchestrator
orchestrator = XMRTOrchestrator()

# HTML template for the boardroom interface
BOARDROOM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Boardroom - Orchestration Hub</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.8; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card h3 { margin-bottom: 15px; color: #4CAF50; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .metric-value { font-weight: bold; color: #FFD700; }
        .status-indicator { 
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background-color: #4CAF50; }
        .status-degraded { background-color: #FF9800; }
        .status-offline { background-color: #F44336; }
        .system-links { margin-top: 20px; }
        .system-links a {
            display: inline-block;
            margin: 5px 10px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
        }
        .system-links a:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        .log-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
        }
        .log-entry {
            margin-bottom: 5px;
            opacity: 0.8;
        }
        .timestamp {
            color: #4CAF50;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ XMRT Boardroom</h1>
            <p>Orchestration Hub for the XMRT Ecosystem</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>🎯 System Overview</h3>
                <div class="metric">
                    <span>Boardroom Status:</span>
                    <span class="metric-value" id="boardroom-status">Active</span>
                </div>
                <div class="metric">
                    <span>Connected Systems:</span>
                    <span class="metric-value" id="connected-systems">0/2</span>
                </div>
                <div class="metric">
                    <span>System Uptime:</span>
                    <span class="metric-value" id="system-uptime">0s</span>
                </div>
                <div class="metric">
                    <span>Last Update:</span>
                    <span class="metric-value" id="last-update">Never</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 AI Agents</h3>
                <div class="metric">
                    <span>Total Agents:</span>
                    <span class="metric-value" id="total-agents">5</span>
                </div>
                <div class="metric">
                    <span>Active Sessions:</span>
                    <span class="metric-value" id="active-sessions">0</span>
                </div>
                <div class="metric">
                    <span>Mining Hashrate:</span>
                    <span class="metric-value" id="mining-hashrate">0 H/s</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🏛️ DAO Governance</h3>
                <div class="metric">
                    <span>Active Proposals:</span>
                    <span class="metric-value" id="governance-proposals">0</span>
                </div>
                <div class="metric">
                    <span>Treasury Balance:</span>
                    <span class="metric-value" id="treasury-balance">$0.00</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🔗 Connected Systems</h3>
                <div id="system-status">
                    <div class="metric">
                        <span><span class="status-indicator status-offline"></span>Dashboard</span>
                        <span class="metric-value">Connecting...</span>
                    </div>
                    <div class="metric">
                        <span><span class="status-indicator status-offline"></span>DAO Hub</span>
                        <span class="metric-value">Connecting...</span>
                    </div>
                </div>
                
                <div class="system-links">
                    <a href="https://xmrt-ecosystem-redis-langgraph.onrender.com/" target="_blank">📊 Dashboard</a>
                    <a href="https://xmrtnet-eliza.onrender.com" target="_blank">🏛️ DAO Hub</a>
                </div>
            </div>
            
            <div class="card">
                <h3>📋 System Log</h3>
                <div class="log-container" id="system-log">
                    <div class="log-entry">
                        <span class="timestamp">[INIT]</span>
                        <span>XMRT Boardroom initializing...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Add log entry function
        function addLogEntry(message) {
            const logContainer = document.getElementById('system-log');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span><span>${message}</span>`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Keep only last 50 entries
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
        
        // Socket event handlers
        socket.on('connect', function() {
            addLogEntry('Connected to XMRT Boardroom');
        });
        
        socket.on('system_update', function(data) {
            // Update system overview
            document.getElementById('boardroom-status').textContent = data.boardroom_status || 'Active';
            document.getElementById('connected-systems').textContent = `${data.connected_systems || 0}/2`;
            document.getElementById('system-uptime').textContent = formatUptime(data.system_uptime || 0);
            document.getElementById('last-update').textContent = formatTime(data.last_update);
            
            // Update AI agents
            document.getElementById('total-agents').textContent = data.total_agents || 5;
            document.getElementById('active-sessions').textContent = data.active_sessions || 0;
            document.getElementById('mining-hashrate').textContent = `${data.mining_hashrate || 0} H/s`;
            
            // Update governance
            document.getElementById('governance-proposals').textContent = data.governance_proposals || 0;
            document.getElementById('treasury-balance').textContent = `$${(data.treasury_balance || 0).toFixed(2)}`;
            
            addLogEntry(`System state updated - ${data.connected_systems || 0} systems connected`);
        });
        
        // Utility functions
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return `${hours}h ${minutes}m ${secs}s`;
        }
        
        function formatTime(isoString) {
            if (!isoString) return 'Never';
            return new Date(isoString).toLocaleTimeString();
        }
        
        // Initial log entry
        addLogEntry('XMRT Boardroom interface loaded');
        
        // Request initial system state
        fetch('/api/system/status')
            .then(response => response.json())
            .then(data => {
                socket.emit('system_update', data);
            })
            .catch(error => {
                addLogEntry(`Error loading initial state: ${error.message}`);
            });
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    """Main boardroom interface"""
    return render_template_string(BOARDROOM_TEMPLATE)

@app.route('/')
def index():
    """Main boardroom interface"""
    return render_template_string(BOARDROOM_TEMPLATE)



@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'XMRT Boardroom',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': system_state['system_uptime']
    })



@app.route('/api/system/status')
def system_status():
    """Get current system status"""
    return jsonify(system_state)



@app.route('/api/systems/connected')
def connected_systems():
    """Get status of connected systems"""
    return jsonify(DEPLOYED_SYSTEMS)



@app.route('/api/orchestration/sync', methods=['POST'])
def trigger_sync():
    """Manually trigger synchronization"""
    try:
        orchestrator._sync_with_deployed_systems()
        orchestrator._update_system_state()
        return jsonify({
            'status': 'success',
            'message': 'Synchronization triggered',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500



@app.route('/api/events/publish', methods=['POST'])
def publish_event():
    """Publish event to the event bus"""
    try:
        data = request.get_json()
        event_type = data.get('type')
        event_data = data.get('data', {})
        
        # Broadcast to all connected clients
        socketio.emit('event', {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Store in Redis if available
        if redis_client:
            redis_client.lpush('xmrt:events', json.dumps({
                'type': event_type,
                'data': event_data,
                'timestamp': datetime.utcnow().isoformat()
            }))
            redis_client.ltrim('xmrt:events', 0, 99)  # Keep last 100 events
        
        return jsonify({'status': 'published'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/events/history')
def event_history():
    """Get recent event history"""
    try:
        if redis_client:
            events = redis_client.lrange('xmrt:events', 0, 49)  # Last 50 events
            return jsonify([json.loads(event) for event in events])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket events


# Enhanced Routes for Growth System (Optional)
@app.route('/api/growth/status')
def growth_system_status():
    """Get growth system status"""
    return jsonify({
        "enabled": ENABLE_GROWTH_SYSTEM,
        "available": GROWTH_SYSTEM_AVAILABLE,
        "redis_connected": REDIS_AVAILABLE
    })

@app.route('/api/growth/plan')
def get_growth_plan():
    """Get current growth plan (if growth system is enabled)"""
    if not ENABLE_GROWTH_SYSTEM:
        return jsonify({"error": "Growth system disabled"}), 503
    
    if not GROWTH_SYSTEM_AVAILABLE or not eliza_growth:
        return jsonify({"error": "Growth system not available"}), 503
    
    try:
        plan = eliza_growth.create_growth_plan()
        return jsonify(plan)
    except Exception as e:
        logger.error(f"Growth plan generation failed: {e}")
        return jsonify({"error": "Growth plan unavailable"}), 500

@app.route('/api/growth/execute', methods=['POST'])
def execute_growth_initiative():
    """Execute a specific growth initiative (if growth system is enabled)"""
    if not ENABLE_GROWTH_SYSTEM:
        return jsonify({"error": "Growth system disabled"}), 503
    
    if not GROWTH_SYSTEM_AVAILABLE or not eliza_growth:
        return jsonify({"error": "Growth system not available"}), 503
    
    try:
        data = request.get_json()
        initiative_type = data.get('type', 'user_acquisition')
        
        # Generate and execute initiative
        assessment = eliza_growth.assess_current_state()
        initiatives = eliza_growth.generate_autonomous_initiatives(assessment)
        
        # Find matching initiative
        for initiative in initiatives:
            if initiative['area'] == initiative_type:
                result = eliza_growth.execute_initiative(initiative)
                return jsonify(result)
        
        return jsonify({"error": "No matching initiative found"}), 404
        
    except Exception as e:
        logger.error(f"Growth initiative execution failed: {e}")
        return jsonify({"error": "Execution failed"}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to XMRT Boardroom'})



@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")



@socketio.on('join_room')
def handle_join_room(data):
    """Handle room joining for targeted updates"""
    room = data.get('room', 'general')
    join_room(room)
    emit('joined_room', {'room': room})



@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle room leaving"""
    room = data.get('room', 'general')
    leave_room(room)
    emit('left_room', {'room': room})



# Enhanced SocketIO handlers for Growth System
@socketio.on('request_growth_update')
def handle_growth_update():
    """Handle request for growth update"""
    if GROWTH_SYSTEM_AVAILABLE and eliza_growth:
        try:
            assessment = eliza_growth.assess_current_state()
            emit('growth_update', assessment)
        except Exception as e:
            logger.warning(f"Growth update failed: {e}")
            emit('growth_update', {"error": "Growth update unavailable"})

def start_autonomous_growth_loop():
    """Start Eliza's autonomous growth loop in background (if enabled)"""
    if not ENABLE_GROWTH_SYSTEM or not GROWTH_SYSTEM_AVAILABLE or not eliza_growth:
        logger.info("Autonomous growth loop not started (disabled or unavailable)")
        return
    
    logger.info("🚀 Starting Eliza's Autonomous Growth Loop")
    
    def growth_loop():
        while True:
            try:
                # Check if growth system is still enabled
                if not ENABLE_GROWTH_SYSTEM:
                    logger.info("Growth system disabled, stopping loop")
                    break
                
                # Daily growth assessment and execution
                assessment = eliza_growth.assess_current_state()
                initiatives = eliza_growth.generate_autonomous_initiatives(assessment)
                
                # Execute top priority initiatives
                for initiative in initiatives[:2]:  # Execute top 2
                    if initiative["urgency"] in ["high", "medium"]:
                        logger.info(f"🤖 Eliza executing: {initiative['strategy']}")
                        result = eliza_growth.execute_initiative(initiative)
                        
                        # Broadcast to connected clients
                        socketio.emit('growth_activity', {
                            'initiative': initiative['strategy'],
                            'result': result,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Save to Redis if available
                        if REDIS_AVAILABLE and redis_client:
                            try:
                                redis_client.setex(
                                    f"growth_activity_{int(time.time())}", 
                                    86400, 
                                    json.dumps(result, default=str)
                                )
                            except Exception as e:
                                logger.warning(f"Could not save to Redis: {e}")
                
                # Sleep for next cycle (6 hours for demo, 24 hours for production)
                time.sleep(6 * 60 * 60)  # 6 hours
                
            except Exception as e:
                logger.error(f"Error in growth loop: {e}")
                time.sleep(60 * 60)  # Wait 1 hour before retry
    
    # Start growth loop in background thread
    growth_thread = Thread(target=growth_loop, daemon=True)
    growth_thread.start()

BOARDROOM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Boardroom - Orchestration Hub</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.8; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .card h3 { margin-bottom: 15px; color: #4CAF50; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 10px; }
        .metric-value { font-weight: bold; color: #FFD700; }
        .status-indicator { 
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-active { background-color: #4CAF50; }
        .status-degraded { background-color: #FF9800; }
        .status-offline { background-color: #F44336; }
        .system-links { margin-top: 20px; }
        .system-links a {
            display: inline-block;
            margin: 5px 10px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
        }
        .system-links a:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        .log-container {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
        }
        .log-entry {
            margin-bottom: 5px;
            opacity: 0.8;
        }
        .timestamp {
            color: #4CAF50;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ XMRT Boardroom</h1>
            <p>Orchestration Hub for the XMRT Ecosystem</p>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>🎯 System Overview</h3>
                <div class="metric">
                    <span>Boardroom Status:</span>
                    <span class="metric-value" id="boardroom-status">Active</span>
                </div>
                <div class="metric">
                    <span>Connected Systems:</span>
                    <span class="metric-value" id="connected-systems">0/2</span>
                </div>
                <div class="metric">
                    <span>System Uptime:</span>
                    <span class="metric-value" id="system-uptime">0s</span>
                </div>
                <div class="metric">
                    <span>Last Update:</span>
                    <span class="metric-value" id="last-update">Never</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 AI Agents</h3>
                <div class="metric">
                    <span>Total Agents:</span>
                    <span class="metric-value" id="total-agents">5</span>
                </div>
                <div class="metric">
                    <span>Active Sessions:</span>
                    <span class="metric-value" id="active-sessions">0</span>
                </div>
                <div class="metric">
                    <span>Mining Hashrate:</span>
                    <span class="metric-value" id="mining-hashrate">0 H/s</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🏛️ DAO Governance</h3>
                <div class="metric">
                    <span>Active Proposals:</span>
                    <span class="metric-value" id="governance-proposals">0</span>
                </div>
                <div class="metric">
                    <span>Treasury Balance:</span>
                    <span class="metric-value" id="treasury-balance">$0.00</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🔗 Connected Systems</h3>
                <div id="system-status">
                    <div class="metric">
                        <span><span class="status-indicator status-offline"></span>Dashboard</span>
                        <span class="metric-value">Connecting...</span>
                    </div>
                    <div class="metric">
                        <span><span class="status-indicator status-offline"></span>DAO Hub</span>
                        <span class="metric-value">Connecting...</span>
                    </div>
                </div>
                
                <div class="system-links">
                    <a href="https://xmrt-ecosystem-redis-langgraph.onrender.com/" target="_blank">📊 Dashboard</a>
                    <a href="https://xmrtnet-eliza.onrender.com" target="_blank">🏛️ DAO Hub</a>
                </div>
            </div>
            
            <div class="card">
                <h3>📋 System Log</h3>
                <div class="log-container" id="system-log">
                    <div class="log-entry">
                        <span class="timestamp">[INIT]</span>
                        <span>XMRT Boardroom initializing...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize Socket.IO connection
        const socket = io();
        
        // Add log entry function
        function addLogEntry(message) {
            const logContainer = document.getElementById('system-log');
            const timestamp = new Date().toLocaleTimeString();
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            logEntry.innerHTML = `<span class="timestamp">[${timestamp}]</span><span>${message}</span>`;
            logContainer.appendChild(logEntry);
            logContainer.scrollTop = logContainer.scrollHeight;
            
            // Keep only last 50 entries
            while (logContainer.children.length > 50) {
                logContainer.removeChild(logContainer.firstChild);
            }
        }
        
        // Socket event handlers
        socket.on('connect', function() {
            addLogEntry('Connected to XMRT Boardroom');
        });
        
        socket.on('system_update', function(data) {
            // Update system overview
            document.getElementById('boardroom-status').textContent = data.boardroom_status || 'Active';
            document.getElementById('connected-systems').textContent = `${data.connected_systems || 0}/2`;
            document.getElementById('system-uptime').textContent = formatUptime(data.system_uptime || 0);
            document.getElementById('last-update').textContent = formatTime(data.last_update);
            
            // Update AI agents
            document.getElementById('total-agents').textContent = data.total_agents || 5;
            document.getElementById('active-sessions').textContent = data.active_sessions || 0;
            document.getElementById('mining-hashrate').textContent = `${data.mining_hashrate || 0} H/s`;
            
            // Update governance
            document.getElementById('governance-proposals').textContent = data.governance_proposals || 0;
            document.getElementById('treasury-balance').textContent = `$${(data.treasury_balance || 0).toFixed(2)}`;
            
            addLogEntry(`System state updated - ${data.connected_systems || 0} systems connected`);
        });
        
        // Utility functions
        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return `${hours}h ${minutes}m ${secs}s`;
        }
        
        function formatTime(isoString) {
            if (!isoString) return 'Never';
            return new Date(isoString).toLocaleTimeString();
        }
        
        // Initial log entry
        addLogEntry('XMRT Boardroom interface loaded');
        
        // Request initial system state
        fetch('/api/system/status')
            .then(response => response.json())
            .then(data => {
                socket.emit('system_update', data);
            })
            .catch(error => {
                addLogEntry(`Error loading initial state: ${error.message}`);
            });
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    """Main boardroom interface"""
    return render_template_string(BOARDROOM_TEMPLATE)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'XMRT Boardroom',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': system_state['system_uptime']
    })

@app.route('/api/system/status')
def system_status():
    """Get current system status"""
    return jsonify(system_state)

@app.route('/api/systems/connected')
def connected_systems():
    """Get status of connected systems"""
    return jsonify(DEPLOYED_SYSTEMS)

@app.route('/api/orchestration/sync', methods=['POST'])
def trigger_sync():
    """Manually trigger synchronization"""
    try:
        orchestrator._sync_with_deployed_systems()
        orchestrator._update_system_state()
        return jsonify({
            'status': 'success',
            'message': 'Synchronization triggered',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/events/publish', methods=['POST'])
def publish_event():
    """Publish event to the event bus"""
    try:
        data = request.get_json()
        event_type = data.get('type')
        event_data = data.get('data', {})
        
        # Broadcast to all connected clients
        socketio.emit('event', {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Store in Redis if available
        if redis_client:
            redis_client.lpush('xmrt:events', json.dumps({
                'type': event_type,
                'data': event_data,
                'timestamp': datetime.utcnow().isoformat()
            }))
            redis_client.ltrim('xmrt:events', 0, 99)  # Keep last 100 events
        
        return jsonify({'status': 'published'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/history')
def event_history():
    """Get recent event history"""
    try:
        if redis_client:
            events = redis_client.lrange('xmrt:events', 0, 49)  # Last 50 events
            return jsonify([json.loads(event) for event in events])
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to XMRT Boardroom'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    """Handle room joining for targeted updates"""
    room = data.get('room', 'general')
    join_room(room)
    emit('joined_room', {'room': room})

@socketio.on('leave_room')
def handle_leave_room(data):
    """Handle room leaving"""
    room = data.get('room', 'general')
    leave_room(room)
    emit('left_room', {'room': room})



# Enhanced main section with growth system
if __name__ == '__main__':
    # Initialize orchestrator
    orchestrator = XMRTOrchestrator()
    orchestrator.start_orchestration()
    
    # Start autonomous growth loop (if enabled)
    start_autonomous_growth_loop()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
