"""
SEMrush Keyword Analysis Module
Uses SEMrush URLs for keyword research - actual data must be retrieved via browser/API
"""

from typing import Dict, List
from backend.config import SEMRUSH_URL_TEMPLATE


class SEMrushAnalyzer:
    """
    Provides SEMrush URL generation for keyword analysis.
    Search volume data should come from actual SEMrush scraping or API.
    """
    
    def classify_keyword(self, keyword: str) -> Dict:
        """Classify a keyword by type based on word count"""
        word_count = len(keyword.split())
        
        return {
            'type': 'long_tail' if word_count >= 3 else 'short_tail',
            'word_count': word_count
        }
    
    def get_semrush_url(self, keyword: str) -> str:
        """Generate SEMrush URL for a keyword"""
        return SEMRUSH_URL_TEMPLATE.format(keyword=keyword.replace(' ', '+'))
    
    def analyze_keyword(self, keyword: str) -> Dict:
        """Return keyword with classification and SEMrush URL"""
        classification = self.classify_keyword(keyword)
        
        return {
            'keyword': keyword,
            'type': classification['type'],
            'word_count': classification['word_count'],
            'semrush_url': self.get_semrush_url(keyword)
        }
    
    def analyze_keywords_batch(self, keywords: List[str]) -> Dict:
        """Analyze multiple keywords"""
        results = []
        for keyword in keywords:
            if keyword and isinstance(keyword, str):
                results.append(self.analyze_keyword(keyword))
        
        short_tail = [r for r in results if r['type'] == 'short_tail']
        long_tail = [r for r in results if r['type'] == 'long_tail']
        
        return {
            'keywords_analyzed': len(results),
            'results': results,
            'short_tail_count': len(short_tail),
            'long_tail_count': len(long_tail)
        }


semrush_analyzer = SEMrushAnalyzer()

