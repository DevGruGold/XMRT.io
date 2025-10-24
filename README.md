# XMRT.io AI Executive Boardroom

A powerful, interactive interface where users can engage with all five XMRT.io AI agents in a collaborative boardroom setting. This repository also contains the FastAPI server that powers the backend, including the new **Model Context Protocol (mCP) Gateway** for ecosystem integration.

## Features

- 🏛️ Circular boardroom layout with agent avatars
- 💬 Real-time chat with all agents
- 🎯 Direct agent targeting or auto-routing
- 👥 Multi-agent conversations
- ⚡ **Real-Time mCP Activity Stream** on the frontend
- 🔗 **Exposed mCP Endpoints** for external ecosystem engagement
- 📱 Responsive design
- 💾 Chat export functionality

## Setup

This project uses a Streamlit frontend (`streamlit_boardroom.py`) and a FastAPI backend (`server.py`).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DevGruGold/XMRT.io.git
    cd XMRT.io
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the FastAPI Backend:**
    ```bash
    uvicorn server:app --host 0.0.0.0 --port 8000
    ```

4.  **Run the Streamlit Frontend (in a separate terminal):**
    ```bash
    streamlit run streamlit_boardroom.py
    ```
    The Streamlit app will automatically connect to the FastAPI backend (assuming the deployment environment is configured correctly, or you update the URLs in `streamlit_boardroom.py` for local testing).

## mCP Gateway Endpoints

The FastAPI server exposes endpoints for the Model Context Protocol (mCP) to allow the wider XMRT ecosystem to engage with the boardroom and push real-time activity updates.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/mcp/health` | `GET` | Checks the health and availability of the XMRT.io MCP Gateway. |
| `/api/mcp/activity` | `POST` | Endpoint for an mCP server to push real-time activity updates to the boardroom's frontend stream. |
| `/api/mcp/activities` | `GET` | Fetches the latest real-time activities displayed on the Streamlit frontend. |
| `/api/mcp/test_command` | `POST` | A simple endpoint to test command execution from an mCP server. |

## Agent Capabilities

- **Technical Agent**: Code generation, APIs, debugging
- **DAO Agent**: Governance, proposals, treasury
- **Mining Agent**: Operations, optimization, leaderboards  
- **Marketing Agent**: Content creation, campaigns
- **General Agent**: Coordination and general assistance

Enjoy your liberated AI boardroom! 🚀

