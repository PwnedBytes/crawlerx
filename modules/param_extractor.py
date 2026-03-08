# modules/param_extractor.py
"""
Parameter Extractor
"""

import re
from typing import Set, Dict, List
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

class ParamExtractor:
    """Extract parameters from various sources"""
    
    def __init__(self):
        self.common_params = {
            'id', 'page', 'search', 'query', 'q', 's', 'keyword',
            'category', 'cat', 'type', 'format', 'view', 'action',
            'callback', 'jsonp', 'api', 'key', 'token', 'auth',
            'user', 'username', 'email', 'password', 'pass', 'pwd',
            'redirect', 'return', 'next', 'url', 'link', 'target',
            'file', 'path', 'folder', 'dir', 'location', 'site',
            'host', 'port', 'ip', 'domain', 'server', 'env',
            'debug', 'test', 'dev', 'staging', 'prod', 'mode',
            'version', 'v', 'ver', 'api_key', 'apikey', 'secret',
        }
    
    def from_url(self, url: str) -> Set[str]:
        """Extract parameters from URL query string"""
        params = set()
        
        try:
            parsed = urlparse(url)
            if parsed.query:
                qs = parse_qs(parsed.query)
                params.update(qs.keys())
        except Exception:
            pass
        
        return params
    
    def from_form(self, html: str) -> Set[str]:
        """Extract parameters from HTML forms"""
        params = set()
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            for form in soup.find_all('form'):
                # Get method
                method = form.get('method', 'get').upper()
                
                # Extract inputs
                for inp in form.find_all(['input', 'textarea', 'select']):
                    name = inp.get('name')
                    if name:
                        params.add(name)
                    
                    # Also check id as fallback
                    id_attr = inp.get('id')
                    if id_attr:
                        params.add(id_attr)
        except Exception:
            pass
        
        return params
    
    def from_javascript(self, js_content: str) -> Set[str]:
        """Extract parameters from JavaScript"""
        params = set()
        
        # Look for common parameter patterns
        patterns = [
            r'["\']([a-zA-Z_][a-zA-Z0-9_]*)\s*["\']\s*:\s*',
            r'getParameter\(["\']([^"\']+)["\']',
            r'params\.([a-zA-Z_][a-zA-Z0-9_]*)',
            r'query\.([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content)
            params.update(matches)
        
        return params
    
    def from_json(self, json_content: str) -> Set[str]:
        """Extract keys from JSON responses"""
        params = set()
        
        try:
            import json
            data = json.loads(json_content)
            
            def extract_keys(obj, prefix=''):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        params.add(key)
                        if isinstance(value, (dict, list)):
                            extract_keys(value, prefix + key + '.')
                elif isinstance(obj, list) and obj:
                    extract_keys(obj[0], prefix)
            
            extract_keys(data)
        except Exception:
            pass
        
        return params
    
    def get_common_params(self) -> Set[str]:
        """Return set of common parameter names"""
        return self.common_params.copy()
