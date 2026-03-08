# utils/proxy_handler.py
"""
Proxy configuration handler
"""

from typing import Optional, Dict

class ProxyHandler:
    """Handle proxy configurations"""
    
    def __init__(self, proxy_url: Optional[str] = None):
        self.proxy_url = proxy_url
        self.proxies = self._parse_proxy(proxy_url) if proxy_url else None
    
    def _parse_proxy(self, proxy_url: str) -> Dict[str, str]:
        """Parse proxy URL into aiohttp format"""
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_aiohttp_proxy(self) -> Optional[str]:
        """Get proxy string for aiohttp"""
        return self.proxy_url
    
    def get_requests_proxy(self) -> Optional[Dict[str, str]]:
        """Get proxy dict for requests"""
        return self.proxies
    
    def is_configured(self) -> bool:
        """Check if proxy is configured"""
        return self.proxy_url is not None
