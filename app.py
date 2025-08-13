from webhook_endpoints import create_ecosystem_webhook_blueprint
import requests
import time
#!/usr/bin/env python3
"""
XMRT Boardroom Flask Application - Fixed Version
================================================

Fixed version that preserves all original functionality while adding
optional growth system without conflicts.

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

# Initialize Flask app
app = Flask(__name__)

# Register ecosystem webhook blueprint
ecosystem_webhook_bp = create_ecosystem_webhook_blueprint()
app.register_blueprint(ecosystem_webhook_bp)

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

# System configuration (preserved from original)
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

# Global state management (preserved from original)
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
    Main orchestration class for coordinating XMRT ecosystem (preserved from original)
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
    
    def _monitor_systems(self):
        """Monitor system health"""
        while self.is_running:
            try:
                # Monitor system health
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(10)
    
    def _sync_with_deployed_systems(self):
        """Sync with deployed systems"""
        for system_id, system_info in DEPLOYED_SYSTEMS.items():
            try:
                response = requests.get(f"{system_info['url']}/api/health", timeout=5)
                if response.status_code == 200:
                    system_info['status'] = 'active'
                    system_info['last_sync'] = datetime.utcnow().isoformat()
                else:
                    system_info['status'] = 'degraded'
            except Exception as e:
                logger.warning(f"Failed to sync with {system_id}: {e}")
                system_info['status'] = 'offline'
    
    def _update_system_state(self):
        """Update system state"""
        system_state['last_update'] = datetime.utcnow().isoformat()
        system_state['connected_systems'] = len([s for s in DEPLOYED_SYSTEMS.values() if s['status'] == 'active'])
        system_state['system_uptime'] = int((datetime.utcnow() - self.start_time).total_seconds())
    
    def _broadcast_updates(self):
        """Broadcast updates to connected clients"""
        if REDIS_AVAILABLE and redis_client:
            try:
                redis_client.publish('system_updates', json.dumps(system_state, default=str))
            except Exception as e:
                logger.warning(f"Failed to broadcast updates: {e}")

# Enhanced Boardroom Template with Growth System Integration
BOARDROOM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Boardroom - Enhanced</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
        }
        .header h1 { 
            font-size: 2.5em; 
            margin: 0; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle { 
            font-size: 1.2em; 
            opacity: 0.9; 
            margin-top: 10px;
        }
        .dashboard { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }
        .card { 
            background: rgba(255,255,255,0.15); 
            border-radius: 10px; 
            padding: 20px; 
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 { 
            margin-top: 0; 
            color: #fff; 
            font-size: 1.3em;
        }
        .metric { 
            display: flex; 
            justify-content: space-between; 
            margin: 10px 0; 
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .metric:last-child { 
            border-bottom: none; 
        }
        .metric-value { 
            font-weight: bold; 
            color: #4ade80;
        }
        .status-indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-right: 8px;
        }
        .status-online { 
            background-color: #4ade80; 
        }
        .status-offline { 
            background-color: #ef4444; 
        }
        .status-disabled { 
            background-color: #fbbf24; 
        }
        .btn { 
            background: linear-gradient(45deg, #4ade80, #22c55e); 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1em;
            margin: 5px;
            transition: all 0.3s ease;
        }
        .btn:hover { 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .btn:disabled {
            background: #6b7280;
            cursor: not-allowed;
            transform: none;
        }
        .growth-section {
            display: none;
        }
        .growth-section.enabled {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ XMRT Boardroom</h1>
            <div class="subtitle">Autonomous Ecosystem Orchestration Hub</div>
        </div>
        
        <div class="dashboard">
            <div class="card">
                <h3>🔧 System Status</h3>
                <div class="metric">
                    <span><span class="status-indicator" id="redis-status"></span>Redis Connection</span>
                    <span class="metric-value" id="redis-text">Checking...</span>
                </div>
                <div class="metric">
                    <span><span class="status-indicator" id="growth-status"></span>Growth System</span>
                    <span class="metric-value" id="growth-text">Checking...</span>
                </div>
                <div class="metric">
                    <span><span class="status-indicator status-online"></span>Boardroom</span>
                    <span class="metric-value">Operational</span>
                </div>
            </div>
            
            <div class="card growth-section" id="growth-metrics">
                <h3>🎯 Growth Metrics</h3>
                <div class="metric">
                    <span>Overall Health</span>
                    <span class="metric-value" id="overall-health">--</span>
                </div>
                <div class="metric">
                    <span>Motivation Level</span>
                    <span class="metric-value" id="motivation-level">--</span>
                </div>
                <div class="metric">
                    <span>Active Opportunities</span>
                    <span class="metric-value" id="opportunities">--</span>
                </div>
            </div>
            
            <div class="card growth-section" id="growth-controls">
                <h3>🚀 Growth Actions</h3>
                <button class="btn" onclick="executeGrowthInitiative('user_acquisition')">
                    Boost User Acquisition
                </button>
                <button class="btn" onclick="executeGrowthInitiative('ecosystem_improvement')">
                    Improve Ecosystem
                </button>
                <button class="btn" onclick="executeGrowthInitiative('community_engagement')">
                    Engage Community
                </button>
                <button class="btn" onclick="requestGrowthUpdate()">
                    Refresh Metrics
                </button>
            </div>
        </div>
        
        <div class="card">
            <h3>📊 System Activity</h3>
            <div id="activity-log">
                <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; border-left: 4px solid #4ade80;">
                    <strong>🏛️ XMRT Boardroom Initialized</strong><br>
                    Orchestration hub is operational and monitoring the ecosystem.
                    <div style="font-size: 0.8em; opacity: 0.7;">Just now</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let growthSystemEnabled = false;
        
        socket.on('connect', function() {
            console.log('Connected to XMRT Boardroom');
            requestSystemStatus();
        });
        
        socket.on('growth_update', function(data) {
            if (growthSystemEnabled) {
                updateGrowthMetrics(data);
            }
        });
        
        function requestSystemStatus() {
            fetch('/api/system/status')
                .then(response => response.json())
                .then(data => {
                    updateSystemStatus(data);
                });
        }
        
        function requestGrowthUpdate() {
            if (growthSystemEnabled) {
                socket.emit('request_growth_update');
            }
        }
        
        function executeGrowthInitiative(type) {
            if (!growthSystemEnabled) {
                alert('Growth system is not enabled');
                return;
            }
            
            fetch('/api/growth/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({type: type})
            })
            .then(response => response.json())
            .then(data => {
                console.log('Growth initiative result:', data);
            });
        }
        
        function updateSystemStatus(data) {
            // Update Redis status
            const redisStatus = document.getElementById('redis-status');
            const redisText = document.getElementById('redis-text');
            if (data.redis_connected) {
                redisStatus.className = 'status-indicator status-online';
                redisText.textContent = 'Connected';
            } else {
                redisStatus.className = 'status-indicator status-offline';
                redisText.textContent = 'Disconnected';
            }
            
            // Update Growth System status
            const growthStatus = document.getElementById('growth-status');
            const growthText = document.getElementById('growth-text');
            
            growthSystemEnabled = data.growth_system_enabled && data.growth_system_active;
            
            if (data.growth_system_enabled) {
                if (data.growth_system_active) {
                    growthStatus.className = 'status-indicator status-online';
                    growthText.textContent = 'Active';
                    showGrowthSections();
                } else {
                    growthStatus.className = 'status-indicator status-offline';
                    growthText.textContent = 'Error';
                }
            } else {
                growthStatus.className = 'status-indicator status-disabled';
                growthText.textContent = 'Disabled';
            }
            
            // Update growth metrics if available
            if (data.growth_metrics && !data.growth_metrics.error) {
                updateGrowthMetrics(data.growth_metrics);
            }
        }
        
        function showGrowthSections() {
            document.querySelectorAll('.growth-section').forEach(section => {
                section.classList.add('enabled');
            });
        }
        
        function updateGrowthMetrics(data) {
            if (data.overall_health !== undefined) {
                document.getElementById('overall-health').textContent = 
                    (data.overall_health * 100).toFixed(1) + '%';
            }
            
            if (data.motivation_level !== undefined) {
                document.getElementById('motivation-level').textContent = 
                    (data.motivation_level * 100).toFixed(1) + '%';
            }
            
            if (data.growth_opportunities !== undefined) {
                document.getElementById('opportunities').textContent = data.growth_opportunities;
            }
        }
        
        // Auto-refresh system status every 30 seconds
        setInterval(requestSystemStatus, 30000);
    </script>
</body>
</html>
"""

# Flask Routes (preserved from original with enhancements)

@app.route('/')
def index():
    """Main boardroom interface (preserved from original)"""
    return render_template_string(BOARDROOM_TEMPLATE)

@app.route('/api/system/status')
def system_status():
    """Get system status (enhanced with growth metrics)"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "redis_connected": REDIS_AVAILABLE,
        "boardroom_status": "operational",
        "growth_system_enabled": ENABLE_GROWTH_SYSTEM,
        "growth_system_active": GROWTH_SYSTEM_AVAILABLE
    }
    
    # Add growth metrics if available
    if GROWTH_SYSTEM_AVAILABLE and eliza_growth:
        try:
            assessment = eliza_growth.assess_current_state()
            status["growth_metrics"] = {
                "overall_health": assessment["overall_health"],
                "motivation_level": assessment["motivation_level"],
                "growth_opportunities": len(assessment["growth_opportunities"])
            }
        except Exception as e:
            logger.warning(f"Growth metrics unavailable: {e}")
    
    return jsonify(status)

@app.route('/api/orchestration/status')
def orchestration_status():
    """Get orchestration status (preserved from original)"""
    return jsonify({
        "status": "active",
        "connected_systems": len(DEPLOYED_SYSTEMS),
        "last_update": datetime.now().isoformat(),
        "deployed_systems": DEPLOYED_SYSTEMS,
        "system_state": system_state
    })

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

# SocketIO handlers (preserved from original)

@socketio.on('connect')
def handle_connect():
    """Handle client connection (preserved from original)"""
    logger.info("Client connected to boardroom")
    emit('status', {'message': 'Connected to XMRT Boardroom'})
    
    # Send growth system status if available
    if GROWTH_SYSTEM_AVAILABLE and eliza_growth:
        try:
            assessment = eliza_growth.assess_current_state()
            emit('growth_update', assessment)
        except Exception as e:
            logger.warning(f"Could not send growth update: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection (preserved from original)"""
    logger.info("Client disconnected from boardroom")

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

# Main execution (preserved from original with enhancements)
if __name__ == '__main__':
    # Initialize orchestrator
    orchestrator = XMRTOrchestrator()
    orchestrator.start_orchestration()
    
    # Start autonomous growth loop (if enabled)
    start_autonomous_growth_loop()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

def broadcast_boardroom_activity(event_type, data):
    """Broadcast boardroom activities to ecosystem"""
    try:
        activity = {
            "source_system": "boardroom",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "event_id": f"boardroom_{event_type}_{int(time.time())}"
        }
        
        ecosystem_endpoints = [
            "https://xmrtnet-eliza.onrender.com/api/webhook/receive",
            "https://xmrt-ecosystem-redis-langgraph.onrender.com/api/webhook/receive"
        ]
        
        for endpoint in ecosystem_endpoints:
            try:
                requests.post(endpoint, json=activity, timeout=5)
            except Exception as e:
                print(f"Failed to broadcast to {endpoint}: {e}")
                
    except Exception as e:
        print(f"Error broadcasting activity: {e}")

@app.route('/api/activity/feed', methods=['GET'])
def get_activity_feed():
    """Get activity feed for ecosystem widget"""
    try:
        activities = []
        
        # Add growth metrics activity
        if 'eliza_growth' in globals() and eliza_growth:
            try:
                assessment = eliza_growth.assess_current_state()
                activities.append({
                    "id": f"growth_{int(time.time())}",
                    "title": "📈 Growth Metrics Updated",
                    "description": f"Overall health: {assessment.get('overall_health', 'Unknown')}",
                    "source": "boardroom",
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "growth_update",
                    "data": assessment
                })
            except:
                pass
        
        # Add system status activity
        activities.append({
            "id": f"status_{int(time.time())}",
            "title": "🏛️ Boardroom Status",
            "description": "Orchestration hub operational and monitoring ecosystem",
            "source": "boardroom", 
            "timestamp": datetime.utcnow().isoformat(),
            "type": "system_status",
            "data": {"status": "operational"}
        })
        
        return jsonify({
            "success": True,
            "activities": activities[-10:]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
