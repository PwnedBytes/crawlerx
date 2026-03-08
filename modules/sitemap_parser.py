# modules/sitemap_parser.py
"""
Sitemap XML Parser
"""

import xml.etree.ElementTree as ET
import re
from typing import Set, List, Optional
from urllib.parse import urljoin

from utils.logger import Logger

class SitemapParser:
    """Parse XML sitemaps"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger
    
    def parse(self, content: str) -> Set[str]:
        """
        Parse sitemap XML and extract URLs
        """
        urls = set()
        
        try:
            # Try XML parsing
            root = ET.fromstring(content)
            
            # Handle sitemap index
            if 'sitemapindex' in root.tag:
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    if sitemap.text:
                        urls.add(sitemap.text)
            
            # Handle urlset
            elif 'urlset' in root.tag:
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    if url.text:
                        urls.add(url.text)
            
            # Fallback for malformed XML
            else:
                urls.update(self._regex_parse(content))
                
        except ET.ParseError:
            # Try regex fallback
            urls.update(self._regex_parse(content))
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Sitemap parse error: {e}")
        
        return urls
    
    def _regex_parse(self, content: str) -> Set[str]:
        """Fallback regex parsing"""
        urls = set()
        
        # Find all <loc> tags
        pattern = r'<loc>([^<]+)</loc>'
        matches = re.findall(pattern, content)
        
        for match in matches:
            url = match.strip()
            if url.startswith(('http://', 'https://')):
                urls.add(url)
        
        return urls
    
    def parse_text_sitemap(self, content: str) -> Set[str]:
        """Parse plain text sitemap"""
        urls = set()
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith(('http://', 'https://')):
                urls.add(line)
        
        return urls
