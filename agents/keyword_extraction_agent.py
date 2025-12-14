"""
Keyword Extraction Agent

Responsible for extracting keywords from URLs using web scraping and AI analysis.
Agent 2 in the SEO Agent System.
"""

from typing import List, Dict, Any
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scraper import scraper
from backend.llm_client import llm_client
from backend.semrush import semrush_analyzer


class KeywordExtractionAgent:
    """
    Agent 2: Keyword Extraction Specialist
    
    Responsible for:
    - Scraping web content from URLs
    - Extracting SEO keywords using Azure OpenAI
    - Generating search volumes and SEMrush URLs
    """
    
    def __init__(self):
        self.role = "SEO Keyword Extraction Specialist"
        self.scraper = scraper
        self.llm_client = llm_client
        self.semrush = semrush_analyzer
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Step 1: Scrape content from URL - NO FALLBACKS
        Returns: title, headings, content
        Raises exception if scraping fails
        """
        # scraper.scrape_url now raises exceptions on failure - no fallbacks
        scraped_data = await self.scraper.scrape_url(url)
        
        # Validate all required fields are present
        title = scraped_data.get("title")
        content = scraped_data.get("content")
        headings = scraped_data.get("headings")
        
        if not title:
            raise Exception(f"No title found in URL: {url}")
        
        if not content:
            raise Exception(f"No content found in URL: {url}")
        
        if headings is None:
            raise Exception(f"No headings data returned for URL: {url}")
        
        return {
            "title": title,
            "headings": headings,
            "content": content
        }
    
    async def extract_article_keywords(
        self,
        title: str,
        headings: List[str],
        content: str,
        url: str,
        time_range: str = "month"
    ) -> List[Dict[str, Any]]:
        """
        Step 2: Extract keywords from article content using Azure OpenAI
        Returns list of keywords with search volume, CPC, difficulty
        """
        print(f"[KeywordExtractionAgent] Extracting keywords from: {url}")
        
        keywords = await self.llm_client.extract_article_keywords(
            title=title,
            headings=headings,
            content=content,
            url=url,
            time_range=time_range
        )
        
        print(f"[KeywordExtractionAgent] Extracted {len(keywords)} article keywords")
        return keywords
    
    async def full_extraction(
        self,
        url: str,
        time_range: str = "month",
        max_keywords: int = 10
    ) -> Dict[str, Any]:
        """
        Full extraction pipeline: Scrape + Extract keywords
        """
        try:
            # Step 1: Scrape
            scraped = await self.scrape_url(url)
            
            # Step 2: Extract keywords
            keywords = await self.extract_article_keywords(
                title=scraped["title"],
                headings=scraped["headings"],
                content=scraped["content"],
                url=url,
                time_range=time_range
            )
            
            return {
                "status": "success",
                "url": url,
                "title": scraped["title"],
                "content": scraped["content"],
                "keywords": keywords[:max_keywords],
                "total_extracted": len(keywords[:max_keywords]),
                "time_range": time_range,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Keyword extraction failed: {str(e)}")
