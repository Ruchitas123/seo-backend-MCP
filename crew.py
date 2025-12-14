"""
SEO Agent Orchestration System

Coordinates multiple agents to perform SEO analysis tasks.
All 4 agents work together through this orchestrator.
"""

from typing import Dict, Any, List
from datetime import datetime

from agents.competitor_agent import CompetitorFetchingAgent
from agents.keyword_extraction_agent import KeywordExtractionAgent
from agents.competitive_analysis_agent import CompetitiveAnalysisAgent
from agents.content_rewriting_agent import ContentRewritingAgent


class SEOAgentCrew:
    """
    Orchestrates the SEO Agent system.
    
    Manages four sub-agents:
    1. CompetitorFetchingAgent - Fetches competitor list for a product
    2. KeywordExtractionAgent - Extracts keywords from URLs
    3. CompetitiveAnalysisAgent - Analyzes competitor keywords
    4. ContentRewritingAgent - Rewrites content for SEO
    """
    
    def __init__(self):
        print("[SEOAgentCrew] Initializing 4 agents...")
        self.competitor_agent = CompetitorFetchingAgent()
        self.keyword_agent = KeywordExtractionAgent()
        self.analysis_agent = CompetitiveAnalysisAgent()
        self.rewriting_agent = ContentRewritingAgent()
        print("[SEOAgentCrew] All agents initialized")
    
    # ===== AGENT 1: Competitor Fetching =====
    def get_competitors(self, product: str) -> Dict[str, Any]:
        """
        Agent 1: Fetch competitors for a selected product.
        Uses: CompetitorFetchingAgent
        """
        print(f"[Agent 1: CompetitorFetching] Getting competitors for {product}")
        return self.competitor_agent.execute(product)
    
    # ===== AGENT 2: Keyword Extraction =====
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Agent 2 - Step 1: Scrape content from URL
        Uses: KeywordExtractionAgent
        """
        print(f"[Agent 2: KeywordExtraction] Scraping URL: {url}")
        return await self.keyword_agent.scrape_url(url)
    
    async def extract_article_keywords(
        self,
        title: str,
        headings: List[str],
        content: str,
        url: str,
        time_range: str = "month"
    ) -> List[Dict[str, Any]]:
        """
        Agent 2 - Step 2: Extract keywords from article
        Uses: KeywordExtractionAgent
        """
        print(f"[Agent 2: KeywordExtraction] Extracting article keywords")
        return await self.keyword_agent.extract_article_keywords(
            title=title,
            headings=headings,
            content=content,
            url=url,
            time_range=time_range
        )
    
    # ===== AGENT 3: Competitive Analysis =====
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
        Agent 3: Analyze competitor keywords for each article keyword
        Uses: CompetitiveAnalysisAgent
        
        NEW: Uses dynamic capability-based analysis to find equivalent
        pages on competitor websites.
        """
        print(f"[Agent 3: CompetitiveAnalysis] Dynamic capability-based analysis")
        return await self.analysis_agent.analyze_competitor_keywords(
            article_keywords=article_keywords,
            product=product,
            time_range=time_range,
            article_title=article_title,
            article_content=article_content,
            article_headings=article_headings or [],
            article_url=article_url
        )
    
    # ===== AGENT 4: Content Rewriting =====
    async def rewrite_content(
        self,
        content: str,
        target_keywords: List[str],
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Agent 4: Rewrite content for SEO optimization
        Uses: ContentRewritingAgent
        """
        print(f"[Agent 4: ContentRewriting] Rewriting content with {len(target_keywords)} keywords")
        return await self.rewriting_agent.rewrite_content(content, target_keywords, tone)
    
    # ===== FULL PIPELINE =====
    async def full_seo_analysis(
        self,
        url: str,
        product: str,
        time_range: str = "month"
    ) -> Dict[str, Any]:
        """
        Run the complete SEO analysis pipeline using all 4 agents.
        
        Pipeline:
        1. Agent 1: Get competitors for product
        2. Agent 2: Scrape URL and extract article keywords
        3. Agent 3: Get competitor keywords for each article keyword
        
        Returns complete analysis with article, competitor, and suggested keywords.
        """
        print(f"\n{'='*50}")
        print(f"[SEOAgentCrew] Starting full analysis pipeline")
        print(f"URL: {url}")
        print(f"Product: {product}")
        print(f"Time Range: {time_range}")
        print(f"{'='*50}\n")
        
        # Agent 1: Get competitors
        competitor_result = self.get_competitors(product)
        competitor_names = [c['name'] for c in competitor_result["competitors"]]
        
        # Agent 2: Scrape and extract article keywords
        scraped = await self.scrape_url(url)
        article_keywords = await self.extract_article_keywords(
            title=scraped["title"],
            headings=scraped["headings"],
            content=scraped["content"],
            url=url,
            time_range=time_range
        )
        
        # Agent 3: Analyze competitor keywords (DYNAMIC CAPABILITY-BASED)
        analysis_result = await self.analyze_competitor_keywords(
            article_keywords=article_keywords,
            product=product,
            time_range=time_range,
            article_title=scraped["title"],
            article_content=scraped["content"],
            article_headings=scraped["headings"],
            article_url=url
        )
        
        # Get capability info if available
        capability = analysis_result.get("capability", {})
        
        print(f"\n{'='*50}")
        print(f"[SEOAgentCrew] Analysis complete!")
        print(f"Capability Identified: {capability.get('name', 'N/A')}")
        print(f"Article Keywords: {len(analysis_result['article_keywords'])}")
        print(f"Competitor Keywords: {len(analysis_result['competitor_keywords'])}")
        print(f"Suggested Keywords: {len(analysis_result['suggested_keywords'])}")
        print(f"{'='*50}\n")
        
        return {
            "status": "success",
            "url": url,
            "title": scraped["title"],
            "product": product,
            "time_range": time_range,
            "capability": capability,
            "competitors": competitor_names,
            "article_keywords": analysis_result["article_keywords"],
            "competitor_keywords": analysis_result["competitor_keywords"],
            "suggested_keywords": analysis_result["suggested_keywords"],
            "keyword_mappings": analysis_result["keyword_mappings"],
            "original_content": scraped["content"],
            "timestamp": datetime.now().isoformat()
        }


# Global instance
seo_crew = SEOAgentCrew()
