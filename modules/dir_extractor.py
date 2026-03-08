# modules/dir_extractor.py
"""
Directory Extractor
"""

import re
from typing import Set
from urllib.parse import urlparse

class DirExtractor:
    """Extract directory paths from URLs"""
    
    def __init__(self):
        self.common_dirs = {
            'admin', 'api', 'assets', 'css', 'js', 'images', 'img',
            'uploads', 'files', 'downloads', 'media', 'static',
            'includes', 'inc', 'lib', 'vendor', 'node_modules',
            'test', 'tests', 'dev', 'development', 'staging', 'prod',
            'backup', 'old', 'new', 'v1', 'v2', 'v3', 'version',
            'user', 'users', 'account', 'accounts', 'profile',
            'dashboard', 'panel', 'manage', 'management', 'control',
            'config', 'configuration', 'settings', 'setup', 'install',
            'logs', 'tmp', 'temp', 'cache', 'data', 'database', 'db',
            'private', 'protected', 'secret', 'hidden', 'internal',
        }
    
    def extract(self, url: str) -> Set[str]:
        """Extract all directory paths from URL"""
        directories = set()
        
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            if not path or path == '/':
                return directories
            
            # Split path
            parts = path.strip('/').split('/')
            current = ''
            
            for i, part in enumerate(parts[:-1]):  # Exclude last part (file or leaf)
                if part and '.' not in part:  # Skip if looks like file
                    current += '/' + part + '/'
                    directories.add(current)
                    
        except Exception:
            pass
        
        return directories
    
    def extract_from_text(self, text: str, base_url: str) -> Set[str]:
        """Extract directory-like patterns from text"""
        directories = set()
        
        # Look for path patterns
        pattern = r'["\'](/[a-zA-Z0-9_\-/]+/)["\']'
        matches = re.findall(pattern, text)
        
        for match in matches:
            if match.count('/') >= 2:  # At least one directory level
                directories.add(match)
        
        return directories
    
    def get_common_directories(self) -> Set[str]:
        """Return set of common directory names"""
        return self.common_dirs.copy()
