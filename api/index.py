"""
XMRT API Entry Point for Vercel
This file imports and exports the FastAPI app for Vercel's ASGI runtime
"""

import sys
import os

# Add parent directory to path to import server
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the FastAPI app from the root server.py
from server import app

# Export for Vercel's ASGI runtime
# The FastAPI app itself is a valid ASGI3 application
# Vercel's Python runtime will automatically detect and handle it correctly
# No need for a wrapper - just export the app directly
