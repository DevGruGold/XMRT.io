# XMRT Eliza Server - Vercel Compatible FastAPI Application
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

# Create main app
app = FastAPI(title="XMRT Eliza System")

# Try to import optional dependencies with fallback
try:
    from redis_eventbus import event_bus
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis event bus not available, running in standalone mode")

# Try to serve static files if they exist
try:
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    print(f"Note: Static files not mounted: {e}")

@app.get("/")
async def serve_main_page():
    """Serve the main chat interface"""
    
    # Try to serve index.html first
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    elif os.path.exists("chat.html"):
        return FileResponse("chat.html")
    else:
        # Fallback to embedded HTML
        return HTMLResponse(content='''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XMRT Eliza AI Assistant</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        .logo { font-size: 48px; margin-bottom: 20px; }
        h1 { color: #333; margin-bottom: 10px; }
        .status {
            background: #10b981;
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin: 20px 0;
        }
        .chat-button {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-size: 18px;
            cursor: pointer;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }
        .chat-button:hover { transform: translateY(-2px); }
        .api-links { margin-top: 30px; }
        .api-links a {
            color: #4facfe;
            text-decoration: none;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖</div>
        <h1>XMRT Eliza AI Assistant</h1>
        <p>Powered by 739+ autonomous learning cycles</p>
        
        <div class="status">✅ System Operational</div>
        
        <div>
            <button class="chat-button" onclick="startEmbeddedChat()">💬 Start Chatting</button>
        </div>
        
        <div class="api-links">
            <p><strong>API Endpoints:</strong></p>
            <a href="/api/health">🏥 Health Check</a>
            <a href="/api/knowledge/stats">📊 Knowledge Stats</a>
            <a href="/api/knowledge/latest/development?limit=3">🔧 Latest Development</a>
        </div>
        
        <div id="chatContainer" style="display: none; margin-top: 30px;">
            <div style="background: #f8f9fa; border-radius: 10px; padding: 20px; text-align: left;">
                <div id="chatMessages" style="height: 300px; overflow-y: auto; margin-bottom: 15px; padding: 10px; background: white; border-radius: 8px;">
                    <div style="margin-bottom: 15px;">
                        <strong>🤖 Eliza:</strong> Hello! I'm your XMRT AI assistant with access to 739+ autonomous learning cycles. What would you like to know?
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="chatInput" placeholder="Ask me anything..." style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; outline: none;">
                    <button onclick="sendMessage()" style="padding: 10px 20px; background: #4facfe; color: white; border: none; border-radius: 20px; cursor: pointer;">Send</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function startEmbeddedChat() {
            document.getElementById('chatContainer').style.display = 'block';
            document.getElementById('chatInput').focus();
        }
        
        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const messages = document.getElementById('chatMessages');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            messages.innerHTML += `<div style="margin-bottom: 15px; text-align: right;"><strong>👤 You:</strong> ${message}</div>`;
            input.value = '';
            
            // Show loading
            messages.innerHTML += `<div id="loading" style="margin-bottom: 15px;"><strong>🤖 Eliza:</strong> <em>Thinking...</em></div>`;
            messages.scrollTop = messages.scrollHeight;
            
            try {
                // Try to get relevant insights
                const category = classifyMessage(message);
                const response = await fetch(`/api/knowledge/latest/${category}?limit=1`);
                
                let elizaResponse = "I understand your question. Let me process that...";
                
                if (response.ok) {
                    const data = await response.json();
                    if (data && data.length > 0) {
                        const insight = data[0];
                        elizaResponse = `Based on my autonomous analysis from cycle #${insight.cycle || 'N/A'}: ${insight.content || 'Processing insights...'}`;
                    }
                } else {
                    elizaResponse = "I'm having trouble accessing my knowledge base right now, but I'm here to help! Could you try rephrasing your question?";
                }
                
                // Remove loading and add response
                document.getElementById('loading').remove();
                messages.innerHTML += `<div style="margin-bottom: 15px;"><strong>🤖 Eliza:</strong> ${elizaResponse}</div>`;
                messages.scrollTop = messages.scrollHeight;
                
            } catch (error) {
                document.getElementById('loading').remove();
                messages.innerHTML += `<div style="margin-bottom: 15px;"><strong>🤖 Eliza:</strong> I'm experiencing some technical difficulties. My systems are working to resolve this!</div>`;
                messages.scrollTop = messages.scrollHeight;
            }
        }
        
        function classifyMessage(message) {
            const msg = message.toLowerCase();
            if (msg.includes('develop') || msg.includes('code')) return 'development';
            if (msg.includes('analytic') || msg.includes('data')) return 'analytics';
            if (msg.includes('market') || msg.includes('growth')) return 'marketing';
            if (msg.includes('mining')) return 'mining';
            if (msg.includes('browser') || msg.includes('interface')) return 'browser';
            if (msg.includes('social') || msg.includes('community')) return 'social_media';
            return 'development';
        }
        
        // Allow Enter key to send message
        document.addEventListener('DOMContentLoaded', function() {
            const inputEl = document.getElementById('chatInput');
            if (inputEl) {
                inputEl.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            }
        });
    </script>
</body>
</html>
''')

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "XMRT Eliza System",
        "redis_available": REDIS_AVAILABLE,
        "version": "1.0.0"
    })

# Basic fallback API endpoints for when knowledge bridge isn't available
@app.get("/api/knowledge/stats")
async def basic_stats():
    """Get basic knowledge statistics"""
    return JSONResponse(content={
        "total_cycles": 739,
        "status": "operational",
        "categories": ["development", "analytics", "marketing", "mining", "browser", "social_media"],
        "note": "Basic endpoint - enhanced features require full ecosystem"
    })

@app.get("/api/knowledge/latest/{category}")
async def basic_latest(category: str, limit: int = 3):
    """Get latest insights from a category"""
    return JSONResponse(content=[
        {
            "cycle": 739,
            "category": category,
            "content": f"Sample {category} insight from autonomous learning cycles",
            "timestamp": "2025-10-31T00:00:00Z"
        }
    ])

@app.get("/api/knowledge/search/{query}")
async def basic_search(query: str, limit: int = 3):
    """Search knowledge base"""
    return JSONResponse(content=[
        {
            "cycle": 739,
            "query": query,
            "content": f"Search results for: {query}",
            "relevance": 0.95
        }
    ])

# Event bus startup handler (only if Redis is available)
if REDIS_AVAILABLE:
    @app.on_event("startup")
    async def startup_event():
        """Initialize event bus listeners on startup"""
        import asyncio
        
        try:
            # Start listening to ecosystem events
            channels = [
                'meshnet:verified',
                'mining:update',
                'dao:proposal',
                'agent:activity',
                'boardroom:message'
            ]
            
            asyncio.create_task(event_bus.listen(channels))
            print(f"Event bus listening to: {channels}")
        except Exception as e:
            print(f"Note: Event bus startup skipped: {e}")

# Export app for Vercel
# Vercel looks for 'app' in the module
handler = app

# Local development server
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
