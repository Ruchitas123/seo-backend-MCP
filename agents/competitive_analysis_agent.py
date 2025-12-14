"""
Competitive Keyword Analysis Agent

Responsible for analyzing competitor keywords based on article keywords.
NOW WITH REAL COMPETITOR WEBSITE SCRAPING!
Agent 3 in the SEO Agent System.
"""

from typing import List, Dict, Any
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm_client import llm_client
from backend.config import PRODUCT_COMPETITORS
from agents.competitor_agent import CompetitorFetchingAgent


class CompetitiveAnalysisAgent:
    """
    Agent 3: Competitive Intelligence & SEO Analyst
    
    Responsible for:
    - SCRAPING real competitor websites for content
    - Getting competitor keywords from ACTUAL competitor content
    - Generating suggested keywords (top 10 high-volume from both sources)
    - Creating keyword mappings between article and competitor keywords
    """
    
    def __init__(self):
        self.role = "Competitive Intelligence & SEO Analyst"
        self.competitor_agent = CompetitorFetchingAgent()
        self.llm_client = llm_client
    
    async def analyze_competitor_keywords(
        self,
        article_keywords: List[Dict[str, Any]],
        product: str,
        time_range: str = "month",
        article_title: str = "",
        article_content: str = "",
        article_headings: List[str] = None,
        article_url: str = ""
    ) -> Dict[str, Any]:
        """
        DYNAMIC Capability-Based Competitor Analysis
        
        NEW FLOW:
        1. Identify the CAPABILITY/FEATURE from the article
        2. Use LLM to find EQUIVALENT pages on competitor websites
        3. Scrape those specific capability pages
        4. Extract terminology and keywords from competitor content
        
        Fully dynamic - no hardcoded paths or fallbacks.
        
        Returns: article_keywords, competitor_keywords, suggested_keywords, mappings
        """
        print(f"\n{'='*70}")
        print(f"[CompetitiveAnalysisAgent]  DYNAMIC CAPABILITY-BASED ANALYSIS")
        print(f"{'='*70}")
        print(f"[CompetitiveAnalysisAgent] Product: {product}")
        print(f"[CompetitiveAnalysisAgent] Article URL: {article_url}")
        print(f"[CompetitiveAnalysisAgent] Article keywords: {len(article_keywords)}")
        print(f"{'='*70}\n")
        
        # Step 1: Get competitor names
        competitor_data = self.competitor_agent.execute(product)
        competitor_names = [c['name'] for c in competitor_data["competitors"]]
        print(f"[CompetitiveAnalysisAgent] Competitors to analyze: {competitor_names}")
        
        # Step 2: IDENTIFY THE CAPABILITY from the article
        print(f"\n[CompetitiveAnalysisAgent]  Step 1: Identifying article capability...")
        capability = await self.llm_client.identify_article_capability(
            title=article_title,
            headings=article_headings or [],
            content=article_content,
            url=article_url
        )
        
        print(f"[CompetitiveAnalysisAgent]  Capability identified: {capability.get('name')}")
        print(f"[CompetitiveAnalysisAgent]    Description: {capability.get('description')}")
        print(f"[CompetitiveAnalysisAgent]    Search terms: {capability.get('competitor_search_terms')}")
        
        # Step 3: DYNAMICALLY FIND and SCRAPE competitor capability pages
        print(f"\n[CompetitiveAnalysisAgent]  Step 2: Finding equivalent capability on competitor sites...")
        
        competitor_content_data = await self.competitor_agent.get_competitor_content_for_capability(
            product=product,
            capability=capability,
            llm_client=self.llm_client
        )
        
        competitor_content = competitor_content_data.get("competitor_content", [])
        print(f"\n[CompetitiveAnalysisAgent]  Found capability content from {len(competitor_content)} competitors")
        
        for comp in competitor_content:
            content_len = len(comp.get('content', ''))
            feature_name = comp.get('competitor_feature_name', 'Unknown')
            urls_count = len(comp.get('urls_scraped', []))
            print(f"  - {comp.get('competitor_name')}: '{feature_name}' - {content_len} chars from {urls_count} URLs")
        
        # Step 4: Use LLM to analyze REAL competitor content and extract keywords
        print(f"\n[CompetitiveAnalysisAgent]  Step 3: Analyzing competitor terminology...")
        keyword_data = await self.llm_client.get_competitor_keywords(
            article_keywords=article_keywords,
            product=product,
            time_range=time_range,
            article_title=article_title,
            article_content=article_content,
            competitor_content=competitor_content  # Pass REAL capability-specific content
        )
        
        print(f"\n[CompetitiveAnalysisAgent]  Generated {len(keyword_data['competitor_keywords'])} competitor keywords")
        print(f"[CompetitiveAnalysisAgent]  Generated {len(keyword_data['suggested_keywords'])} suggested keywords")
        
        return {
            "status": "success",
            "product": product,
            "capability": capability,
            "competitors": competitor_names,
            "competitors_scraped": len(competitor_content),
            "article_keywords": keyword_data["article_keywords"],
            "competitor_keywords": keyword_data["competitor_keywords"],
            "suggested_keywords": keyword_data["suggested_keywords"],
            "keyword_mappings": keyword_data["keyword_mappings"],
            "time_range": time_range,
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "dynamic_capability_based"
        }
