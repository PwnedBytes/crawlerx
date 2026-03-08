# core/parser.py
"""
HTML Content Parser
"""

import re
from typing import Set, List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from utils.url_utils import URLUtils
from config import LINK_ELEMENTS, JS_PATTERNS, INTERESTING_PATHS

class Parser:
    """Parse HTML and extract links, endpoints, parameters"""
    
    def __init__(self, base_url: str, logger=None):
        self.base_url = base_url
        self.base_domain = URLUtils.get_domain(base_url)
        self.logger = logger
    
    def parse(self, html: str, current_url: str) -> Dict:
        """
        Parse HTML content and extract all relevant data
        Returns dict with links, parameters, directories, etc.
        """
        if self.logger:
            self.logger.debug(f"[PARSER] Parsing {len(html)} bytes from {current_url}")
        
        soup = BeautifulSoup(html, 'lxml')
        
        result = {
            'links': set(),
            'parameters': set(),
            'directories': set(),
            'js_files': set(),
            'form_actions': set(),
            'comments': [],
            'title': '',
            'meta_refresh': None,
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            result['title'] = title_tag.get_text(strip=True)
            if self.logger:
                self.logger.debug(f"[PARSER] Title: {result['title'][:50]}...")
        
        # Extract links from various elements
        for tag, attr in LINK_ELEMENTS.items():
            elements = soup.find_all(tag)
            if self.logger:
                self.logger.debug(f"[PARSER] Found {len(elements)} <{tag}> tags")
            
            for element in elements:
                url = element.get(attr)
                if url:
                    full_url = urljoin(current_url, url)
                    normalized = URLUtils.normalize(full_url, current_url)
                    
                    if normalized:
                        result['links'].add(normalized)
                        
                        # Track JS files separately
                        if tag == 'script' and URLUtils.get_file_extension(normalized) in ['js', 'javascript']:
                            result['js_files'].add(normalized)
                            if self.logger:
                                self.logger.debug(f"[PARSER] Found JS file: {normalized}")
                        
                        # Track form actions
                        if tag == 'form':
                            result['form_actions'].add(normalized)
                            if self.logger:
                                self.logger.debug(f"[PARSER] Found form action: {normalized}")
                        
                        # Extract parameters
                        params = URLUtils.extract_parameters(normalized)
                        if params and self.logger:
                            self.logger.debug(f"[PARSER] Parameters in {normalized}: {params}")
                        result['parameters'].update(params)
                        
                        # Extract directories
                        dirs = URLUtils.extract_directories(normalized)
                        result['directories'].update(dirs)
        
        if self.logger:
            self.logger.debug(f"[PARSER] Total links extracted: {len(result['links'])}")
            self.logger.debug(f"[PARSER] Total JS files: {len(result['js_files'])}")
            self.logger.debug(f"[PARSER] Total parameters: {len(result['parameters'])}")
            self.logger.debug(f"[PARSER] Total directories: {len(result['directories'])}")
        
        # Extract meta refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            match = re.search(r'url=(.+)', content, re.IGNORECASE)
            if match:
                result['meta_refresh'] = urljoin(current_url, match.group(1).strip())
                if self.logger:
                    self.logger.debug(f"[PARSER] Meta refresh found: {result['meta_refresh']}")
        
        # Extract comments
        comments = soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--'))
        for comment in comments:
            result['comments'].append(comment.strip())
            # Look for URLs in comments
            urls_in_comments = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', comment)
            for url in urls_in_comments:
                normalized = URLUtils.normalize(urljoin(current_url, url), current_url)
                if normalized:
                    result['links'].add(normalized)
                    if self.logger:
                        self.logger.debug(f"[PARSER] Found URL in comment: {normalized}")
        
        return result
    
    def extract_js_endpoints(self, js_content: str) -> Set[str]:
        """
        Extract API endpoints from JavaScript content
        """
        if self.logger:
            self.logger.debug(f"[JS_PARSE] Analyzing {len(js_content)} bytes of JavaScript")
        
        endpoints = set()
        
        for pattern in JS_PATTERNS:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                endpoint = self._clean_endpoint(match)
                if endpoint:
                    endpoints.add(endpoint)
                    if self.logger:
                        self.logger.debug(f"[JS_PARSE] Found endpoint: {endpoint}")
        
        if self.logger:
            self.logger.debug(f"[JS_PARSE] Total endpoints extracted: {len(endpoints)}")
        
        return endpoints
    
    def _clean_endpoint(self, match: str) -> Optional[str]:
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
            normalized = URLUtils.normalize(endpoint, self.base_url)
            if normalized and URLUtils.is_in_scope(normalized, self.base_domain):
                return normalized
        elif endpoint.startswith('/'):
            full_url = urljoin(self.base_url, endpoint)
            return URLUtils.normalize(full_url, self.base_url)
        elif endpoint.startswith(('./', '../')):
            full_url = urljoin(self.base_url, endpoint)
            return URLUtils.normalize(full_url, self.base_url)
        
        return None
    
    def find_interesting_paths(self, text: str) -> Set[str]:
        """
        Find interesting paths/patterns in text
        """
        found = set()
        text_lower = text.lower()
        
        for path in INTERESTING_PATHS:
            patterns = [
                rf'["\'](/{path}/?[^"\']*)["\']',
                rf'["\']({path}/?[^"\']*)["\']',
                rf'https?://[^/\s]+/{path}/?[^\s"\']*',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                if matches and self.logger:
                    self.logger.debug(f"[PATH_FIND] Found interesting path '{path}': {matches[:3]}")
                found.update(matches)
        
        return found
    
    def extract_form_parameters(self, html: str) -> Set[str]:
        """
        Extract input names from forms
        """
        params = set()
        soup = BeautifulSoup(html, 'lxml')
        
        for input_tag in soup.find_all(['input', 'textarea', 'select']):
            name = input_tag.get('name')
            if name:
                params.add(name)
                if self.logger:
                    self.logger.debug(f"[FORM_PARSE] Input name: {name}")
            
            id_attr = input_tag.get('id')
            if id_attr:
                params.add(id_attr)
        
        return params
