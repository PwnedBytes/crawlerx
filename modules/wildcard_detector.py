# modules/wildcard_detector.py
"""
Wildcard Domain Detector
"""

import re
from typing import Set, Optional, List

from utils.logger import Logger

class WildcardDetector:
    """Detect and handle wildcard domains"""
    
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger
        self.wildcards: Set[str] = set()
    
    def check_domain(self, domain: str) -> bool:
        """
        Check if domain has wildcard DNS enabled
        Returns True if wildcard detected
        """
        # This is a placeholder - actual implementation would require
        # DNS resolution checks which are complex in pure Python
        
        # For now, check common wildcard indicators
        wildcard_indicators = ['*.', 'wildcard']
        
        for indicator in wildcard_indicators:
            if indicator in domain:
                return True
        
        return False
    
    def extract_subdomains(self, urls: List[str]) -> Set[str]:
        """Extract unique subdomains from URL list"""
        subdomains = set()
        
        for url in urls:
            match = re.search(r'https?://([^/]+)', url)
            if match:
                domain = match.group(1)
                if domain:
                    subdomains.add(domain)
        
        return subdomains
    
    def prompt_user(self, wildcards: Set[str]) -> bool:
        """
        Prompt user for wildcard scanning permission
        Returns True if user approves
        """
        if not wildcards:
            return False
        
        print(f"\n[!] Wildcard domains detected: {', '.join(wildcards)}")
        
        while True:
            response = input("Scan them? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def generate_subdomain_list(self, base_domain: str, wordlist: List[str]) -> List[str]:
        """Generate potential subdomains to test"""
        subdomains = []
        
        for word in wordlist:
            subdomain = f"{word}.{base_domain}"
            subdomains.append(subdomain)
        
        return subdomains
