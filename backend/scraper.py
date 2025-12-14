"""
Web Scraper Module for SEO Agent
Extracts article content for ChatGPT to analyze
NO FALLBACKS - raises exceptions on failure
"""

import httpx
import re
from bs4 import BeautifulSoup
from typing import Dict, List


class WebScraper:
    """Web scraper for extracting article content - NO FALLBACKS"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    
    async def fetch_page(self, url: str) -> str:
        """Fetch HTML content from a URL - raises exception on failure"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                html = response.text
                if not html or len(html) < 100:
                    raise Exception(f"Empty or invalid HTML response from URL: {url}")
                return html
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error fetching {url}: {e.response.status_code}")
        except httpx.TimeoutException:
            raise Exception(f"Timeout fetching {url}")
        except Exception as e:
            raise Exception(f"Failed to fetch URL {url}: {str(e)}")
    
    async def scrape_url(self, url: str) -> Dict:
        """Scrape a URL and extract content for keyword analysis - NO FALLBACKS"""
        html = await self.fetch_page(url)
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove non-content elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'meta', 'link']):
            element.decompose()
        
        # Extract title - REQUIRED
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        if not title:
            # Try h1 as fallback for title
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
        
        if not title:
            raise Exception(f"No title found in URL: {url}")
        
        # Extract all headings
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
        
        if not content or len(content) < 100:
            raise Exception(f"No meaningful content found in URL: {url}")
        
        return {
            "url": url,
            "title": title,
            "headings": headings,
            "content": content  # Full content - no clipping
        }
    
    async def scrape_multiple_urls(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs - raises exception if ALL fail"""
        results = []
        errors = []
        
        for url in urls:
            try:
                result = await self.scrape_url(url)
                results.append(result)
            except Exception as e:
                errors.append(f"{url}: {str(e)}")
        
        if len(results) == 0:
            raise Exception(f"Failed to scrape ALL URLs: {'; '.join(errors)}")
        
        return results


scraper = WebScraper()
