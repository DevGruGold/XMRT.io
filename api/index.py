"""
XMRT API Entry Point for Vercel
This file imports the FastAPI app from the root server.py
"""

# Import the FastAPI app from the root server.py
import sys
import os

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app

# Export for Vercel
handler = app
