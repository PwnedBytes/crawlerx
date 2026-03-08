# CrawlerX

<div align="center">

**High-Performance Terminal-Based Web Crawler**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Asyncio](https://img.shields.io/badge/asyncio-supported-brightgreen.svg)](https://docs.python.org/3/library/asyncio.html)

*Developed by Pwned Bytes*

</div>

---

## Overview

CrawlerX is a high-performance, asynchronous web crawler designed specifically for security reconnaissance, bug bounty hunting, and attack surface discovery. Built with Python's asyncio and aiohttp, it delivers exceptional speed while maintaining a lightweight footprint optimized for resource-constrained environments.

### Key Features

- **Asynchronous Architecture**: Built on asyncio and aiohttp for maximum concurrency
- **Deep Recursive Crawling**: Configurable depth with intelligent duplicate detection
- **JavaScript Analysis**: Extracts API endpoints from JS files using pattern matching
- **Smart Scope Control**: Subdomain inclusion, external link handling
- **Parameter Discovery**: Extracts URL parameters, form inputs, and API keys
- **Directory Enumeration**: Generates comprehensive wordlists from discovered paths
- **Live Terminal Interface**: Real-time statistics with color-coded output
- **Pause/Resume**: Save and resume crawling state across sessions
- **Proxy Support**: Full support for HTTP/HTTPS proxies (Burp Suite, etc.)
- **Rate Limiting**: Configurable requests per second to avoid blocking
- **Multiple Output Formats**: JSON results, wordlists, and structured reports

---

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/pwnedbytes/crawlerx.git
cd crawlerx

# Install dependencies
pip install -r requirements.txt

# Make executable (optional)
chmod +x crawlerx.py

# Or install as system package
pip install -e .
```

Dependencies

Package	Version	Purpose	
aiohttp	=3.8.0	Async HTTP client/server	
aiofiles	=0.8.0	Async file operations	
beautifulsoup4	=4.11.0	HTML parsing	
lxml	=4.9.0	XML/HTML parser backend	
colorama	=0.4.4	Cross-platform colored terminal	
tqdm	=4.64.0	Progress bars (optional)	

---

Usage

Basic Usage

Single Target

```bash
python crawlerx.py -u https://example.com
```

Multiple Targets

```bash
python crawlerx.py -l domains.txt
```

Resume Interrupted Scan

```bash
python crawlerx.py --resume example.com
```

Advanced Examples

Deep Crawl with High Concurrency

```bash
python crawlerx.py -u https://example.com \
    --depth 5 \
    --workers 20 \
    --rate 15
```

Bug Bounty Mode with Proxy

```bash
python crawlerx.py -u https://target.com \
    --depth 4 \
    --workers 10 \
    --proxy http://127.0.0.1:8080 \
    -H "X-BugBounty: HackerOne" \
    -H "Authorization: Bearer token123" \
    --include-subdomains
```

Stealth Mode

```bash
python crawlerx.py -u https://example.com \
    --rate 2 \
    --workers 3 \
    --timeout 15 \
    -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
```

---

Command Line Options

Input Options

Flag	Description	Example	
`-u, --url`	Single target URL	`-u https://example.com`	
`-l, --list`	File containing URLs (one per line)	`-l targets.txt`	
`--resume`	Resume previous scan by domain	`--resume example.com`	

Performance Options

Flag	Default	Description	
`-w, --workers`	10	Number of concurrent async workers	
`-r, --rate`	10	Maximum requests per second	
`-d, --depth`	3	Maximum crawl depth (0 = unlimited)	
`--timeout`	10	Request timeout in seconds	

Scope Control

Flag	Description	
`--include-subdomains`	Include subdomains in crawl scope (e.g., api.example.com)	
`--crawl-external`	Follow and crawl external links	
`--no-verify-ssl`	Disable SSL certificate verification	

Network Options

Flag	Description	Example	
`--proxy`	Proxy URL for all requests	`--proxy http://127.0.0.1:8080`	
`-H, --header`	Custom HTTP header (repeatable)	`-H "X-Custom: value"`	

Output Options

Flag	Description	
`-v, --verbose`	Enable verbose debug output	
`-q, --quiet`	Suppress banner and live interface	

---

Architecture

Module Structure

```
crawlerx/
├── crawlerx.py              # Main entry point
├── config.py                # Global configuration
├── core/                    # Core crawling engine
│   ├── crawler.py           # Main orchestrator
│   ├── queue_manager.py     # Async URL queue with deduplication
│   ├── fetcher.py           # HTTP fetcher with aiohttp
│   └── parser.py            # HTML content parser
├── modules/                 # Feature modules
│   ├── js_extractor.py      # JavaScript endpoint discovery
│   ├── robots_parser.py     # robots.txt parsing
│   ├── sitemap_parser.py    # XML sitemap handling
│   ├── wildcard_detector.py # Wildcard domain detection
│   ├── param_extractor.py   # Parameter extraction
│   └── dir_extractor.py     # Directory extraction
├── storage/                 # Data persistence
│   ├── json_writer.py       # Async JSON output
│   ├── wordlist_manager.py  # Wordlist generation
│   └── state_manager.py     # Pause/resume state
├── utils/                   # Utilities
│   ├── url_utils.py         # URL normalization
│   ├── validators.py        # Input validation
│   ├── headers.py           # Header management
│   ├── rate_limiter.py      # Token bucket rate limiting
│   ├── proxy_handler.py     # Proxy configuration
│   └── logger.py            # Logging utilities
└── cli/                     # Command line interface
    ├── main.py              # Argument parsing
    ├── banner.py            # Terminal banner
    └── interface.py         # Live statistics display
```

Workflow

1. Initialization: Parse arguments, validate inputs, setup directories
2. Pre-flight: Fetch robots.txt, sitemap.xml for initial URLs
3. Seed Queue: Add target URL to async queue
4. Worker Pool: Spawn async workers to process queue
5. Fetch & Parse: Download content, extract links, parameters, directories
6. JavaScript Analysis: Download and analyze JS files for endpoints
7. Deduplication: Normalize URLs, prevent duplicate processing
8. Storage: Save results to JSON, generate wordlists
9. State Management: Periodic saves for pause/resume capability

---

Output Structure

```
targets/
└── example.com/
    ├── results.json              # Complete crawl results
    ├── directories.txt           # Discovered directory paths
    ├── parameters.txt            # Discovered parameter names
    ├── js_endpoints.txt          # JavaScript API endpoints
    ├── crawl_state.json          # Pause/resume state
    └── crawl.log                 # Activity log
```

results.json Format

```json
{
  "crawler": "CrawlerX",
  "version": "1.0",
  "start_time": "2024-01-15T10:30:00",
  "last_updated": "2024-01-15T10:35:22",
  "results": [
    {
      "url": "https://example.com/page",
      "title": "Page Title",
      "status": 200,
      "content_type": "text/html",
      "length": 4523,
      "depth": 2,
      "redirect": null
    }
  ],
  "metadata": {
    "total_urls": 150,
    "directories": 45,
    "parameters": 23
  }
}
```

---

Crawling Logic

URL Normalization

CrawlerX normalizes URLs to prevent duplicate crawling:

Original	Normalized	
`https://example.com/page`	`https://example.com/page`	
`https://example.com/page/`	`https://example.com/page`	
`https://example.com/page#section`	`https://example.com/page`	
`https://example.com/page?utm_source=ads`	`https://example.com/page`	
`//example.com/page`	`https://example.com/page`	

Link Extraction

Extracts links from HTML elements:

- `<a href="">` - Standard links
- `<script src="">` - JavaScript files
- `<img src="">` - Images (filtered by extension)
- `<iframe src="">` - Iframes
- `<link href="">` - Stylesheets, icons
- `<form action="">` - Form submissions
- `<meta http-equiv="refresh">` - Meta redirects

JavaScript Endpoint Detection

Pattern-based extraction from JS files:

- `fetch("/api/data")`
- `axios.get("/v1/users")`
- `XMLHttpRequest("/auth/login")`
- `url: "/internal/api"`
- `path: "/admin/dashboard"`

Ignored File Extensions

```
Images: jpg, jpeg, png, gif, svg, ico, bmp, webp
Fonts: woff, woff2, ttf, otf, eot
Media: mp4, webm, avi, mov, mp3, wav
Docs: pdf, doc, docx, xls, xlsx, ppt
Archives: zip, rar, 7z, tar, gz
Styles: css, scss, less
Binaries: exe, dll, dmg
```

---

Performance Tuning

Worker Count

Recommended workers based on environment:

Environment	Workers	Description	
Mobile/Termux	5-10	Limited CPU/memory	
Desktop	20-50	Standard development	
Server	50-100	High-performance VPS	

Rate Limiting

Adjust based on target:

Scenario	Rate	Use Case	
Stealth	1-5	Avoiding detection, WAF evasion	
Normal	10-20	Standard reconnaissance	
Aggressive	50-100	Internal testing, time-sensitive	

Memory Usage

Memory usage scales with:
- Queue size (pending URLs)
- Seen URL set (deduplication)
- Response cache (disabled by default)

Typical usage: 50-100MB per 10,000 URLs crawled.

---

Security Considerations

Responsible Disclosure

- Always have permission before crawling
- Respect robots.txt Disallow directives
- Follow responsible disclosure for findings
- Do not crawl production systems without authorization

Rate Limiting

Built-in rate limiting prevents overwhelming targets. Default 10 req/s is conservative.

Scope Control

- `--include-subdomains`: Only crawl subdomains of target
- `--crawl-external`: Disabled by default, prevents crawling external sites
- URL normalization prevents duplicate requests

---

Troubleshooting

Common Issues

SSL Certificate Errors

```bash
# Disable SSL verification
python crawlerx.py -u https://example.com --no-verify-ssl
```

Too Many Open Files

```bash
# Increase ulimit
ulimit -n 4096
```

Memory Issues

```bash
# Reduce workers and depth
python crawlerx.py -u https://example.com --workers 5 --depth 2
```

Connection Timeouts

```bash
# Increase timeout
python crawlerx.py -u https://example.com --timeout 30
```

Debug Mode

Enable verbose logging:

```bash
python crawlerx.py -u https://example.com -v
```

---

Development

Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with coverage
pytest --cov=crawlerx tests/
```

Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Async/await for all I/O operations

---

Comparison with Other Tools

Feature	CrawlerX	Katana	hakrawler	Photon	
Language	Python	Go	Go	Python	
Async	Yes	Yes	Yes	No	
JS Parsing	Yes	Yes	Limited	Yes	
Live Interface	Yes	No	No	No	
Pause/Resume	Yes	No	No	No	
Wordlists	Yes	Limited	No	Limited	
Mobile Friendly	Yes	Binary	Binary	Heavy	

---

License

MIT License

Copyright (c) 2024 Pwned Bytes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

Acknowledgments

- Inspired by [Katana](https://github.com/projectdiscovery/katana) and [hakrawler](https://github.com/hakluke/hakrawler)
- Built with [aiohttp](https://docs.aiohttp.org/) and [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- Terminal colors by [colorama](https://github.com/tartley/colorama)

---

Contact

- Author: Pwned Bytes
- GitHub: https://github.com/pwnedbytes/crawlerx
- Issues: https://github.com/pwnedbytes/crawlerx/issues

---

Happy Hunting! 🕷️