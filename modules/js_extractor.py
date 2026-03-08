# modules/js_extractor.py
"""
JavaScript Endpoint Extractor
"""

import re
from typing import Set, Optional
from urllib.parse import urljoin

from utils.url_utils import URLUtils
from utils.logger import Logger
from config import JS_PATTERNS

class JSExtractor:
    """Extract endpoints from JavaScript files"""
    
    def __init__(self, base_domain: str, logger: Optional[Logger] = None):
        self.base_domain = base_domain
        self.logger = logger
    
    def extract(self, js_content: str, base_url: str) -> Set[str]:
        """
        Extract all endpoints from JavaScript content
        """
        endpoints = set()
        
        # Pattern-based extraction
        for pattern in JS_PATTERNS:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                endpoint = self._clean_endpoint(match, base_url)
                if endpoint:
                    endpoints.add(endpoint)
        
        # Additional heuristics
        endpoints.update(self._extract_urls(js_content, base_url))
        endpoints.update(self._extract_api_paths(js_content, base_url))
        
        return endpoints
    
    def _clean_endpoint(self, match: str, base_url: str) -> Optional[str]:
        """Clean and validate extracted endpoint"""
        endpoint = match.strip()
        
        if len(endpoint) < 2:
            return None
        
        # Skip common libraries/frameworks
        skip_patterns = ['jquery', 'bootstrap', 'analytics', 'gtag', 'ga(', 'fbq(']
        if any(pattern in endpoint.lower() for pattern in skip_patterns):
            return None
        
        # Normalize
        if endpoint.startswith(('http://', 'https://')):
            normalized = URLUtils.normalize(endpoint, base_url)
            if normalized and URLUtils.is_in_scope(normalized, self.base_domain):
                return normalized
        elif endpoint.startswith('/'):
            full_url = urljoin(base_url, endpoint)
            return URLUtils.normalize(full_url, base_url)
        elif endpoint.startswith(('./', '../')):
            full_url = urljoin(base_url, endpoint)
            return URLUtils.normalize(full_url, base_url)
        
        return None
    
    def _extract_urls(self, content: str, base_url: str) -> Set[str]:
        """Extract full URLs from content"""
        urls = set()
        
        # Find all URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        matches = re.findall(url_pattern, content)
        
        for match in matches:
            normalized = URLUtils.normalize(match, base_url)
            if normalized and URLUtils.is_in_scope(normalized, self.base_domain):
                urls.add(normalized)
        
        return urls
    
    def _extract_api_paths(self, content: str, base_url: str) -> Set[str]:
        """Extract API-like paths"""
        paths = set()
        
        # Common API patterns
        api_patterns = [
            r'["\'](/api/[v\d]+/[^"\']+)["\']',
            r'["\'](/v\d+/[^"\']+)["\']',
            r'["\'](/graphql/?[^"\']*)["\']',
            r'["\'](/rest/[^"\']+)["\']',
            r'["\'](/swagger[^"\']*)["\']',
            r'["\'](/docs/[^"\']+)["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                full_url = urljoin(base_url, match)
                normalized = URLUtils.normalize(full_url, base_url)
                if normalized:
                    paths.add(normalized)
        
        return paths
