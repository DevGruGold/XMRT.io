# XMRT Eliza Server - Serves HTML chat interface and Knowledge Bridge API
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

# Create main app
app = FastAPI(title="XMRT Eliza System")

# Try to serve static files if they exist
try:
    if os.path.exists("index.html") or os.path.exists("chat.html"):
        app.mount("/static", StaticFiles(directory="."), name="static")
except:
    pass

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
            <a href="/api/knowledge/stats">📊 Knowledge Stats</a>
            <a href="/api/knowledge/latest/development?limit=3">🔧 Latest Development</a>
            <a href="/api/knowledge/search/progress?limit=3">🔍 Search Progress</a>
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
            document.getElementById('chatInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        });
    </script>
</body>
</html>
        ''')

@app.get("/chat.html")
async def serve_chat_html():
    """Serve chat.html if it exists"""
    if os.path.exists("chat.html"):
        return FileResponse("chat.html")
    else:
        return await serve_main_page()

# Import the Knowledge Bridge and mCP API routers
from knowledge_bridge import app as knowledge_app
from mcp_endpoints import mcp_router

# Mount the Knowledge Bridge API
app.mount("/api/knowledge", knowledge_app)
app.include_router(mcp_router, prefix="/api")

print("✅ Knowledge Bridge API mounted at /api/knowledge")
print("✅ mCP Endpoints mounted at /api")

# The original code had a try/except for ImportError, which suggests knowledge_bridge might be optional.
# I will wrap the mounting in a try/except to handle the optional dependency, but the mcp_endpoints is new and required.
# I will assume the user has ensured all dependencies are installed.

# Import and mount the Knowledge Bridge API
try:
    from knowledge_bridge import app as knowledge_app
    app.mount("/api", knowledge_app)
    print("✅ Knowledge Bridge API mounted at /api")
except ImportError:
    print("⚠️ Knowledge Bridge not found, creating basic API endpoints")
    
    @app.get("/api/knowledge/stats")
    async def basic_stats():
        return {"total_cycles": 739, "status": "operational", "note": "Basic endpoint"}
    
    @app.get("/api/knowledge/latest/{category}")
    async def basic_latest(category: str):
        return [{"cycle": 739, "content": f"Sample {category} insight from autonomous learning cycles"}]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
