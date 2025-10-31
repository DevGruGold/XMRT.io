"""
Redis Event Bus for XMRT Ecosystem
Provides pub/sub coordination across services
"""

import os
import json
import asyncio
import logging
from typing import Dict, List, Callable, Any
from datetime import datetime
from upstash_redis import Redis

logger = logging.getLogger(__name__)

class RedisEventBus:
    """Event bus for cross-service communication"""
    
    def __init__(self):
        self.redis_url = os.getenv('UPSTASH_REDIS_URL')
        self.redis_token = os.getenv('UPSTASH_REDIS_TOKEN')
        
        if not self.redis_url or not self.redis_token:
            logger.warning("Redis credentials not found, using mock mode")
            self.mock_mode = True
            self.client = None
        else:
            self.mock_mode = False
            self.client = Redis(url=self.redis_url, token=self.redis_token)
        
        self.subscribers: Dict[str, List[Callable]] = {}
        self.activities: List[Dict] = []
    
    def publish(self, channel: str, data: Dict[str, Any]) -> bool:
        """Publish event to channel"""
        try:
            if self.mock_mode:
                logger.info(f"[MOCK] Publishing to {channel}: {data}")
                self._trigger_local_subscribers(channel, data)
                return True
            
            payload = json.dumps({
                **data,
                'timestamp': datetime.now().isoformat(),
                'channel': channel
            })
            
            self.client.publish(channel, payload)
            logger.info(f"Published to {channel}")
            
            # Also store in activities for mCP
            self._add_activity(channel, data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            return False
    
    def subscribe(self, channel: str, callback: Callable):
        """Subscribe to channel"""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)
        logger.info(f"Subscribed to {channel}")
    
    def _trigger_local_subscribers(self, channel: str, data: Dict):
        """Trigger local subscribers (for mock/testing)"""
        if channel in self.subscribers:
            for callback in self.subscribers[channel]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Subscriber callback error: {e}")
    
    def _add_activity(self, channel: str, data: Dict):
        """Add activity to mCP stream"""
        activity = {
            'channel': channel,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.activities.append(activity)
        
        # Keep only last 100 activities
        self.activities = self.activities[-100:]
    
    def get_activities(self) -> List[Dict]:
        """Get recent activities for mCP"""
        return self.activities
    
    async def listen(self, channels: List[str]):
        """Listen to channels asynchronously"""
        if self.mock_mode:
            logger.info(f"[MOCK] Listening to {channels}")
            return
        
        try:
            pubsub = self.client.pubsub()
            pubsub.subscribe(*channels)
            
            while True:
                message = pubsub.get_message()
                if message and message['type'] == 'message':
                    channel = message['channel']
                    data = json.loads(message['data'])
                    
                    self._add_activity(channel, data)
                    self._trigger_local_subscribers(channel, data)
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error listening to channels: {e}")

# Global event bus instance
event_bus = RedisEventBus()
