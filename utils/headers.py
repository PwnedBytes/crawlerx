# utils/headers.py
"""
Header management for HTTP requests
"""

from typing import Dict, Optional, List

class HeaderManager:
    """Manages HTTP headers for requests"""
    
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    def __init__(self, user_agent: Optional[str] = None, custom_headers: Optional[List[str]] = None):
        self.headers = self.DEFAULT_HEADERS.copy()
        
        # Set User-Agent
        if user_agent:
            self.headers['User-Agent'] = user_agent
        else:
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        
        # Parse custom headers
        if custom_headers:
            for header in custom_headers:
                self.add_header(header)
    
    def add_header(self, header_string: str):
        """
        Add custom header from string format "Name: Value"
        """
        if ':' not in header_string:
            return
            
        name, value = header_string.split(':', 1)
        name = name.strip()
        value = value.strip()
        
        if name and value:
            self.headers[name] = value
    
    def get_headers(self) -> Dict[str, str]:
        """Get all headers"""
        return self.headers.copy()
    
    def update_header(self, name: str, value: str):
        """Update specific header"""
        self.headers[name] = value
    
    def remove_header(self, name: str):
        """Remove specific header"""
        self.headers.pop(name, None)
