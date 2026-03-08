# modules/robots_parser.py
"""
robots.txt Parser
"""

import re
from typing import Set, List, Optional
from urllib.parse import urljoin

from utils.logger import Logger

class RobotsParser:
    """Parse robots.txt files"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger
    
    def parse(self, content: str) -> Set[str]:
        """
        Parse robots.txt content and extract disallowed paths
        """
        disallowed = set()
        sitemaps = []
        
        lines = content.split('\n')
        user_agent_relevant = False
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            if ':' not in line:
                continue
            
            directive, value = line.split(':', 1)
            directive = directive.strip().lower()
            value = value.strip()
            
            if directive == 'user-agent':
                # Check if this applies to us or all
                if value == '*' or 'crawler' in value.lower() or 'bot' in value.lower():
                    user_agent_relevant = True
                else:
                    user_agent_relevant = False
            
            elif user_agent_relevant:
                if directive == 'disallow' and value:
                    disallowed.add(value)
                elif directive == 'allow' and value:
                    # Track allowed paths that override disallow
                    pass
            
            # Sitemaps apply to all
            if directive == 'sitemap' and value:
                sitemaps.append(value)
        
        if self.logger and sitemaps:
            self.logger.debug(f"Found sitemaps: {sitemaps}")
        
        return disallowed
    
    def parse_sitemaps(self, content: str) -> List[str]:
        """Extract sitemap URLs from robots.txt"""
        sitemaps = []
        
        for line in content.split('\n'):
            if line.lower().startswith('sitemap:'):
                url = line.split(':', 1)[1].strip()
                if url:
                    sitemaps.append(url)
        
        return sitemaps
