# knowledge_bridge.py - Production version for XMRT.io deployment
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import requests
import base64
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class KnowledgeExtractor:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN", "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")
        self.username = os.getenv("GITHUB_USERNAME", "DevGruGold")
        self.base_url = f"https://api.github.com/repos/{self.username}/xmrtnet/contents"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self._cache = {}
        self._last_update = None
        
    def get_cached_insights(self) -> Dict[str, Any]:
        """Get cached insights or fetch fresh ones"""
        now = datetime.now()
        
        # Cache for 10 minutes
        if (self._last_update is None or 
            (now - self._last_update).seconds > 600 or 
            not self._cache):
            
            print("🔄 Refreshing knowledge cache...")
            self._cache = self._extract_cycle_insights()
            self._last_update = now
            
        return self._cache
        
    def _extract_cycle_insights(self) -> Dict[str, Any]:
        """Extract key insights from all cycle reports"""
        insights = {
            "analytics": [],
            "development": [],
            "marketing": [],
            "mining": [],
            "browser": [],
            "social_media": [],
            "latest_update": datetime.now().isoformat(),
            "total_cycles": 0
        }
        
        # Get repository contents
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to access xmrtnet repository")
            
        files = response.json()
        cycle_count = 0
        
        for file_info in files:
            filename = file_info['name']
            
            # Process different cycle types
            category = None
            
            if filename.startswith('ANALYTICS_CYCLE_'):
                category = "analytics"
            elif filename.startswith('DEVELOPMENT_CYCLE_'):
                category = "development"
            elif filename.startswith('MARKETING_CYCLE_'):
                category = "marketing"
            elif filename.startswith('MINING_CYCLE_'):
                category = "mining"
            elif filename.startswith('BROWSER_CYCLE_'):
                category = "browser"
            elif filename.startswith('SOCIAL_MEDIA_CYCLE_'):
                category = "social_media"
            
            if category:
                cycle_data = self._extract_file_content(filename)
                if cycle_data:
                    insights[category].append({
                        "cycle": self._extract_cycle_number(filename),
                        "content": cycle_data,
                        "filename": filename,
                        "timestamp": datetime.now().isoformat()
                    })
                    cycle_count += 1
        
        insights["total_cycles"] = cycle_count
        
        # Sort all categories by cycle number (latest first)
        for category in ["analytics", "development", "marketing", "mining", "browser", "social_media"]:
            insights[category].sort(key=lambda x: x['cycle'], reverse=True)
        
        return insights
    
    def _extract_file_content(self, filename: str) -> Optional[str]:
        """Extract content from a specific file"""
        file_url = f"{self.base_url}/{filename}"
        response = requests.get(file_url, headers=self.headers)
        
        if response.status_code == 200:
            file_data = response.json()
            if file_data.get('content'):
                try:
                    content = base64.b64decode(file_data['content']).decode('utf-8')
                    return self._extract_key_insights(content)
                except:
                    return None
        return None
    
    def _extract_key_insights(self, content: str) -> str:
        """Extract key insights from cycle content"""
        insights = []
        
        # Extract progress indicators
        progress_patterns = [
            r'(?:Progress|Achievement|Completion|Success|Status):\s*(.+)',
            r'(?:✅|✓)\s*(.+)',
            r'(?:COMPLETED|DONE|FINISHED):\s*(.+)'
        ]
        
        for pattern in progress_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                insights.extend([f"Progress: {match.strip()}" for match in matches[:2]])
        
        # Extract metrics
        metric_patterns = [
            r'(?:Metric|Score|Rate|Performance|Efficiency):\s*(.+)',
            r'(\d+(?:\.\d+)?%)',
            r'(\d+\s+(?:tasks|items|cycles|operations))'
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                insights.extend([f"Metric: {match.strip()}" for match in matches[:2]])
        
        # Extract actions
        action_patterns = [
            r'(?:Next|Action|TODO|Plan|Goal):\s*(.+)',
            r'(?:🎯|📋|⚡)\s*(.+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                insights.extend([f"Action: {match.strip()}" for match in matches[:2]])
        
        # Fallback to summary
        if not insights:
            paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
            if paragraphs:
                insights.append(f"Summary: {paragraphs[0][:200]}...")
        
        return "; ".join(insights[:5]) if insights else content[:200] + "..."
    
    def _extract_cycle_number(self, filename: str) -> int:
        """Extract cycle number from filename"""
        match = re.search(r'_(\d+)\.md$', filename)
        return int(match.group(1)) if match else 0

# FastAPI app
app = FastAPI(
    title="XMRT Knowledge Bridge",
    description="Unified API for accessing Eliza's autonomous cycle insights",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

extractor = KnowledgeExtractor()

@app.get("/")
async def root():
    return {
        "service": "XMRT Knowledge Bridge",
        "status": "operational",
        "description": "Unified access to Eliza's 739+ autonomous cycle insights",
        "endpoints": {
            "insights": "/api/knowledge/insights",
            "latest": "/api/knowledge/latest/{category}",
            "search": "/api/knowledge/search/{query}",
            "stats": "/api/knowledge/stats"
        }
    }

@app.get("/api/knowledge/insights")
async def get_all_insights():
    """Get comprehensive insights from all cycle reports"""
    return extractor.get_cached_insights()

@app.get("/api/knowledge/latest/{category}")
async def get_latest_insights(category: str, limit: int = Query(10, ge=1, le=50)):
    """Get latest insights from specific category"""
    all_insights = extractor.get_cached_insights()
    
    if category not in all_insights:
        raise HTTPException(status_code=404, detail=f"Category {category} not found")
    
    category_data = all_insights[category]
    return category_data[:limit]

@app.get("/api/knowledge/search/{query}")
async def search_insights(query: str, limit: int = Query(20, ge=1, le=100)):
    """Search for specific insights across all cycles"""
    all_insights = extractor.get_cached_insights()
    results = []
    
    for category, cycles in all_insights.items():
        if isinstance(cycles, list):
            for cycle in cycles:
                content = cycle.get('content', '').lower()
                if query.lower() in content:
                    results.append({
                        "category": category,
                        "cycle": cycle['cycle'],
                        "content": cycle['content'],
                        "relevance_score": content.count(query.lower())
                    })
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:limit]

@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """Get statistics about the knowledge base"""
    insights = extractor.get_cached_insights()
    
    stats = {
        "total_cycles": insights["total_cycles"],
        "last_updated": insights["latest_update"],
        "categories": {}
    }
    
    for category in ["analytics", "development", "marketing", "mining", "browser", "social_media"]:
        stats["categories"][category] = {
            "count": len(insights[category]),
            "latest_cycle": insights[category][0]["cycle"] if insights[category] else 0
        }
    
    return stats
