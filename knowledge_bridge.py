# OPTIMIZED Knowledge Bridge - Fixed Performance Issues
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
        self._stats_cache = None
        self._last_update = None
        
    def get_cached_insights(self) -> Dict[str, Any]:
        """Get cached insights or fetch fresh ones - OPTIMIZED VERSION"""
        now = datetime.now()
        
        # Cache for 15 minutes instead of 10
        if (self._last_update is None or 
            (now - self._last_update).seconds > 900 or 
            not self._cache):
            
            print("🔄 Refreshing knowledge cache (optimized)...")
            self._cache = self._extract_cycle_insights_optimized()
            self._last_update = now
            
        return self._cache
    
    def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick stats without processing all files - NEW OPTIMIZED METHOD"""
        
        # Use cached stats if available and recent
        now = datetime.now()
        if (self._stats_cache and self._last_update and 
            (now - self._last_update).seconds < 600):  # 10 minute cache
            return self._stats_cache
        
        try:
            # Get repository contents (just file list, no content)
            response = requests.get(self.base_url, headers=self.headers, timeout=30)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to access xmrtnet repository")
                
            files = response.json()
            
            # Quick count by category (no file content processing)
            quick_stats = {
                "analytics": [],
                "development": [],
                "marketing": [],
                "mining": [],
                "browser": [],
                "social_media": [],
                "latest_update": datetime.now().isoformat(),
                "total_cycles": 0
            }
            
            cycle_count = 0
            category_counts = {
                "analytics": 0,
                "development": 0,
                "marketing": 0,
                "mining": 0,
                "browser": 0,
                "social_media": 0
            }
            
            latest_cycles = {
                "analytics": 0,
                "development": 0,
                "marketing": 0,
                "mining": 0,
                "browser": 0,
                "social_media": 0
            }
            
            for file_info in files:
                filename = file_info['name']
                
                # Quick category detection
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
                    cycle_num = self._extract_cycle_number(filename)
                    category_counts[category] += 1
                    latest_cycles[category] = max(latest_cycles[category], cycle_num)
                    cycle_count += 1
            
            # Build quick stats response
            quick_stats["total_cycles"] = cycle_count
            categories_info = {}
            
            for category in category_counts:
                categories_info[category] = {
                    "count": category_counts[category],
                    "latest_cycle": latest_cycles[category]
                }
            
            result = {
                "total_cycles": cycle_count,
                "last_updated": quick_stats["latest_update"],
                "categories": categories_info,
                "note": "Quick stats - optimized for performance"
            }
            
            # Cache the result
            self._stats_cache = result
            
            return result
            
        except Exception as e:
            print(f"Error in quick stats: {e}")
            return {
                "total_cycles": 0,
                "error": "Stats temporarily unavailable",
                "categories": {}
            }
        
    def _extract_cycle_insights_optimized(self) -> Dict[str, Any]:
        """Extract insights with performance optimization"""
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
        
        try:
            # Get repository contents with timeout
            response = requests.get(self.base_url, headers=self.headers, timeout=45)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to access xmrtnet repository")
                
            files = response.json()
            cycle_count = 0
            processed_count = 0
            
            # Process files in batches to avoid timeout
            for file_info in files:
                filename = file_info['name']
                
                # Only process cycle files
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
                    # Process with timeout protection
                    try:
                        cycle_data = self._extract_file_content_fast(filename)
                        if cycle_data:
                            insights[category].append({
                                "cycle": self._extract_cycle_number(filename),
                                "content": cycle_data,
                                "filename": filename,
                                "timestamp": datetime.now().isoformat()
                            })
                            cycle_count += 1
                            processed_count += 1
                            
                            # Progress indicator every 100 files
                            if processed_count % 100 == 0:
                                print(f"Processed {processed_count} cycles...")
                                
                    except Exception as e:
                        print(f"Skipping {filename}: {e}")
                        continue
            
            insights["total_cycles"] = cycle_count
            
            # Sort all categories by cycle number (latest first)
            for category in ["analytics", "development", "marketing", "mining", "browser", "social_media"]:
                insights[category].sort(key=lambda x: x['cycle'], reverse=True)
            
            print(f"✅ Optimized extraction complete: {cycle_count} cycles processed")
            return insights
            
        except Exception as e:
            print(f"Error in optimized extraction: {e}")
            return insights
    
    def _extract_file_content_fast(self, filename: str) -> Optional[str]:
        """Fast file content extraction with timeout protection"""
        file_url = f"{self.base_url}/{filename}"
        
        try:
            # Shorter timeout for individual files
            response = requests.get(file_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                file_data = response.json()
                if file_data.get('content'):
                    try:
                        content = base64.b64decode(file_data['content']).decode('utf-8')
                        return self._extract_key_insights(content)
                    except:
                        return f"Content from {filename} (decode issue)"
            return None
            
        except requests.exceptions.Timeout:
            return f"Timeout processing {filename}"
        except Exception:
            return None
    
    def _extract_key_insights(self, content: str) -> str:
        """Extract key insights from cycle content - OPTIMIZED"""
        insights = []
        
        # Faster pattern matching with limits
        progress_patterns = [
            r'(?:Progress|Achievement|Completion|Success|Status):\s*(.+)',
            r'(?:✅|✓)\s*(.+)',
        ]
        
        for pattern in progress_patterns[:2]:  # Limit patterns
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                insights.extend([f"Progress: {match.strip()}" for match in matches[:1]])  # Limit matches
                break  # Stop after first match
        
        # Quick metric extraction
        if not insights:
            metric_patterns = [r'(\d+(?:\.\d+)?%)', r'(\d+\s+(?:tasks|items|cycles))']
            for pattern in metric_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    insights.extend([f"Metric: {match.strip()}" for match in matches[:1]])
                    break
        
        # Fallback to summary
        if not insights:
            paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 30]
            if paragraphs:
                insights.append(f"Summary: {paragraphs[0][:150]}...")
        
        return "; ".join(insights[:2]) if insights else content[:100] + "..."
    
    def _extract_cycle_number(self, filename: str) -> int:
        """Extract cycle number from filename"""
        match = re.search(r'_(\d+)\.md$', filename)
        return int(match.group(1)) if match else 0

# FastAPI app with optimizations
app = FastAPI(
    title="XMRT Knowledge Bridge - OPTIMIZED",
    description="High-performance API for accessing Eliza's autonomous cycle insights",
    version="2.0.0"
)

# Enable CORS
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
        "version": "2.0.0 - OPTIMIZED",
        "description": "High-performance access to Eliza's 739+ autonomous cycle insights",
        "endpoints": {
            "insights": "/api/knowledge/insights",
            "latest": "/api/knowledge/latest/{category}",
            "search": "/api/knowledge/search/{query}",
            "stats": "/api/knowledge/stats (OPTIMIZED)"
        }
    }

@app.get("/api/knowledge/insights")
async def get_all_insights():
    """Get comprehensive insights from all cycle reports"""
    return extractor.get_cached_insights()

@app.get("/api/knowledge/latest/{category}")
async def get_latest_insights(category: str, limit: int = Query(10, ge=1, le=50)):
    """Get latest insights from specific category - FAST"""
    all_insights = extractor.get_cached_insights()
    
    if category not in all_insights:
        raise HTTPException(status_code=404, detail=f"Category {category} not found")
    
    category_data = all_insights[category]
    return category_data[:limit]

@app.get("/api/knowledge/search/{query}")
async def search_insights(query: str, limit: int = Query(20, ge=1, le=100)):
    """Search for specific insights across all cycles - FAST"""
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
    """Get statistics about the knowledge base - OPTIMIZED FOR SPEED"""
    return extractor.get_quick_stats()
