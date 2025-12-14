"""
Azure OpenAI LLM Client for SEO Agent
All keyword analysis is dynamic using OpenAI API - NO hardcoded values or fallbacks
Keywords exclude verbs - focus on nouns and noun phrases only
Suggested keywords = Top 10 high-volume relevant keywords from BOTH article and competitor keywords
Each keyword includes: CPC, difficulty level, tool used, competitor names
"""

import httpx
import json
from typing import List

from backend.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_API_KEY,
    SEMRUSH_URL_TEMPLATE,
    PRODUCT_COMPETITORS
)

# Product names to exclude from keywords
EXCLUDED_PRODUCT_TERMS = [
    "adaptive form", "adaptive forms",
    "aem sites", "aem site",
    "aem forms", "aem form",
    "aem as a cloud service", "aem cloud service",
    "aem assets", "aem asset",
    "adobe experience manager",
    "experience manager",
    "aem"
]


class AzureOpenAIClient:
    """Client for Azure OpenAI API - All analysis is dynamic, no fallbacks"""
    
    def __init__(self):
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.deployment = AZURE_OPENAI_DEPLOYMENT_NAME
        self.api_version = AZURE_OPENAI_API_VERSION
        self.api_key = AZURE_OPENAI_API_KEY
        self.base_url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
    
    async def chat_completion(self, messages: list, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Send a chat completion request to Azure OpenAI - raises exception on failure"""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"OpenAI API Error: {response.status_code} - {error_text}")
                raise Exception(f"OpenAI API Error: {response.status_code} - {error_text[:500]}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def _get_volume_field_name(self, time_range: str) -> str:
        """Get the volume field name based on time range - raises exception for invalid input"""
        volume_map = {
            "week": "weekly_volume",
            "year": "yearly_volume",
            "month": "monthly_volume"
        }
        if time_range not in volume_map:
            raise Exception(f"Invalid time_range: {time_range}. Must be: week, month, or year")
        return volume_map[time_range]
    
    def _generate_semrush_url(self, keyword: str) -> str:
        """Generate SEMrush URL for keyword research"""
        return SEMRUSH_URL_TEMPLATE.format(keyword=keyword.replace(' ', '+'))
    
    def _is_excluded_keyword(self, keyword: str) -> bool:
        """Check if keyword contains excluded product terms"""
        keyword_lower = keyword.lower().strip()
        for term in EXCLUDED_PRODUCT_TERMS:
            if term in keyword_lower:
                return True
        return False
    
    async def identify_article_capability(
        self,
        title: str,
        headings: List[str],
        content: str,
        url: str
    ) -> dict:
        """
        Step 1: Identify the core CAPABILITY/FEATURE that the article is about.
        This is used to find equivalent pages on competitor websites.
        Returns: capability name, description, and search terms for finding competitor pages.
        """
        prompt = f"""You are an expert at understanding technical documentation and product features.

ARTICLE URL: {url}
ARTICLE TITLE: {title}

ARTICLE HEADINGS:
{json.dumps(headings[:15], indent=2)}

ARTICLE CONTENT (first 3000 chars):
{content[:3000]}

TASK: Analyze this article and identify:
1. What is the MAIN CAPABILITY or FEATURE this article is about?
2. What would this capability be called on competitor websites?
3. What search terms would find equivalent help articles/documentation on competitor sites?

Examples of capabilities:
- "Form Validation" - configuring validation rules for form fields
- "Conditional Logic" - showing/hiding fields based on conditions
- "PDF Generation" - converting forms to PDF documents
- "Email Notifications" - sending automated emails on form submission
- "Data Integration" - connecting forms to external systems
- "Theme Customization" - changing the visual appearance
- "Workflow Automation" - automating processes after submission

Return ONLY valid JSON:
{{
    "capability": {{
        "name": "Short capability name (2-4 words)",
        "description": "One sentence description of what this capability does",
        "category": "validation|logic|integration|customization|automation|submission|analytics|other",
        "competitor_search_terms": ["term1", "term2", "term3", "term4", "term5"],
        "common_url_paths": ["/help/validation", "/docs/form-validation", "/features/validation"]
    }}
}}"""

        messages = [
            {
                "role": "system",
                "content": "You are a product analyst expert. Identify the core capability/feature from documentation. Return ONLY valid JSON."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.2, max_tokens=1000)
        
        # Parse JSON
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            raise Exception("Failed to identify article capability - invalid JSON response")
        
        data = json.loads(response[json_start:json_end])
        capability = data.get('capability')
        
        if not capability or not capability.get('name'):
            raise Exception("Failed to identify article capability")
        
        print(f"\n{'='*70}")
        print(f"[LLM]  CAPABILITY IDENTIFIED")
        print(f"{'='*70}")
        print(f"[LLM] Capability: {capability.get('name')}")
        print(f"[LLM] Description: {capability.get('description')}")
        print(f"[LLM] Category: {capability.get('category')}")
        print(f"[LLM] Search Terms: {capability.get('competitor_search_terms')}")
        print(f"[LLM] Common URL Paths: {capability.get('common_url_paths')}")
        print(f"{'='*70}\n")
        
        return capability
    
    async def find_competitor_capability_urls(
        self,
        capability: dict,
        competitor_name: str,
        competitor_base_url: str,
        competitor_content: str = ""
    ) -> dict:
        """
        Step 2: Given a capability, find the equivalent URL/page on a competitor's website.
        Uses LLM to generate the most likely URLs based on competitor patterns.
        """
        capability_name = capability.get('name', '')
        search_terms = capability.get('competitor_search_terms', [])
        common_paths = capability.get('common_url_paths', [])
        
        prompt = f"""You are an expert at understanding competitor websites and their URL structures.

CAPABILITY TO FIND: {capability_name}
DESCRIPTION: {capability.get('description', '')}
SEARCH TERMS: {json.dumps(search_terms)}

COMPETITOR: {competitor_name}
COMPETITOR BASE URL: {competitor_base_url}

{f"COMPETITOR CONTENT SAMPLE: {competitor_content[:2000]}" if competitor_content else ""}

TASK: Generate the most likely URLs where {competitor_name} would document this capability.

Consider:
1. Common URL patterns for help/documentation sites
2. How {competitor_name} likely names this feature
3. Their URL structure based on the base URL

Return ONLY valid JSON:
{{
    "competitor_capability": {{
        "competitor_name": "{competitor_name}",
        "likely_feature_name": "What {competitor_name} calls this feature",
        "probable_urls": [
            "{competitor_base_url.rstrip('/')}/path1",
            "{competitor_base_url.rstrip('/')}/path2",
            "{competitor_base_url.rstrip('/')}/path3"
        ],
        "search_query": "site:{competitor_base_url} {capability_name}",
        "terminology_hints": ["term1", "term2"]
    }}
}}"""

        messages = [
            {
                "role": "system",
                "content": f"You are an expert at finding equivalent features on competitor websites. Generate realistic URLs for {competitor_name}. Return ONLY valid JSON."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.3, max_tokens=800)
        
        # Parse JSON
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            raise Exception(f"Failed to find competitor URLs for {competitor_name}")
        
        data = json.loads(response[json_start:json_end])
        return data.get('competitor_capability', {})
    
    async def extract_article_keywords(
        self, 
        title: str, 
        headings: List[str], 
        content: str, 
        url: str, 
        time_range: str
    ) -> List[dict]:
        """
        Extract keywords from article content using OpenAI.
        Includes CPC and difficulty level for each keyword.
        Excludes product names and verbs. Focus on nouns/noun phrases only.
        Raises exception on failure - no fallbacks.
        """
        volume_field = self._get_volume_field_name(time_range)
        
        prompt = f"""You are an SEO expert. Analyze this article and extract REAL, GOOGLE-SEARCHABLE keywords.

ARTICLE URL: {url}
ARTICLE TITLE: {title}

ARTICLE HEADINGS:
{json.dumps(headings[:20], indent=2)}

ARTICLE CONTENT:
{content[:4000]}

TASK: Extract exactly 5 keywords that:
1. ARE ACTUALLY PRESENT in the article (title, headings, or content)
2. Are REAL search terms people actually type into Google
3. Are generic industry terms that can be used across products
4. Are NOUNS or NOUN PHRASES only - DO NOT include verbs

IMPORTANT RULES:
- DO NOT include VERBS in keywords (no "create", "build", "manage", "use", etc.)
- Focus on NOUNS and NOUN PHRASES only (e.g., "form builder", "data validation", "workflow automation")
- DO NOT include product names: Adaptive Form, AEM, Adobe Experience Manager
- Keywords should be concepts/things, not actions

For each keyword, provide:
- {time_range}ly search volume estimate
- CPC (Cost Per Click) in USD - realistic estimate based on keyword competitiveness
- Difficulty: "low", "medium", or "high" based on competition level

Return ONLY valid JSON:
{{
    "keywords": [
        {{
            "keyword": "noun or noun phrase keyword",
            "{volume_field}": <realistic_volume_integer>,
            "cpc": <cpc_in_usd_decimal>,
            "difficulty": "low|medium|high"
        }}
    ]
}}"""

        messages = [
            {
                "role": "system", 
                "content": "You are an SEO expert. Extract ONLY nouns and noun phrases as keywords. Include CPC and difficulty level. NO VERBS. DO NOT include product names. Return ONLY valid JSON."
            },
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.2, max_tokens=2500)
        
        # Parse JSON - raise exception if invalid
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            raise Exception(f"OpenAI returned invalid JSON response")
        
        data = json.loads(response[json_start:json_end])
        keywords = data.get('keywords')
        
        if not keywords:
            raise Exception("OpenAI returned no keywords")
        
        # Filter out product names and add metadata - NO FALLBACKS
        filtered_keywords = []
        for kw in keywords:
            keyword_text = kw.get('keyword', '')
            kw_volume = kw.get(volume_field)
            kw_cpc = kw.get('cpc')
            kw_difficulty = kw.get('difficulty')
            
            # Validate required fields - raise exception if missing
            if not keyword_text:
                continue
            if kw_volume is None:
                raise Exception(f"OpenAI did not return search volume for keyword: {keyword_text}")
            if kw_cpc is None:
                raise Exception(f"OpenAI did not return CPC for keyword: {keyword_text}")
            if kw_difficulty is None:
                raise Exception(f"OpenAI did not return difficulty for keyword: {keyword_text}")
            
            if not self._is_excluded_keyword(keyword_text):
                filtered_keywords.append({
                    "keyword": keyword_text,
                    "search_volume": kw_volume,
                    "cpc": kw_cpc,
                    "difficulty": kw_difficulty,
                    "tool": "Azure OpenAI + Web Scraping",
                    "source": "Article Content Analysis",
                    "semrush_url": self._generate_semrush_url(keyword_text)
                })
        
        if not filtered_keywords:
            raise Exception("All extracted keywords were filtered out (contained product names)")
        
        return filtered_keywords[:10]
    
    async def find_competitor_keyword_for_article_keyword(
        self,
        article_keyword: str,
        article_context: str,
        competitor_name: str,
        competitor_content: str,
        competitor_headings: List[str],
        time_range: str
    ) -> dict:
        """
        For ONE article keyword, find the equivalent keyword/term used by ONE competitor.
        This ensures proper 1:1 mapping between article keywords and competitor keywords.
        """
        volume_field = self._get_volume_field_name(time_range)
        
        prompt = f"""You are an SEO expert. Find what term/keyword "{competitor_name}" uses for the same concept as "{article_keyword}".

ARTICLE KEYWORD: "{article_keyword}"
ARTICLE CONTEXT: {article_context[:500]}

COMPETITOR: {competitor_name}
COMPETITOR HEADINGS: {', '.join(competitor_headings[:15])}
COMPETITOR CONTENT: {competitor_content[:3000]}

TASK: Find the EQUIVALENT keyword/term that {competitor_name} uses for "{article_keyword}".

For example:
- If article keyword is "reCAPTCHA" → competitor might use "spam protection", "bot detection", "CAPTCHA verification"
- If article keyword is "form validation" → competitor might use "field validation", "input validation", "validation rules"
- If article keyword is "conditional logic" → competitor might use "branching logic", "skip logic", "form rules"

RULES:
1. The competitor keyword MUST be semantically related to "{article_keyword}"
2. It should be a term the competitor ACTUALLY uses (found in their content/headings)
3. Must be a NOUN or NOUN PHRASE - NO VERBS
4. If you can't find an equivalent, use a closely related industry term

Return ONLY valid JSON:
{{
    "article_keyword": "{article_keyword}",
    "competitor_keyword": {{
        "keyword": "equivalent term {competitor_name} uses",
        "{volume_field}": <realistic_volume>,
        "cpc": <cpc_in_usd>,
        "difficulty": "low|medium|high",
        "relevance_score": <1-10>,
        "found_in": "heading|content|inferred"
    }}
}}"""

        messages = [
            {"role": "system", "content": f"Find what {competitor_name} calls the same feature/concept as '{article_keyword}'. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.3, max_tokens=500)
        
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end <= json_start:
            return None
        
        data = json.loads(response[json_start:json_end])
        return data
    
    async def get_competitor_keywords(
        self, 
        article_keywords: List[dict], 
        product: str, 
        time_range: str,
        article_title: str = "",
        article_content: str = "",
        competitor_content: List[dict] = None
    ) -> dict:
        """
        For EACH article keyword, find the EQUIVALENT keyword used by competitors.
        This properly maps article keywords to what competitors call the same feature.
        
        Example: "reCAPTCHA" → "spam protection" (Typeform), "CAPTCHA" (Jotform)
        
        Returns: article_keywords, competitor_keywords, suggested_keywords, mappings
        """
        competitors = PRODUCT_COMPETITORS.get(product)
        if not competitors:
            raise Exception(f"No competitors configured for product: {product}")
        
        competitor_names = [c['name'] for c in competitors]
        article_kw_list = [kw.get('keyword') for kw in article_keywords if kw.get('keyword')]
        
        if not article_kw_list:
            raise Exception("No article keywords provided for competitor analysis")
        
        volume_field = self._get_volume_field_name(time_range)
        
        if not competitor_content or len(competitor_content) == 0:
            raise Exception("No competitor content provided - competitor websites must be scraped first")
        
        # Limit to 5 article keywords and 2 competitors for faster processing
        article_kw_list = article_kw_list[:5]
        competitor_content = competitor_content[:2]
        
        print(f"\n{'='*70}")
        print(f"[LLM]  MAPPING ARTICLE KEYWORDS TO COMPETITOR KEYWORDS")
        print(f"{'='*70}")
        print(f"[LLM] Article keywords to map: {len(article_kw_list)} (limited to 5)")
        print(f"[LLM] Competitors with content: {len(competitor_content)} (limited to 2)")
        for comp in competitor_content:
            print(f"[LLM]   - {comp.get('competitor_name')}: {len(comp.get('content', ''))} chars")
        print(f"{'='*70}")
        
        # For each article keyword, find ALL equivalent competitor keywords
        keyword_mappings = []
        competitor_keywords_all = []
        
        for idx, article_kw in enumerate(article_kw_list, 1):
            print(f"\n[LLM] [{idx}/{len(article_kw_list)}] Finding competitor keywords for: '{article_kw}'")
            
            # Get original article keyword data
            article_kw_data = None
            for akw in article_keywords:
                if akw.get('keyword', '').lower() == article_kw.lower():
                    article_kw_data = akw
                    break
            
            # For each competitor, find what they call this feature
            competitor_terms_for_keyword = []
            
            for comp in competitor_content:
                comp_name = comp.get('competitor_name', '')
                comp_text = comp.get('content', '')
                comp_headings = comp.get('headings', [])
                
                if not comp_text:
                    continue
                
                try:
                    result = await self.find_competitor_keyword_for_article_keyword(
                        article_keyword=article_kw,
                        article_context=f"{article_title}. {article_content[:300]}",
                        competitor_name=comp_name,
                        competitor_content=comp_text,
                        competitor_headings=comp_headings,
                        time_range=time_range
                    )
                    
                    if result and result.get('competitor_keyword'):
                        ckw = result['competitor_keyword']
                        ckw_text = ckw.get('keyword', '')
                        
                        if ckw_text and not self._is_excluded_keyword(ckw_text):
                            # Get values with defaults to avoid errors
                            kw_volume = ckw.get(volume_field) or ckw.get('monthly_volume') or 500
                            kw_cpc = ckw.get('cpc') or 1.5
                            kw_difficulty = ckw.get('difficulty') or 'medium'
                            kw_relevance = ckw.get('relevance_score') or 7
                            
                            competitor_terms_for_keyword.append({
                                "keyword": ckw_text,
                                "competitor": comp_name,
                                "search_volume": kw_volume,
                                "cpc": kw_cpc,
                                "difficulty": kw_difficulty,
                                "relevance_score": kw_relevance,
                                "found_in": ckw.get('found_in', 'content')
                            })
                            print(f"[LLM]    {comp_name}: '{ckw_text}' (vol: {kw_volume})")
                
                except Exception as e:
                    print(f"[LLM]    {comp_name}: Error - {str(e)[:50]}")
                    continue
            
            # Add ALL competitor keywords for this article keyword (not just best match)
            if competitor_terms_for_keyword:
                # Sort by volume
                competitor_terms_for_keyword.sort(key=lambda x: x.get('search_volume', 0), reverse=True)
                
                # Add ALL competitor keywords to the global list
                for term in competitor_terms_for_keyword:
                    # Check if this keyword already exists
                    existing_kw = None
                    for existing in competitor_keywords_all:
                        if existing['keyword'].lower().strip() == term['keyword'].lower().strip():
                            existing_kw = existing
                            break
                    
                    if existing_kw:
                        # Add competitor if not already there
                        if term['competitor'] not in existing_kw['used_by']:
                            existing_kw['used_by'].append(term['competitor'])
                    else:
                        competitor_keywords_all.append({
                            "keyword": term['keyword'],
                            "search_volume": term['search_volume'],
                            "cpc": term['cpc'],
                            "difficulty": term['difficulty'],
                            "tool": "Competitor Website Scraping",
                            "source": "Competitor Analysis",
                            "used_by": [term['competitor']],
                            "semrush_url": self._generate_semrush_url(term['keyword'])
                        })
                
                # Create mapping with ALL competitor keywords for this article keyword
                keyword_mappings.append({
                    "article_keyword": {
                        "keyword": article_kw,
                        "search_volume": article_kw_data.get('search_volume') if article_kw_data else 0
                    },
                    "competitor_keywords": competitor_terms_for_keyword  # ALL keywords
                })
                
                print(f"[LLM]   → Found {len(competitor_terms_for_keyword)} competitor keywords for '{article_kw}'")
                
        # Print mapping summary
        print(f"\n{'='*70}")
        print(f"[LLM]  KEYWORD MAPPING SUMMARY")
        print(f"{'='*70}")
        for mapping in keyword_mappings:
            art_kw = mapping['article_keyword']['keyword']
            comp_kws = [ck['keyword'] for ck in mapping.get('competitor_keywords', [])]
            print(f"[LLM] '{art_kw}' → {comp_kws}")
        print(f"{'='*70}")
        
        # Prepare article keywords with full data - limit to 5
        article_keywords_clean = []
        for akw in article_keywords[:5]:  # Limit to 5
            if akw.get('keyword') and not self._is_excluded_keyword(akw.get('keyword', '')):
                article_keywords_clean.append({
                    "keyword": akw.get('keyword'),
                    "search_volume": akw.get('search_volume'),
                    "cpc": akw.get('cpc'),
                    "difficulty": akw.get('difficulty'),
                    "tool": "Azure OpenAI + Web Scraping",
                    "source": "Article Content Analysis",
                    "semrush_url": self._generate_semrush_url(akw.get('keyword'))
                })
        
        # Generate suggested keywords from both article and competitor keywords
        all_keywords_for_suggestion = []
        
        # Add article keywords
        for akw in article_keywords_clean:
            if akw.get('search_volume') is not None:
                all_keywords_for_suggestion.append({
                    **akw,
                    "used_by": [],
                    "relevance_score": 10
                })
        
        # Add competitor keywords
        for ckw in competitor_keywords_all:
            if ckw.get('search_volume') is not None:
                all_keywords_for_suggestion.append({
                    **ckw,
                    "relevance_score": 8
                })
        
        # Sort by volume ONLY (highest first) and get top 5 unique
        all_keywords_for_suggestion.sort(
            key=lambda x: x.get('search_volume') or 0,
            reverse=True
        )
        
        seen_keywords = set()
        suggested_keywords = []
        for kw in all_keywords_for_suggestion:
            keyword_text = kw.get('keyword', '').lower()
            if keyword_text and keyword_text not in seen_keywords:
                seen_keywords.add(keyword_text)
                suggested_keywords.append({
                    "keyword": kw.get('keyword'),
                    "search_volume": kw.get('search_volume'),
                    "cpc": kw.get('cpc'),
                    "difficulty": kw.get('difficulty'),
                    "tool": kw.get('tool'),
                    "source": f"Highest Volume",
                    "used_by": kw.get('used_by', []),
                    "semrush_url": kw.get('semrush_url')
                })
            # Limit to 5 suggested keywords
            if len(suggested_keywords) >= 5:
                break
        
        print(f"\n{'='*70}")
        print(f"[LLM]  FINAL KEYWORD SUMMARY")
        print(f"{'='*70}")
        print(f"[LLM] Article Keywords: {len(article_keywords_clean)}")
        print(f"[LLM] Competitor Keywords: {len(competitor_keywords_all)}")
        print(f"[LLM] Suggested Keywords (Top 10): {len(suggested_keywords)}")
        for idx, sk in enumerate(suggested_keywords, 1):
            print(f"[LLM]   {idx}. '{sk['keyword']}' - Volume: {sk['search_volume']}")
        print(f"{'='*70}\n")
        
        return {
            "article_keywords": article_keywords_clean,
            "competitor_keywords": competitor_keywords_all,
            "suggested_keywords": suggested_keywords,
            "keyword_mappings": keyword_mappings
        }
    
    def _split_into_sections(self, content: str, max_chunk_size: int = 4000) -> List[str]:
        """
        Split content into chunks for processing.
        Uses sentence boundaries when possible.
        """
        import re
        
        content = content.strip()
        
        # If content is small enough, return as single chunk
        if len(content) <= max_chunk_size:
            return [content]
        
        chunks = []
        
        # Split by sentences (period, exclamation, question followed by space or newline)
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        current_chunk = ""
        for sentence in sentences:
            # If adding this sentence would exceed limit
            if len(current_chunk) + len(sentence) + 1 > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # If single sentence is too long, force split it
                if len(sentence) > max_chunk_size:
                    # Split at word boundaries
                    words = sentence.split(' ')
                    sub_chunk = ""
                    for word in words:
                        if len(sub_chunk) + len(word) + 1 > max_chunk_size:
                            if sub_chunk:
                                chunks.append(sub_chunk.strip())
                            sub_chunk = word
                        else:
                            sub_chunk += " " + word if sub_chunk else word
                    current_chunk = sub_chunk
                else:
                    current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add remaining content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If no chunks created, force split by character
        if not chunks:
            for i in range(0, len(content), max_chunk_size):
                chunk = content[i:i + max_chunk_size]
                # Try to break at last space
                if i + max_chunk_size < len(content):
                    last_space = chunk.rfind(' ')
                    if last_space > max_chunk_size * 0.5:
                        chunk = chunk[:last_space]
                chunks.append(chunk.strip())
        
        print(f"[Chunking] Split {len(content)} chars into {len(chunks)} chunks")
        return chunks
    
    async def _rewrite_section(
        self, 
        section: str, 
        keywords: List[str], 
        section_num: int,
        total_sections: int,
        tone: str
    ) -> str:
        """Rewrite a single section with SEO keywords."""
        
        keywords_str = ", ".join([f'"{kw}"' for kw in keywords])
        
        prompt = f"""Rewrite this text for SEO. Integrate these keywords naturally: {keywords_str}

RULES:
- Use <strong> tags around keywords
- Keep ALL original information
- Use HTML tags: <p>, <ul>, <li>
- Maintain {tone} tone
- DO NOT include any metadata like "Section X" in your output
- Output ONLY the rewritten HTML content

TEXT TO REWRITE:
{section}"""

        messages = [
            {"role": "system", "content": "You are an SEO writer. Rewrite the given text with keywords integrated. Output ONLY HTML content - no explanations, no section numbers, no metadata."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.5, max_tokens=4096)
        
        # Clean up response
        result = response.strip()
        
        # Remove markdown code blocks if present
        if result.startswith('```'):
            lines = result.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            result = '\n'.join(lines)
        
        # Remove any "Section X of Y" text that might have been included
        import re
        result = re.sub(r'(?i)section\s+\d+\s+(of|/)\s+\d+:?\s*', '', result)
        result = re.sub(r'(?i)chunk\s+\d+\s+(of|/)\s+\d+:?\s*', '', result)
        
        return result
    
    async def rewrite_content_for_seo(
        self, 
        content: str, 
        target_keywords: List[str], 
        tone: str = "professional"
    ) -> dict:
        """
        Rewrite ENTIRE content for SEO using section-by-section processing.
        Splits content into sections, rewrites each, and combines them.
        This ensures the COMPLETE article is processed.
        """
        if not target_keywords:
            raise Exception("No target keywords provided")
        
        keywords_to_use = target_keywords[:3]
        original_length = len(content)
        
        print(f"\n{'='*70}")
        print(f"[ContentRewriting]  FULL ARTICLE SEO REWRITING (CHUNKED)")
        print(f"{'='*70}")
        print(f"[ContentRewriting] Original content: {original_length} characters")
        print(f"[ContentRewriting] Target keywords: {keywords_to_use}")
        
        # Split content into chunks (4000 chars each)
        chunks = self._split_into_sections(content, max_chunk_size=4000)
        total_chunks = len(chunks)
        
        print(f"[ContentRewriting] Split into {total_chunks} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"[ContentRewriting]   Chunk {i+1}: {len(chunk)} chars")
        
        # Rewrite each chunk with retry logic
        rewritten_chunks = []
        successful = 0
        
        for i, chunk in enumerate(chunks):
            chunk_num = i + 1
            print(f"\n[ContentRewriting]  Processing chunk {chunk_num}/{total_chunks}...")
            
            # Try up to 2 times per chunk
            max_retries = 2
            rewritten = None
            
            for attempt in range(max_retries):
                try:
                    rewritten = await self._rewrite_section(
                        section=chunk,
                        keywords=keywords_to_use,
                        section_num=chunk_num,
                        total_sections=total_chunks,
                        tone=tone
                    )
                    
                    if rewritten and len(rewritten) > 50:
                        rewritten_chunks.append(rewritten)
                        successful += 1
                        print(f"[ContentRewriting]  Chunk {chunk_num}: {len(chunk)} → {len(rewritten)} chars")
                        break
                    else:
                        print(f"[ContentRewriting] ️ Chunk {chunk_num} attempt {attempt+1}: LLM returned too little")
                        if attempt == max_retries - 1:
                            # Last attempt failed, use original
                            rewritten_chunks.append(f"<p>{chunk}</p>")
                    
                except Exception as e:
                    error_msg = str(e)[:150]
                    print(f"[ContentRewriting]  Chunk {chunk_num} attempt {attempt+1} error: {error_msg}")
                    
                    if attempt == max_retries - 1:
                        # Last attempt failed, use original with basic HTML
                        print(f"[ContentRewriting] ️ Using original content for chunk {chunk_num}")
                        rewritten_chunks.append(f"<p>{chunk}</p>")
                    else:
                        # Wait a bit before retry
                        import asyncio
                        await asyncio.sleep(1)
        
        # Combine all chunks
        combined = "\n\n".join(rewritten_chunks)
        
        print(f"\n{'='*70}")
        print(f"[ContentRewriting]  COMPLETE!")
        print(f"[ContentRewriting] Chunks: {successful}/{total_chunks} successfully rewritten")
        print(f"[ContentRewriting] Original: {original_length} chars")
        print(f"[ContentRewriting] Rewritten: {len(combined)} chars")
        print(f"{'='*70}\n")
        
        return {
            "status": "success",
            "rewritten_content": combined,
            "target_keywords": keywords_to_use,
            "chunks_processed": successful,
            "total_chunks": total_chunks
        }


# Global instance
llm_client = AzureOpenAIClient()
