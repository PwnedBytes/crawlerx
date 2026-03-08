# utils/validators.py
"""
Input validation utilities
"""

import re
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional, List

class Validators:
    """Input validation class"""
    
    @staticmethod
    def validate_url(url: str) -> tuple[bool, str]:
        """
        Validate single URL
        Returns: (is_valid, error_message)
        """
        if not url:
            return False, "URL is empty"
            
        if not url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
            
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False, "URL has no domain"
                
            # Basic domain validation
            domain_pattern = r'^[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+$'
            if not re.match(domain_pattern, parsed.netloc.replace('www.', '')):
                return False, "Invalid domain format"
                
            return True, ""
            
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"
    
    @staticmethod
    def validate_domain_list(file_path: str) -> tuple[bool, List[str], str]:
        """
        Validate domain list file
        Returns: (is_valid, domains, error_message)
        """
        path = Path(file_path)
        
        if not path.exists():
            return False, [], f"File not found: {file_path}"
            
        if not path.is_file():
            return False, [], f"Not a file: {file_path}"
            
        try:
            with open(path, 'r') as f:
                lines = f.readlines()
                
            domains = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Add protocol if missing
                if not line.startswith(('http://', 'https://')):
                    line = 'https://' + line
                    
                is_valid, error = Validators.validate_url(line)
                if is_valid:
                    domains.append(line)
                else:
                    return False, [], f"Invalid URL at line {line_num}: {error}"
                    
            if not domains:
                return False, [], "No valid domains found in file"
                
            return True, domains, ""
            
        except Exception as e:
            return False, [], f"Error reading file: {str(e)}"
    
    @staticmethod
    def validate_workers(workers: int) -> tuple[bool, int, str]:
        """Validate worker count"""
        if not isinstance(workers, int):
            try:
                workers = int(workers)
            except ValueError:
                return False, 0, "Workers must be an integer"
                
        if workers < 1:
            return False, 0, "Workers must be at least 1"
        if workers > 100:
            return False, 0, "Workers cannot exceed 100"
            
        return True, workers, ""
    
    @staticmethod
    def validate_rate(rate: int) -> tuple[bool, int, str]:
        """Validate rate limit"""
        if not isinstance(rate, int):
            try:
                rate = int(rate)
            except ValueError:
                return False, 0, "Rate must be an integer"
                
        if rate < 1:
            return False, 0, "Rate must be at least 1"
        if rate > 1000:
            return False, 0, "Rate cannot exceed 1000"
            
        return True, rate, ""
    
    @staticmethod
    def validate_depth(depth: int) -> tuple[bool, int, str]:
        """Validate crawl depth"""
        if not isinstance(depth, int):
            try:
                depth = int(depth)
            except ValueError:
                return False, 0, "Depth must be an integer"
                
        if depth < 0:
            return False, 0, "Depth cannot be negative"
        if depth > 20:
            return False, 0, "Depth cannot exceed 20"
            
        return True, depth, ""
    
    @staticmethod
    def validate_proxy(proxy: str) -> tuple[bool, str]:
        """Validate proxy URL"""
        if not proxy:
            return True, ""  # Empty is valid (no proxy)
            
        proxy_pattern = r'^(http|https|socks4|socks5)://[^:]+:\d+$'
        if not re.match(proxy_pattern, proxy):
            return False, "Proxy format: protocol://host:port"
            
        return True, ""
