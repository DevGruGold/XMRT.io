#!/usr/bin/env python3
"""
Enhanced XMRT.io with Gemini AI Integration
"""

import os
import sys
sys.path.append('/home/ubuntu')

from gemini_integration import get_gemini_instance, initialize_gemini
from github_integration import XMRTGitHubIntegration
import asyncio
import json
from datetime import datetime

# Initialize Gemini AI
GEMINI_ENABLED = initialize_gemini()

# Initialize GitHub integration
GITHUB_TOKEN = "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"
github_integration = XMRTGitHubIntegration(username="DevGruGold", token=GITHUB_TOKEN)

async def enhanced_eliza_response(message, agent_id="eliza"):
    """Generate enhanced response using Gemini AI"""
    if GEMINI_ENABLED:
        gemini = get_gemini_instance()
        response = await gemini.generate_response(message, agent_id)
        return response
    else:
        return {"success": False, "error": "Gemini AI not available"}

async def autonomous_ecosystem_update():
    """Perform autonomous ecosystem updates"""
    try:
        # Generate autonomous insights
        if GEMINI_ENABLED:
            gemini = get_gemini_instance()
            
            # Generate discussion between agents
            discussion = await gemini.generate_autonomous_discussion(
                "daily ecosystem health assessment",
                ["eliza", "dao_governor", "defi_specialist", "security_guardian"]
            )
            
            # Commit discussion to GitHub
            discussion_content = json.dumps(discussion, indent=2)
            commit_result = await github_integration.commit_and_push_changes(
                repo_key="xmrt_io",
                file_path=f"autonomous_discussions/discussion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                content=discussion_content,
                commit_message=f"Autonomous discussion: {datetime.now().isoformat()}"
            )
            
            return {"discussion": discussion, "commit": commit_result}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Test autonomous operations
    async def test_operations():
        result = await autonomous_ecosystem_update()
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_operations())
