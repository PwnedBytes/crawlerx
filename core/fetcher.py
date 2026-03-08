# core/fetcher.py
"""
Async HTTP Fetcher
"""

import asyncio
import aiohttp
import ssl
from typing import Optional, Dict, Tuple, Any
from aiohttp import ClientTimeout, TCPConnector

from utils.headers import HeaderManager
from utils.rate_limiter import RateLimiter
from utils.proxy_handler import ProxyHandler
from utils.logger import Logger

class Fetcher:
    """Async HTTP fetcher with rate limiting and proxy support"""
    
    def __init__(self, headers: HeaderManager, rate_limiter: RateLimiter,
                 proxy_handler: Optional[ProxyHandler] = None,
                 timeout: int = 10, max_redirects: int = 5,
                 verify_ssl: bool = False, logger: Optional[Logger] = None):
        self.headers = headers
        self.rate_limiter = rate_limiter
        self.proxy_handler = proxy_handler
        self.timeout = ClientTimeout(total=timeout, connect=5, sock_read=timeout)
        self.max_redirects = max_redirects
        self.verify_ssl = verify_ssl
        self.logger = logger or Logger()
        
        # SSL context
        self.ssl_context = ssl.create_default_context()
        if not verify_ssl:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Session will be created in async context
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Create aiohttp session"""
        self.logger.debug("[FETCHER] Initializing HTTP session...")
        
        connector = TCPConnector(
            limit=50,
            limit_per_host=5,
            enable_cleanup_closed=True,
            force_close=True,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.headers.get_headers(),
        )
        
        self.logger.debug(f"[FETCHER] Session created with timeout={self.timeout.total}s")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session"""
        self.logger.debug("[FETCHER] Closing HTTP session...")
        if self.session:
            await self.session.close()
            self.logger.debug("[FETCHER] Session closed")
    
    async def fetch(self, url: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Fetch URL content
        Returns: (response_data, error_message)
        """
        self.logger.debug(f"[FETCH] Acquiring rate limit for {url}")
        await self.rate_limiter.acquire()
        
        try:
            proxy = self.proxy_handler.get_aiohttp_proxy() if self.proxy_handler else None
            self.logger.debug(f"[FETCH] Requesting: {url} (proxy={proxy})")
            
            start_time = asyncio.get_event_loop().time()
            
            async with self.session.get(
                url, 
                proxy=proxy,
                ssl=self.ssl_context if not self.verify_ssl else None,
                allow_redirects=True,
                max_redirects=self.max_redirects,
                timeout=self.timeout
            ) as response:
                
                elapsed = asyncio.get_event_loop().time() - start_time
                content_type = response.headers.get('Content-Type', '')
                
                self.logger.debug(f"[FETCH] Response: {url} -> Status {response.status} in {elapsed:.2f}s")
                self.logger.debug(f"[FETCH] Content-Type: {content_type}")
                self.logger.debug(f"[FETCH] Content-Length: {response.headers.get('Content-Length', 'unknown')}")
                
                # Read content based on type
                if 'text' in content_type or 'json' in content_type or 'xml' in content_type:
                    try:
                        text = await response.text()
                        self.logger.debug(f"[FETCH] Downloaded {len(text)} bytes of text content")
                    except Exception as e:
                        self.logger.debug(f"[FETCH] Error reading text: {e}")
                        text = ''
                else:
                    self.logger.debug(f"[FETCH] Skipping content read for binary type: {content_type}")
                    text = ''
                
                result = {
                    'url': str(response.url),
                    'status': response.status,
                    'headers': dict(response.headers),
                    'content_type': content_type,
                    'text': text,
                    'length': len(text),
                    'redirected': response.history,
                    'final_url': str(response.url)
                }
                
                if response.history:
                    self.logger.debug(f"[FETCH] Redirect chain: {' -> '.join([str(r.url) for r in response.history])} -> {response.url}")
                
                return result, None
                
        except asyncio.TimeoutError:
            self.logger.debug(f"[FETCH] TIMEOUT: {url} after {self.timeout.total}s")
            return None, "Timeout"
        except aiohttp.ClientError as e:
            self.logger.debug(f"[FETCH] ClientError: {url} -> {type(e).__name__}: {e}")
            return None, f"Client error: {str(e)}"
        except Exception as e:
            self.logger.debug(f"[FETCH] Exception: {url} -> {type(e).__name__}: {e}")
            return None, f"Error: {str(e)}"
    
    async def fetch_js(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch JavaScript file content
        Returns: (content, error_message)
        """
        self.logger.debug(f"[FETCH_JS] Acquiring rate limit for {url}")
        await self.rate_limiter.acquire()
        
        try:
            proxy = self.proxy_handler.get_aiohttp_proxy() if self.proxy_handler else None
            self.logger.debug(f"[FETCH_JS] Downloading JS: {url}")
            
            async with self.session.get(
                url,
                proxy=proxy,
                ssl=self.ssl_context if not self.verify_ssl else None,
                max_redirects=self.max_redirects,
                timeout=self.timeout
            ) as response:
                
                self.logger.debug(f"[FETCH_JS] Response: {url} -> Status {response.status}")
                
                if response.status == 200:
                    content = await response.text()
                    self.logger.debug(f"[FETCH_JS] Downloaded {len(content)} bytes of JavaScript")
                    return content, None
                else:
                    self.logger.debug(f"[FETCH_JS] Non-200 status: {response.status}")
                    return None, f"HTTP {response.status}"
                    
        except Exception as e:
            self.logger.debug(f"[FETCH_JS] Exception: {url} -> {type(e).__name__}: {e}")
            return None, str(e)
