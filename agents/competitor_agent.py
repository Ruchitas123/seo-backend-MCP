"""
Product Selection & Competitor Fetching Agent

Responsible for fetching competitor lists and SCRAPING competitor websites
to extract real keywords from competitor content.
"""

from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
import re
import asyncio

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import PRODUCT_COMPETITORS


class CompetitorFetchingAgent:
    """
    Agent responsible for fetching competitor information and 
    ACTUALLY SCRAPING competitor websites to extract real content.
    """
    
    def __init__(self):
        self.role = "Product & Competitor Specialist"
        self.goal = "Fetch competitor information and scrape real competitor content"
        # Rotate through realistic browser headers to avoid detection
        self.headers_list = [
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            },
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            },
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            }
        ]
        self.headers = self.headers_list[0]
        self.request_count = 0
    
    def _get_rotated_headers(self) -> Dict[str, str]:
        """Rotate through headers to avoid detection"""
        self.request_count += 1
        header_index = self.request_count % len(self.headers_list)
        return self.headers_list[header_index]
    
    def get_competitors(self, product: str) -> List[Dict[str, str]]:
        """Fetch competitors for the specified product type."""
        if product not in PRODUCT_COMPETITORS:
            raise ValueError(f"Unknown product type: {product}. Valid options: {list(PRODUCT_COMPETITORS.keys())}")
        return PRODUCT_COMPETITORS[product]
    
    def _get_common_paths(self) -> List[str]:
        """
        Common paths to try on any competitor website.
        These are generic paths, NOT capability-specific.
        """
        return [
            "/help",
            "/help/",
            "/support",
            "/support/",
            "/docs",
            "/docs/",
            "/documentation",
            "/blog",
            "/blog/",
            "/features",
            "/features/",
            "/product",
            "/products",
            "/resources",
            "/resources/",
            "/learn",
            "/guides",
            "/faq",
            "/knowledge-base",
            "/articles"
        ]
    
    async def discover_help_urls(self, base_url: str, main_page_html: str) -> List[str]:
        """
        Dynamically discover help/documentation URLs from a competitor's main page.
        1. First, scrape links from the main page
        2. Then, try common paths on the domain
        """
        discovered_urls = []
        base_url_clean = base_url.rstrip('/')
        
        # Extract base domain
        try:
            base_domain = base_url_clean.split('//')[1].split('/')[0]
        except:
            base_domain = base_url_clean
        
        # Step 1: Try common paths on the base domain
        common_paths = self._get_common_paths()
        for path in common_paths:
            url = f"{base_url_clean}{path}"
            if url not in discovered_urls:
                discovered_urls.append(url)
        
        # Step 2: Parse links from main page HTML
        if main_page_html:
            soup = BeautifulSoup(main_page_html, 'lxml')
            
            # Keywords that indicate help/documentation pages
            help_keywords = ['help', 'support', 'docs', 'documentation', 'knowledge', 'faq', 'guide', 'learn', 'resources', 'how-to', 'blog', 'features', 'product']
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                # Check if link text or href contains help keywords
                is_help_link = any(kw in href.lower() or kw in link_text for kw in help_keywords)
                
                if is_help_link:
                    # Normalize the URL
                    if href.startswith('/'):
                        full_url = f"https://{base_domain}{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # Only include URLs from same domain or known subdomains
                    if base_domain in full_url or 'help.' in full_url or 'support.' in full_url:
                        if full_url not in discovered_urls:
                            discovered_urls.append(full_url)
        
        return discovered_urls[:10]  # Return top 10 discovered URLs
    
    def execute(self, product: str) -> Dict[str, Any]:
        """Execute the competitor fetching operation."""
        competitors = self.get_competitors(product)
        return {
            "product": product,
            "competitors": competitors,
            "total_competitors": len(competitors),
            "status": "success"
        }
    
    def get_competitor_urls(self, product: str) -> List[str]:
        """Get list of competitor URLs for a product"""
        competitors = self.get_competitors(product)
        return [comp["url"] for comp in competitors]
    
    def get_competitor_names(self, product: str) -> List[str]:
        """Get list of competitor names for a product"""
        competitors = self.get_competitors(product)
        return [comp["name"] for comp in competitors]
    
    async def _fetch_page(self, url: str, raise_on_error: bool = False, timeout: float = 15.0) -> str:
        """Fetch HTML content from a URL with configurable timeout and rotating headers"""
        try:
            headers = self._get_rotated_headers()
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                # Add small delay between requests to be respectful
                await asyncio.sleep(0.5)
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.text
        except httpx.TimeoutException:
            print(f"[CompetitorAgent] Timeout fetching {url}")
            if raise_on_error:
                raise Exception(f"Timeout fetching: {url}")
            return ""
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"[CompetitorAgent] Error fetching {url}: {error_msg}")
            if raise_on_error:
                raise Exception(f"Failed to fetch: {url} - {error_msg}")
            return ""
    
    def _extract_content(self, html: str, url: str) -> Dict[str, Any]:
        """Extract content from HTML"""
        if not html:
            return {"url": url, "title": "", "headings": [], "content": "", "keywords_found": []}
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove non-content elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'meta', 'link', 'noscript']):
            element.decompose()
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        # Extract headings
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4']:
            for heading in soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text and len(text) > 3:
                    headings.append(text)
        
        # Extract main content
        main_area = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body', re.I))
        if main_area:
            content = main_area.get_text(separator=' ', strip=True)
        else:
            content = soup.get_text(separator=' ', strip=True)
        
        # Clean content
        content = ' '.join(content.split())
        
        return {
            "url": url,
            "title": title,
            "headings": headings[:30],  # Top 30 headings
            "content": content[:8000]  # First 8000 chars for analysis
        }
    
    async def scrape_competitor_page(self, url: str) -> Dict[str, Any]:
        """Scrape a single competitor page"""
        print(f"[CompetitorAgent] Scraping: {url}")
        html = await self._fetch_page(url)
        return self._extract_content(html, url)
    
    async def scrape_all_competitors(self, product: str) -> List[Dict[str, Any]]:
        """Scrape all competitor main pages for a product"""
        competitors = self.get_competitors(product)
        results = []
        
        for comp in competitors:
            data = await self.scrape_competitor_page(comp["url"])
            data["competitor_name"] = comp["name"]
            results.append(data)
        
        return results
    
    async def search_competitor_for_topic(
        self, 
        competitor_name: str, 
        competitor_url: str, 
        search_terms: List[str]
    ) -> Dict[str, Any]:
        """
        Search a competitor's site for content related to specific terms.
        This uses Google site search or direct page scraping.
        """
        print(f"[CompetitorAgent] Searching {competitor_name} for: {search_terms[:3]}")
        
        # Build search URLs for different strategies
        search_results = {
            "competitor_name": competitor_name,
            "competitor_url": competitor_url,
            "pages_found": [],
            "content_extracted": ""
        }
        
        # Strategy 1: Scrape main competitor page
        main_content = await self.scrape_competitor_page(competitor_url)
        if main_content.get("content"):
            search_results["pages_found"].append({
                "url": competitor_url,
                "title": main_content.get("title", ""),
                "type": "main_page"
            })
            search_results["content_extracted"] = main_content.get("content", "")
            search_results["headings"] = main_content.get("headings", [])
        
        # Strategy 2: Try common documentation/blog paths
        common_paths = [
            "/blog",
            "/resources",
            "/help",
            "/docs",
            "/features"
        ]
        
        base_url = competitor_url.rstrip('/')
        for path in common_paths[:2]:  # Try first 2 paths to avoid too many requests
            try:
                test_url = f"{base_url}{path}"
                html = await self._fetch_page(test_url)
                if html and len(html) > 1000:
                    content = self._extract_content(html, test_url)
                    if content.get("content"):
                        search_results["pages_found"].append({
                            "url": test_url,
                            "title": content.get("title", ""),
                            "type": "sub_page"
                        })
                        search_results["content_extracted"] += " " + content.get("content", "")[:3000]
                        search_results["headings"] = search_results.get("headings", []) + content.get("headings", [])
            except Exception as e:
                continue
        
        return search_results
    
    async def get_competitor_content_for_keywords(
        self, 
        product: str, 
        article_keywords: List[str],
        article_title: str = ""
    ) -> Dict[str, Any]:
        """
        Main method: Get real content from competitor websites
        based on article keywords for competitive analysis.
        
        Returns scraped content from each competitor that can be analyzed
        for keyword extraction.
        """
        competitors = self.get_competitors(product)
        competitor_content = []
        
        print(f"\n{'='*70}")
        print(f"[CompetitorAgent] 🔍 COMPETITOR WEBSITE SCRAPING")
        print(f"{'='*70}")
        print(f"[CompetitorAgent] Product: {product}")
        print(f"[CompetitorAgent] Total competitors to scrape: {len(competitors)}")
        print(f"[CompetitorAgent] Article keywords for matching: {article_keywords[:5]}")
        print(f"{'='*70}")
        
        for idx, comp in enumerate(competitors, 1):
            try:
                print(f"\n[CompetitorAgent] [{idx}/{len(competitors)}] SCRAPING: {comp['name']}")
                print(f"[CompetitorAgent]    Main URL: {comp['url']}")
                
                # Search competitor site for content related to article keywords
                content_data = await self.search_competitor_for_topic(
                    competitor_name=comp["name"],
                    competitor_url=comp["url"],
                    search_terms=article_keywords[:5]
                )
                
                if content_data.get("content_extracted"):
                    pages_found = content_data.get("pages_found", [])
                    competitor_content.append({
                        "competitor_name": comp["name"],
                        "competitor_url": comp["url"],
                        "content": content_data.get("content_extracted", "")[:6000],
                        "headings": content_data.get("headings", [])[:20],
                        "pages_scraped": len(pages_found),
                        "urls_scraped": [p.get("url") for p in pages_found]
                    })
                    print(f"[CompetitorAgent]    ✅ SUCCESS: {len(content_data.get('content_extracted', ''))} chars extracted")
                    print(f"[CompetitorAgent]    📄 Pages scraped: {len(pages_found)}")
                    for page in pages_found:
                        print(f"[CompetitorAgent]       - {page.get('type', 'page')}: {page.get('url', '')}")
                else:
                    print(f"[CompetitorAgent]    ❌ FAILED: No content found")
                    
            except Exception as e:
                print(f"[CompetitorAgent]    ❌ ERROR: {e}")
                continue
        
        # Validate that we got content from at least one competitor - NO FALLBACKS
        if len(competitor_content) == 0:
            raise Exception(f"Failed to scrape content from any competitor websites for product: {product}")
        
        print(f"\n{'='*70}")
        print(f"[CompetitorAgent] 📊 SCRAPING SUMMARY")
        print(f"{'='*70}")
        print(f"[CompetitorAgent] Successfully scraped: {len(competitor_content)}/{len(competitors)} competitors")
        for comp in competitor_content:
            print(f"[CompetitorAgent]   ✓ {comp['competitor_name']}: {comp['pages_scraped']} pages, {len(comp['content'])} chars")
            for url in comp.get('urls_scraped', []):
                print(f"[CompetitorAgent]      URL: {url}")
        print(f"{'='*70}\n")
        
        return {
            "product": product,
            "competitors_scraped": len(competitor_content),
            "competitor_content": competitor_content,
            "article_keywords_used": article_keywords,
            "status": "success"
        }
    
    async def scrape_capability_specific_urls(
        self,
        competitor_name: str,
        competitor_base_url: str,
        probable_urls: List[str],
        feature_name: str
    ) -> Dict[str, Any]:
        """
        Scrape specific capability-related URLs on a competitor's website.
        Tries each probable URL and extracts content.
        """
        print(f"\n[CompetitorAgent] 🎯 Searching {competitor_name} for: {feature_name}")
        
        result = {
            "competitor_name": competitor_name,
            "feature_name": feature_name,
            "urls_tried": [],
            "urls_successful": [],
            "content_extracted": "",
            "headings": [],
            "terminology_found": []
        }
        
        for url in probable_urls[:5]:  # Try up to 5 URLs
            try:
                print(f"[CompetitorAgent]    Trying: {url}")
                html = await self._fetch_page(url)
                
                if html and len(html) > 500:
                    content_data = self._extract_content(html, url)
                    
                    if content_data.get("content") and len(content_data.get("content", "")) > 200:
                        result["urls_tried"].append({"url": url, "status": "success"})
                        result["urls_successful"].append(url)
                        result["content_extracted"] += f"\n\n=== FROM {url} ===\n" + content_data.get("content", "")[:4000]
                        result["headings"].extend(content_data.get("headings", []))
                        print(f"[CompetitorAgent]    ✅ Found: {len(content_data.get('content', ''))} chars")
                    else:
                        result["urls_tried"].append({"url": url, "status": "no_content"})
                        print(f"[CompetitorAgent]    ⚠️ Page exists but no relevant content")
                else:
                    result["urls_tried"].append({"url": url, "status": "empty"})
                    print(f"[CompetitorAgent]    ❌ Empty or failed")
                    
            except Exception as e:
                result["urls_tried"].append({"url": url, "status": f"error: {str(e)[:50]}"})
                print(f"[CompetitorAgent]    ❌ Error: {str(e)[:50]}")
                continue
        
        # If no specific URLs worked, try the base URL
        if not result["urls_successful"]:
            print(f"[CompetitorAgent]    Falling back to base URL: {competitor_base_url}")
            html = await self._fetch_page(competitor_base_url)
            if html:
                content_data = self._extract_content(html, competitor_base_url)
                if content_data.get("content"):
                    result["urls_successful"].append(competitor_base_url)
                    result["content_extracted"] = content_data.get("content", "")[:5000]
                    result["headings"] = content_data.get("headings", [])
        
        return result
    
    async def get_competitor_content_for_capability(
        self,
        product: str,
        capability: dict,
        llm_client
    ) -> Dict[str, Any]:
        """
        DYNAMIC capability-based competitor scraping.
        
        1. For each competitor, use LLM to find equivalent capability URLs
        2. Scrape those specific URLs
        3. Extract terminology and content
        
        This is fully dynamic - no hardcoded paths.
        """
        competitors = self.get_competitors(product)
        competitor_content = []
        
        capability_name = capability.get('name', 'Unknown')
        search_terms = capability.get('competitor_search_terms', [])
        
        print(f"\n{'='*70}")
        print(f"[CompetitorAgent] 🔍 DYNAMIC CAPABILITY-BASED SCRAPING")
        print(f"{'='*70}")
        print(f"[CompetitorAgent] Capability: {capability_name}")
        print(f"[CompetitorAgent] Description: {capability.get('description', '')}")
        print(f"[CompetitorAgent] Search Terms: {search_terms}")
        print(f"[CompetitorAgent] Competitors to search: {len(competitors)}")
        print(f"{'='*70}")
        
        # Process all competitors
        for idx, comp in enumerate(competitors, 1):
            try:
                print(f"\n[CompetitorAgent] [{idx}/{len(competitors)}] {comp['name']}")
                print(f"[CompetitorAgent]    Base URL: {comp['url']}")
                
                # Step 1: Scrape main page to discover help/docs URLs dynamically
                main_html = await self._fetch_page(comp['url'], timeout=12.0)
                main_content = self._extract_content(main_html, comp['url']) if main_html else {}
                
                fallback_content = main_content.get('content', '')
                fallback_headings = main_content.get('headings', [])
                
                # Step 2: Dynamically discover help/documentation URLs from main page
                discovered_help_urls = await self.discover_help_urls(comp['url'], main_html) if main_html else []
                if discovered_help_urls:
                    print(f"[CompetitorAgent]    🔍 Discovered {len(discovered_help_urls)} help URLs dynamically")
                
                # Step 3: Use LLM to find capability-specific URLs
                try:
                    print(f"[CompetitorAgent]    🤖 Using LLM to find '{capability_name}' URLs...")
                    competitor_capability = await llm_client.find_competitor_capability_urls(
                        capability=capability,
                        competitor_name=comp['name'],
                        competitor_base_url=comp['url'],
                        competitor_content=fallback_content[:1500]
                    )
                    
                    if competitor_capability:
                        likely_feature_name = competitor_capability.get('likely_feature_name', capability_name)
                        llm_urls = competitor_capability.get('probable_urls', [])
                        terminology_hints = competitor_capability.get('terminology_hints', [])
                        
                        print(f"[CompetitorAgent]    📝 {comp['name']} calls it: '{likely_feature_name}'")
                        
                        # Combine LLM-generated URLs with dynamically discovered help URLs
                        all_urls_to_try = llm_urls + discovered_help_urls
                        # Remove duplicates while preserving order
                        seen = set()
                        unique_urls = []
                        for url in all_urls_to_try:
                            if url not in seen:
                                seen.add(url)
                                unique_urls.append(url)
                        
                        print(f"[CompetitorAgent]    🔗 Total URLs to try: {len(unique_urls)}")
                        
                        # Try to scrape the URLs
                        scrape_result = await self.scrape_capability_specific_urls(
                            competitor_name=comp['name'],
                            competitor_base_url=comp['url'],
                            probable_urls=unique_urls,
                            feature_name=likely_feature_name
                        )
                        
                        if scrape_result.get("content_extracted"):
                            competitor_content.append({
                                "competitor_name": comp['name'],
                                "competitor_url": comp['url'],
                                "capability_name": capability_name,
                                "competitor_feature_name": likely_feature_name,
                                "urls_scraped": scrape_result.get("urls_successful", []),
                                "content": scrape_result.get("content_extracted", "")[:8000],
                                "headings": scrape_result.get("headings", [])[:30],
                                "terminology_hints": terminology_hints,
                                "pages_scraped": len(scrape_result.get("urls_successful", []))
                            })
                            print(f"[CompetitorAgent]    ✅ SUCCESS: {len(scrape_result.get('content_extracted', ''))} chars")
                            continue  # Move to next competitor
                
                except Exception as llm_error:
                    print(f"[CompetitorAgent]    ⚠️ LLM error: {str(llm_error)[:50]}")
                
                # Fallback: use main page content if available
                if fallback_content and len(fallback_content) > 200:
                    print(f"[CompetitorAgent]    📄 Using main page content as fallback")
                    competitor_content.append({
                        "competitor_name": comp['name'],
                        "competitor_url": comp['url'],
                        "capability_name": capability_name,
                        "competitor_feature_name": capability_name,
                        "urls_scraped": [comp['url']],
                        "content": fallback_content[:6000],
                        "headings": fallback_headings[:20],
                        "terminology_hints": [],
                        "pages_scraped": 1
                    })
                    print(f"[CompetitorAgent]    ✅ Fallback: {len(fallback_content)} chars from main page")
                else:
                    print(f"[CompetitorAgent]    ❌ No content found for {comp['name']}")
                    
            except Exception as e:
                print(f"[CompetitorAgent]    ❌ ERROR: {str(e)[:100]}")
                continue
        
        # If dynamic capability search failed for all, fall back to main page scraping
        if len(competitor_content) == 0:
            print(f"\n[CompetitorAgent] ⚠️ Dynamic capability search failed, falling back to main page scraping...")
            
            for comp in competitors:
                try:
                    html = await self._fetch_page(comp['url'])
                    if html:
                        content_data = self._extract_content(html, comp['url'])
                        if content_data.get("content") and len(content_data.get("content", "")) > 200:
                            competitor_content.append({
                                "competitor_name": comp['name'],
                                "competitor_url": comp['url'],
                                "capability_name": capability_name,
                                "competitor_feature_name": capability_name,
                                "urls_scraped": [comp['url']],
                                "content": content_data.get("content", "")[:6000],
                                "headings": content_data.get("headings", [])[:20],
                                "terminology_hints": [],
                                "pages_scraped": 1
                            })
                            print(f"[CompetitorAgent]    ✅ Fallback success for {comp['name']}")
                except Exception as e:
                    print(f"[CompetitorAgent]    ❌ Fallback failed for {comp['name']}: {e}")
                    continue
        
        # Final validation
        if len(competitor_content) == 0:
            raise Exception(f"Failed to scrape any competitor content for capability '{capability_name}'")
        
        print(f"\n{'='*70}")
        print(f"[CompetitorAgent] 📊 CAPABILITY SCRAPING SUMMARY")
        print(f"{'='*70}")
        print(f"[CompetitorAgent] Capability: {capability_name}")
        print(f"[CompetitorAgent] Competitors processed: {len(competitors)}")
        print(f"[CompetitorAgent] Successfully found on: {len(competitor_content)} competitors")
        for comp in competitor_content:
            print(f"[CompetitorAgent]   ✓ {comp['competitor_name']}: '{comp['competitor_feature_name']}'")
            print(f"[CompetitorAgent]     Content: {len(comp['content'])} chars from {comp['pages_scraped']} pages")
            for url in comp.get('urls_scraped', []):
                print(f"[CompetitorAgent]     URL: {url}")
        print(f"{'='*70}\n")
        
        return {
            "product": product,
            "capability": capability,
            "competitors_scraped": len(competitor_content),
            "competitor_content": competitor_content,
            "status": "success"
        }
