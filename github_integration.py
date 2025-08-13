#!/usr/bin/env python3
"""
GitHub Integration for XMRT Ecosystem
Provides autonomous GitHub operations using PyGithub
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from github import Github
from datetime import datetime, timedelta
import asyncio
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XMRTGitHubIntegration:
    """
    Enhanced GitHub integration for autonomous XMRT ecosystem operations
    """
    
    def __init__(self, username: str = "DevGruGold", token: str = None):
        self.username = username
        self.token = token or os.environ.get('GITHUB_TOKEN')
        
        if not self.token:
            logger.error("GitHub token not provided")
            raise ValueError("GitHub token is required")
        
        # Initialize GitHub client
        self.github = Github(self.token)
        
        # XMRT repositories
        self.repositories = {
            'xmrt_io': 'DevGruGold/XMRT.io',
            'xmrt_ecosystem': 'DevGruGold/XMRT-Ecosystem', 
            'xmrt_dao': 'DevGruGold/XMRT-DAO-Ecosystem'
        }
        
        # Repository objects
        self.repos = {}
        self._initialize_repositories()
        
        logger.info(f"✅ GitHub Integration initialized for user: {self.username}")
    
    def _initialize_repositories(self):
        """Initialize repository objects"""
        try:
            for repo_key, repo_name in self.repositories.items():
                self.repos[repo_key] = self.github.get_repo(repo_name)
                logger.info(f"✅ Connected to repository: {repo_name}")
        except Exception as e:
            logger.error(f"Error initializing repositories: {e}")
    
    async def commit_and_push_changes(self, repo_key: str, file_path: str, content: str, 
                                    commit_message: str, branch: str = "main") -> Dict:
        """
        Commit and push changes to repository
        """
        try:
            repo = self.repos.get(repo_key)
            if not repo:
                return {"success": False, "error": f"Repository {repo_key} not found"}
            
            # Get current file content to check if update is needed
            try:
                current_file = repo.get_contents(file_path, ref=branch)
                current_content = current_file.decoded_content.decode('utf-8')
                
                # Check if content is different
                if current_content.strip() == content.strip():
                    return {
                        "success": True,
                        "message": "No changes needed - content is identical",
                        "sha": current_file.sha
                    }
                
                # Update existing file
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=current_file.sha,
                    branch=branch
                )
                
            except Exception:
                # File doesn't exist, create new file
                result = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch
                )
            
            return {
                "success": True,
                "commit_sha": result['commit'].sha,
                "commit_url": result['commit'].html_url,
                "file_path": file_path,
                "message": commit_message,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def create_pull_request(self, repo_key: str, title: str, body: str, 
                                head_branch: str, base_branch: str = "main") -> Dict:
        """
        Create a pull request
        """
        try:
            repo = self.repos.get(repo_key)
            if not repo:
                return {"success": False, "error": f"Repository {repo_key} not found"}
            
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            return {
                "success": True,
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "title": title,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating pull request: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def create_issue(self, repo_key: str, title: str, body: str, labels: List[str] = None) -> Dict:
        """
        Create an issue
        """
        try:
            repo = self.repos.get(repo_key)
            if not repo:
                return {"success": False, "error": f"Repository {repo_key} not found"}
            
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            
            return {
                "success": True,
                "issue_number": issue.number,
                "issue_url": issue.html_url,
                "title": title,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_repository_stats(self, repo_key: str) -> Dict:
        """
        Get repository statistics
        """
        try:
            repo = self.repos.get(repo_key)
            if not repo:
                return {"success": False, "error": f"Repository {repo_key} not found"}
            
            # Get recent commits
            commits = list(repo.get_commits()[:10])
            
            # Get open issues and PRs
            open_issues = repo.get_issues(state='open')
            open_prs = repo.get_pulls(state='open')
            
            return {
                "success": True,
                "repository": repo.full_name,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": open_issues.totalCount,
                "open_prs": open_prs.totalCount,
                "recent_commits": [
                    {
                        "sha": commit.sha[:8],
                        "message": commit.commit.message,
                        "author": commit.commit.author.name,
                        "date": commit.commit.author.date.isoformat()
                    }
                    for commit in commits
                ],
                "last_updated": repo.updated_at.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting repository stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def update_gemini_integration_files(self) -> Dict:
        """
        Update all repositories with Gemini AI integration
        """
        results = {}
        
        # Update XMRT.io with enhanced Gemini integration
        xmrt_io_content = '''#!/usr/bin/env python3
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
'''
        
        # Commit to XMRT.io
        results['xmrt_io'] = await self.commit_and_push_changes(
            repo_key='xmrt_io',
            file_path='enhanced_gemini_integration.py',
            content=xmrt_io_content,
            commit_message='Add enhanced Gemini AI integration with autonomous operations'
        )
        
        # Update XMRT-Ecosystem with Gemini integration
        ecosystem_content = '''#!/usr/bin/env python3
"""
Enhanced XMRT Ecosystem with Gemini AI Integration
"""

import os
import sys
sys.path.append('/home/ubuntu')

from gemini_integration import get_gemini_instance, initialize_gemini
import asyncio
import json
from datetime import datetime

# Initialize Gemini AI for boardroom discussions
GEMINI_ENABLED = initialize_gemini()

class EnhancedBoardroomSystem:
    """Enhanced boardroom with Gemini AI agents"""
    
    def __init__(self):
        self.gemini = get_gemini_instance() if GEMINI_ENABLED else None
        self.active_discussions = {}
    
    async def start_autonomous_discussion(self, topic):
        """Start autonomous discussion between AI agents"""
        if not self.gemini:
            return {"error": "Gemini AI not available"}
        
        agents = ["dao_governor", "defi_specialist", "community_manager", "security_guardian"]
        discussion = await self.gemini.generate_autonomous_discussion(topic, agents)
        
        discussion_id = f"discussion_{int(datetime.now().timestamp())}"
        self.active_discussions[discussion_id] = {
            "topic": topic,
            "messages": discussion,
            "started_at": datetime.now().isoformat()
        }
        
        return {"discussion_id": discussion_id, "messages": discussion}
    
    async def get_agent_response(self, message, agent_id="dao_governor"):
        """Get response from specific agent"""
        if not self.gemini:
            return {"error": "Gemini AI not available"}
        
        return await self.gemini.generate_response(message, agent_id)

# Global boardroom instance
enhanced_boardroom = EnhancedBoardroomSystem()

async def test_boardroom():
    """Test enhanced boardroom functionality"""
    discussion = await enhanced_boardroom.start_autonomous_discussion(
        "quarterly ecosystem performance review"
    )
    print(json.dumps(discussion, indent=2))

if __name__ == "__main__":
    asyncio.run(test_boardroom())
'''
        
        results['xmrt_ecosystem'] = await self.commit_and_push_changes(
            repo_key='xmrt_ecosystem',
            file_path='enhanced_boardroom_gemini.py',
            content=ecosystem_content,
            commit_message='Add enhanced boardroom with Gemini AI integration'
        )
        
        # Update XMRT-DAO-Ecosystem with Gemini integration
        dao_content = '''#!/usr/bin/env python3
"""
Enhanced XMRT DAO with Gemini AI Integration
"""

import os
import sys
sys.path.append('/home/ubuntu')

from gemini_integration import get_gemini_instance, initialize_gemini
import asyncio
import json
from datetime import datetime

# Initialize Gemini AI for Eliza
GEMINI_ENABLED = initialize_gemini()

class EnhancedElizaSystem:
    """Enhanced Eliza with Gemini AI and voice capabilities"""
    
    def __init__(self):
        self.gemini = get_gemini_instance() if GEMINI_ENABLED else None
        self.conversation_history = []
    
    async def chat_with_eliza(self, message, include_voice=True):
        """Chat with Eliza using Gemini AI"""
        if not self.gemini:
            return {"error": "Gemini AI not available"}
        
        # Generate response
        response = await self.gemini.generate_response(message, "eliza")
        
        # Generate voice and avatar config if requested
        if include_voice and response['success']:
            voice_config = await self.gemini.generate_voice_avatar_config(
                "eliza", response['response']
            )
            response['voice_config'] = voice_config
        
        # Store in conversation history
        self.conversation_history.append({
            "user_message": message,
            "eliza_response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    async def get_ecosystem_insights(self):
        """Get ecosystem insights from Eliza"""
        if not self.gemini:
            return {"error": "Gemini AI not available"}
        
        insights_prompt = """
        Provide insights about the current XMRT ecosystem status, including:
        1. Overall health assessment
        2. Growth opportunities
        3. Community engagement status
        4. Technical development progress
        5. Recommendations for improvement
        """
        
        return await self.gemini.generate_response(insights_prompt, "eliza")

# Global Eliza instance
enhanced_eliza = EnhancedElizaSystem()

async def test_eliza():
    """Test enhanced Eliza functionality"""
    response = await enhanced_eliza.chat_with_eliza(
        "Hello Eliza, how is the XMRT ecosystem performing today?"
    )
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    asyncio.run(test_eliza())
'''
        
        results['xmrt_dao'] = await self.commit_and_push_changes(
            repo_key='xmrt_dao',
            file_path='enhanced_eliza_gemini.py',
            content=dao_content,
            commit_message='Add enhanced Eliza with Gemini AI and voice capabilities'
        )
        
        return {
            "success": True,
            "updates": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def create_autonomous_learning_system(self) -> Dict:
        """
        Create autonomous learning system across all repositories
        """
        try:
            # Create autonomous learning configuration
            learning_config = {
                "autonomous_learning": {
                    "enabled": True,
                    "learning_cycles": 739,
                    "gemini_integration": True,
                    "github_integration": True,
                    "voice_avatars": True,
                    "real_time_discussions": True
                },
                "agents": {
                    "eliza": {
                        "role": "primary_assistant",
                        "capabilities": ["chat", "insights", "voice", "avatar"],
                        "learning_focus": ["user_interaction", "ecosystem_optimization"]
                    },
                    "dao_governor": {
                        "role": "governance_leader",
                        "capabilities": ["strategy", "consensus", "policy"],
                        "learning_focus": ["governance_optimization", "decision_making"]
                    },
                    "defi_specialist": {
                        "role": "financial_optimizer",
                        "capabilities": ["defi_analysis", "yield_optimization"],
                        "learning_focus": ["market_analysis", "profit_optimization"]
                    },
                    "community_manager": {
                        "role": "growth_facilitator",
                        "capabilities": ["engagement", "growth_strategies"],
                        "learning_focus": ["community_building", "user_acquisition"]
                    },
                    "security_guardian": {
                        "role": "security_protector",
                        "capabilities": ["risk_assessment", "security_monitoring"],
                        "learning_focus": ["threat_detection", "vulnerability_assessment"]
                    }
                },
                "integration": {
                    "gemini_api": "GEMINI_API_KEY",
                    "github_token": "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",
                    "veo3_integration": True,
                    "real_time_sync": True
                }
            }
            
            config_content = json.dumps(learning_config, indent=2)
            
            # Commit to all repositories
            results = {}
            for repo_key in self.repositories.keys():
                results[repo_key] = await self.commit_and_push_changes(
                    repo_key=repo_key,
                    file_path='autonomous_learning_config.json',
                    content=config_content,
                    commit_message='Add autonomous learning system configuration'
                )
            
            return {
                "success": True,
                "config": learning_config,
                "commits": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating autonomous learning system: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict:
        """
        Check GitHub integration health
        """
        try:
            # Test GitHub connection
            user = self.github.get_user()
            
            # Get repository stats
            repo_stats = {}
            for repo_key in self.repositories.keys():
                stats = await self.get_repository_stats(repo_key)
                repo_stats[repo_key] = stats
            
            return {
                "success": True,
                "status": "healthy",
                "user": user.login,
                "repositories": len(self.repositories),
                "repo_stats": repo_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"GitHub health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
github_integration = None

def initialize_github(username: str = "DevGruGold", token: str = None):
    """Initialize global GitHub integration instance"""
    global github_integration
    try:
        github_integration = XMRTGitHubIntegration(username=username, token=token)
        logger.info("✅ Global GitHub integration instance initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize GitHub integration: {e}")
        return False

def get_github_instance():
    """Get global GitHub integration instance"""
    global github_integration
    return github_integration

if __name__ == "__main__":
    # Test the integration
    async def test_github():
        token = "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"
        github = XMRTGitHubIntegration(username="DevGruGold", token=token)
        
        # Test health check
        health = await github.health_check()
        print("Health Check:", json.dumps(health, indent=2))
        
        # Test autonomous learning system creation
        learning_system = await github.create_autonomous_learning_system()
        print("Learning System:", json.dumps(learning_system, indent=2))
    
    asyncio.run(test_github())

