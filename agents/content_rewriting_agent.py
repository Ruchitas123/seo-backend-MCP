"""
Content Rewriting Agent

Responsible for rewriting content to be SEO-optimized using user-selected keywords.
"""

import re
from typing import List, Dict, Any
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm_client import llm_client


class ContentRewritingAgent:
    """
    Agent responsible for SEO-optimized content rewriting.
    """
    
    def __init__(self):
        self.role = "SEO Content Optimization Specialist"
        self.llm_client = llm_client
    
    async def rewrite_content(
        self,
        content: str,
        target_keywords: List[str],
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Execute content rewriting for SEO optimization."""
        keywords_to_use = target_keywords[:3]
        
        if not content.strip():
            return {
                "status": "error",
                "error": "No content provided for rewriting",
                "original_content": content,
                "rewritten_content": "",
                "target_keywords": keywords_to_use
            }
        
        if not keywords_to_use:
            return {
                "status": "error",
                "error": "No target keywords provided",
                "original_content": content,
                "rewritten_content": "",
                "target_keywords": []
            }
        
        try:
            result = await self.llm_client.rewrite_content_for_seo(
                content=content,
                target_keywords=keywords_to_use,
                tone=tone
            )
            
            if result.get("status") == "error":
                return result
            
            rewritten_content = result.get("rewritten_content", "")
            keyword_density = self._calculate_keyword_density(rewritten_content, keywords_to_use)
            
            return {
                "status": "success",
                "original_content": content,
                "rewritten_content": rewritten_content,
                "target_keywords": keywords_to_use,
                "tone": tone,
                "keyword_density": keyword_density,
                "seo_improvements": result.get("seo_improvements", []),
                "word_count": {
                    "original": len(content.split()),
                    "rewritten": len(rewritten_content.split())
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "original_content": content,
                "rewritten_content": "",
                "target_keywords": keywords_to_use
            }
    
    def _calculate_keyword_density(
        self,
        content: str,
        keywords: List[str]
    ) -> Dict[str, float]:
        """Calculate keyword density for each target keyword"""
        content_lower = content.lower()
        word_count = len(content.split())
        
        density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            pattern = rf'\b{re.escape(keyword_lower)}\b'
            occurrences = len(re.findall(pattern, content_lower))
            keyword_word_count = len(keyword.split())
            density[keyword] = round((occurrences * keyword_word_count / word_count) * 100, 2) if word_count > 0 else 0
        
        return density
