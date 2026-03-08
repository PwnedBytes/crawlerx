# config.py
"""
CrawlerX Global Configuration
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
TARGETS_DIR = BASE_DIR / "targets"
WORDLISTS_DIR = BASE_DIR / "wordlists"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for dir_path in [TARGETS_DIR, WORDLISTS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Default crawling settings
DEFAULT_CONFIG = {
    'workers': 10,
    'rate': 10,
    'depth': 3,
    'timeout': 10,
    'include_subdomains': False,
    'crawl_external': False,
    'follow_redirects': True,
    'max_redirects': 5,
    'verify_ssl': False,
    'user_agent': 'CrawlerX/1.0 (Security Research Tool)',
}

# Ignored file extensions
IGNORED_EXTENSIONS = {
    'jpg', 'jpeg', 'png', 'gif', 'svg', 'ico', 'bmp', 'webp',
    'css', 'scss', 'less',
    'woff', 'woff2', 'ttf', 'otf', 'eot',
    'mp4', 'webm', 'avi', 'mov', 'mkv',
    'mp3', 'wav', 'ogg',
    'zip', 'rar', '7z', 'tar', 'gz',
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'exe', 'dll', 'bin', 'dmg', 'pkg',
}

# Interesting paths for hidden endpoint detection
INTERESTING_PATHS = [
    'admin', 'api', 'backup', 'config', 'debug', 'dev', 'internal',
    'test', 'staging', 'prod', 'production', 'beta', 'alpha',
    'graphql', 'graphiql', 'playground', 'swagger', 'api-docs',
    'wp-admin', 'wp-content', 'wp-includes',
    '.git', '.env', '.config', '.ssh', '.aws',
    'phpmyadmin', 'adminer', 'mysql', 'db', 'database',
    'jenkins', 'grafana', 'kibana', 'elasticsearch',
    'actuator', 'health', 'metrics', 'info', 'trace',
    'api/v1', 'api/v2', 'api/v3', 'rest', 'soap',
    'uploads', 'files', 'assets', 'static', 'media',
    'login', 'register', 'signup', 'auth', 'oauth', 'sso',
    'dashboard', 'panel', 'console', 'manage', 'management',
    'robots.txt', 'sitemap.xml', 'crossdomain.xml',
]

# JavaScript endpoint patterns
JS_PATTERNS = [
    r'["\']((?:/|\\./|\\../)[a-zA-Z0-9_\-/]+(?:/[a-zA-Z0-9_\-]+)*)\s*["\']',
    r'fetch\(["\']([^"\']+)["\']',
    r'axios\.(?:get|post|put|delete|patch)\(["\']([^"\']+)["\']',
    r'XMLHttpRequest\(["\']([^"\']+)["\']',
    r'url:\s*["\']([^"\']+)["\']',
    r'path:\s*["\']([^"\']+)["\']',
    r'endpoint:\s*["\']([^"\']+)["\']',
    r'route:\s*["\']([^"\']+)["\']',
    r'action:\s*["\']([^"\']+)["\']',
    r'href:\s*["\']([^"\']+)["\']',
    r'src:\s*["\']([^"\']+)["\']',
]

# HTML elements to extract links from
LINK_ELEMENTS = {
    'a': 'href',
    'script': 'src',
    'img': 'src',
    'iframe': 'src',
    'frame': 'src',
    'link': 'href',
    'object': 'data',
    'embed': 'src',
    'form': 'action',
    'input': 'src',
    'source': 'src',
    'video': 'src',
    'audio': 'src',
    'track': 'src',
    'area': 'href',
    'base': 'href',
}

# State file name
STATE_FILE = "crawl_state.json"
RESULTS_FILE = "results.json"
