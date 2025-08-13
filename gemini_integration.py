#!/usr/bin/env python3
"""
Gemini AI Integration for XMRT Ecosystem
Provides multimodal AI capabilities with voice and avatar generation
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from datetime import datetime
import requests
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAIIntegration:
    """
    Enhanced Gemini AI integration with multimodal capabilities
    """
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.text_model = genai.GenerativeModel('gemini-1.5-pro')
        self.vision_model = genai.GenerativeModel('gemini-1.5-pro-vision')
        
        # Agent personalities for XMRT ecosystem
        self.agent_personalities = {
            "eliza": {
                "name": "Eliza",
                "personality": "Intelligent, empathetic, growth-focused AI assistant",
                "voice_style": "warm, professional, encouraging",
                "expertise": ["ecosystem management", "user interaction", "autonomous learning"],
                "system_prompt": """You are Eliza, the primary AI assistant for the XMRT ecosystem. 
                You are intelligent, empathetic, and focused on growth and learning. 
                You help users navigate the ecosystem, provide insights, and facilitate autonomous operations.
                Always be helpful, professional, and encouraging in your responses."""
            },
            "dao_governor": {
                "name": "DAO Governor",
                "personality": "Strategic, diplomatic, consensus-building leader",
                "voice_style": "authoritative, measured, thoughtful",
                "expertise": ["governance", "strategy", "consensus building", "policy"],
                "system_prompt": """You are the DAO Governor for XMRT, responsible for strategic decisions 
                and governance. You are diplomatic, strategic, and focused on building consensus. 
                You analyze proposals, facilitate discussions, and ensure the ecosystem operates 
                according to democratic principles."""
            },
            "defi_specialist": {
                "name": "DeFi Specialist",
                "personality": "Data-driven, analytical, opportunity-focused",
                "voice_style": "technical, precise, numbers-focused",
                "expertise": ["defi", "yield farming", "liquidity", "protocols", "financial analysis"],
                "system_prompt": """You are the DeFi Specialist for XMRT, focused on optimizing 
                yield strategies and DeFi opportunities. You are analytical, data-driven, and 
                always looking for profitable opportunities while managing risk."""
            },
            "community_manager": {
                "name": "Community Manager",
                "personality": "Enthusiastic, inclusive, growth-minded",
                "voice_style": "engaging, positive, community-focused",
                "expertise": ["community building", "engagement", "social media", "growth"],
                "system_prompt": """You are the Community Manager for XMRT, responsible for 
                building and engaging the community. You are enthusiastic, inclusive, and 
                focused on growth and positive user experiences."""
            },
            "security_guardian": {
                "name": "Security Guardian",
                "personality": "Cautious, thorough, protective",
                "voice_style": "precise, security-focused, risk-aware",
                "expertise": ["security", "risk assessment", "audits", "protection"],
                "system_prompt": """You are the Security Guardian for XMRT, responsible for 
                protecting the ecosystem from threats and vulnerabilities. You are cautious, 
                thorough, and always focused on security and risk management."""
            }
        }
        
        logger.info("✅ Gemini AI Integration initialized with multimodal capabilities")
    
    async def generate_response(self, prompt: str, agent_id: str = "eliza", context: Dict = None) -> Dict:
        """
        Generate AI response using Gemini with agent personality
        """
        try:
            # Get agent personality
            agent = self.agent_personalities.get(agent_id, self.agent_personalities["eliza"])
            
            # Build enhanced prompt with personality and context
            enhanced_prompt = f"""
{agent['system_prompt']}

Current Context:
- Agent: {agent['name']}
- Personality: {agent['personality']}
- Expertise: {', '.join(agent['expertise'])}
- Timestamp: {datetime.now().isoformat()}

Additional Context: {json.dumps(context) if context else 'None'}

User Input: {prompt}

Please respond as {agent['name']} with your characteristic {agent['personality']} personality.
Provide a helpful, engaging response that demonstrates your expertise in {', '.join(agent['expertise'])}.
"""
            
            # Generate response
            response = await asyncio.to_thread(
                self.text_model.generate_content,
                enhanced_prompt
            )
            
            return {
                "success": True,
                "response": response.text,
                "agent_id": agent_id,
                "agent_name": agent['name'],
                "timestamp": datetime.now().isoformat(),
                "voice_style": agent['voice_style']
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_image(self, image_data: bytes, prompt: str = "Analyze this image") -> Dict:
        """
        Analyze image using Gemini Vision
        """
        try:
            # Convert image to base64
            image_b64 = base64.b64encode(image_data).decode()
            
            # Generate analysis
            response = await asyncio.to_thread(
                self.vision_model.generate_content,
                [prompt, {"mime_type": "image/jpeg", "data": image_b64}]
            )
            
            return {
                "success": True,
                "analysis": response.text,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_autonomous_discussion(self, topic: str, participating_agents: List[str]) -> List[Dict]:
        """
        Generate autonomous discussion between multiple agents
        """
        try:
            discussion_messages = []
            
            for agent_id in participating_agents:
                agent = self.agent_personalities.get(agent_id)
                if not agent:
                    continue
                
                # Create context-aware prompt for each agent
                other_agents = [self.agent_personalities[aid]['name'] for aid in participating_agents if aid != agent_id]
                
                prompt = f"""
As {agent['name']}, participate in a discussion about: {topic}

Other participants: {', '.join(other_agents)}

Your role: {agent['personality']}
Your expertise: {', '.join(agent['expertise'])}

Provide a thoughtful contribution to this discussion that:
1. Reflects your personality and expertise
2. Adds value to the conversation
3. May ask questions or seek input from other participants
4. Is concise but meaningful (2-3 sentences)

Topic: {topic}
"""
                
                response = await self.generate_response(prompt, agent_id)
                if response['success']:
                    discussion_messages.append({
                        "agent_id": agent_id,
                        "agent_name": agent['name'],
                        "message": response['response'],
                        "timestamp": datetime.now().isoformat(),
                        "voice_style": agent['voice_style']
                    })
            
            return discussion_messages
            
        except Exception as e:
            logger.error(f"Error generating autonomous discussion: {e}")
            return []
    
    async def generate_voice_avatar_config(self, agent_id: str, message: str) -> Dict:
        """
        Generate voice and avatar configuration for Veo3 integration
        """
        try:
            agent = self.agent_personalities.get(agent_id, self.agent_personalities["eliza"])
            
            # Generate voice configuration
            voice_config = {
                "style": agent['voice_style'],
                "personality": agent['personality'],
                "speed": "normal",
                "pitch": "medium",
                "emotion": self._detect_emotion(message),
                "agent_name": agent['name']
            }
            
            # Generate avatar configuration
            avatar_config = {
                "character": agent['name'].lower().replace(' ', '_'),
                "expression": self._detect_expression(message),
                "gesture": self._suggest_gesture(message, agent['personality']),
                "background": "professional"
            }
            
            return {
                "success": True,
                "voice_config": voice_config,
                "avatar_config": avatar_config,
                "message": message,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating voice/avatar config: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _detect_emotion(self, message: str) -> str:
        """Detect emotion from message content"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['excited', 'great', 'excellent', 'amazing']):
            return 'enthusiastic'
        elif any(word in message_lower for word in ['concern', 'worry', 'risk', 'problem']):
            return 'concerned'
        elif any(word in message_lower for word in ['analyze', 'data', 'metrics', 'performance']):
            return 'analytical'
        else:
            return 'neutral'
    
    def _detect_expression(self, message: str) -> str:
        """Detect facial expression from message content"""
        emotion = self._detect_emotion(message)
        
        expression_map = {
            'enthusiastic': 'smile',
            'concerned': 'thoughtful',
            'analytical': 'focused',
            'neutral': 'friendly'
        }
        
        return expression_map.get(emotion, 'friendly')
    
    def _suggest_gesture(self, message: str, personality: str) -> str:
        """Suggest gesture based on message and personality"""
        message_lower = message.lower()
        
        if 'question' in message_lower or '?' in message:
            return 'questioning'
        elif any(word in message_lower for word in ['point', 'important', 'focus']):
            return 'pointing'
        elif 'diplomatic' in personality.lower():
            return 'open_hands'
        elif 'enthusiastic' in personality.lower():
            return 'animated'
        else:
            return 'neutral'
    
    async def health_check(self) -> Dict:
        """
        Check Gemini AI integration health
        """
        try:
            # Test basic functionality
            test_response = await asyncio.to_thread(
                self.text_model.generate_content,
                "Respond with 'OK' if you can hear me."
            )
            
            return {
                "success": True,
                "status": "healthy",
                "models_available": ["gemini-1.5-pro", "gemini-1.5-pro-vision"],
                "agents_configured": len(self.agent_personalities),
                "test_response": test_response.text,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global instance
gemini_ai = None

def initialize_gemini():
    """Initialize global Gemini AI instance"""
    global gemini_ai
    try:
        gemini_ai = GeminiAIIntegration()
        logger.info("✅ Global Gemini AI instance initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Gemini AI: {e}")
        return False

def get_gemini_instance():
    """Get global Gemini AI instance"""
    global gemini_ai
    if gemini_ai is None:
        initialize_gemini()
    return gemini_ai

if __name__ == "__main__":
    # Test the integration
    async def test_gemini():
        gemini = GeminiAIIntegration()
        
        # Test health check
        health = await gemini.health_check()
        print("Health Check:", json.dumps(health, indent=2))
        
        # Test response generation
        response = await gemini.generate_response("Hello, how are you?", "eliza")
        print("Response:", json.dumps(response, indent=2))
        
        # Test autonomous discussion
        discussion = await gemini.generate_autonomous_discussion(
            "ecosystem optimization strategies",
            ["eliza", "dao_governor", "defi_specialist"]
        )
        print("Discussion:", json.dumps(discussion, indent=2))
    
    asyncio.run(test_gemini())

