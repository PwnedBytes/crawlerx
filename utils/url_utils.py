# utils/url_utils.py
"""
URL Utilities for normalization and parsing
"""

import re
from urllib.parse import urlparse, urljoin, urldefrag, parse_qs, urlencode, urlunparse
from typing import Set, Optional

class URLUtils:
    """Utility class for URL operations"""
    
    # Tracking parameters to remove
    TRACKING_PARAMS = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'utm_id', 'utm_source_platform', 'utm_creative_format', 'utm_marketing_tactic',
        'fbclid', 'gclid', 'ttclid', 'twclid', 'li_fat_id',
        'wickedid', 'yclid', 'msclkid', 'dclid', 'zanpid',
        'utm_reader', 'utm_place', 'utm_user', 'utm_trans',
        'ref', 'referrer', 'referral', 'source', 'medium',
    }
    
    @staticmethod
    def normalize(url: str, base_url: str = None) -> Optional[str]:
        """
        Normalize URL to prevent duplicates
        """
        if not url:
            return None
            
        # Handle relative URLs
        if base_url and not url.startswith(('http://', 'https://', '//')):
            url = urljoin(base_url, url)
        elif url.startswith('//'):
            url = 'https:' + url
            
        if not url.startswith(('http://', 'https://')):
            return None
            
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Remove fragment
            parsed = parsed._replace(fragment='')
            
            # Normalize path
            path = parsed.path
            path = re.sub(r'/+', '/', path)  # Remove duplicate slashes
            path = path.rstrip('/') or '/'   # Ensure leading slash, remove trailing
            
            # Normalize query parameters
            query = parsed.query
            if query:
                params = parse_qs(query, keep_blank_values=True)
                # Remove tracking parameters
                for param in list(params.keys()):
                    if param.lower() in URLUtils.TRACKING_PARAMS:
                        del params[param]
                
                # Sort parameters for consistency
                query = urlencode(sorted(params.items()), doseq=True)
            else:
                query = ''
                
            # Reconstruct URL
            normalized = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                path,
                parsed.params,
                query,
                ''  # No fragment
            ))
            
            return normalized
            
        except Exception:
            return None
    
    @staticmethod
    def get_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return ''
    
    @staticmethod
    def is_same_domain(url1: str, url2: str, include_subdomains: bool = False) -> bool:
        """Check if two URLs belong to same domain"""
        domain1 = URLUtils.get_domain(url1)
        domain2 = URLUtils.get_domain(url2)
        
        if include_subdomains:
            # Remove www. and check if one ends with other
            d1 = domain1.replace('www.', '')
            d2 = domain2.replace('www.', '')
            return d1 == d2 or d1.endswith('.' + d2) or d2.endswith('.' + d1)
        
        return domain1 == domain2
    
    @staticmethod
    def is_in_scope(url: str, target_domain: str, include_subdomains: bool = False) -> bool:
        """Check if URL is within crawl scope"""
        url_domain = URLUtils.get_domain(url)
        target_domain = target_domain.lower().replace('www.', '')
        
        if url_domain == target_domain or url_domain == 'www.' + target_domain:
            return True
            
        if include_subdomains and url_domain.endswith('.' + target_domain):
            return True
            
        return False
    
    @staticmethod
    def extract_directories(url: str) -> Set[str]:
        """Extract directory paths from URL"""
        directories = set()
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            parts = path.strip('/').split('/')
            current_path = ''
            
            for part in parts[:-1]:  # Exclude filename/last part
                if part and '.' not in part:  # Skip if looks like file
                    current_path += '/' + part + '/'
                    directories.add(current_path)
                    
        except Exception:
            pass
            
        return directories
    
    @staticmethod
    def get_file_extension(url: str) -> str:
        """Get file extension from URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path
            if '.' in path:
                return path.split('.')[-1].lower().split('?')[0]
        except Exception:
            pass
        return ''
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Basic URL validation"""
        if not url or not isinstance(url, str):
            return False
        return url.startswith(('http://', 'https://'))
    
    @staticmethod
    def extract_parameters(url: str) -> Set[str]:
        """Extract parameter names from URL"""
        params = set()
        try:
            parsed = urlparse(url)
            if parsed.query:
                query_params = parse_qs(parsed.query)
                params.update(query_params.keys())
        except Exception:
            pass
        return params
