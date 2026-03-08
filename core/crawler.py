# core/crawler.py
"""
Main Crawler Orchestrator
"""

import asyncio
import json
import signal
import sys
from pathlib import Path
from typing import Set, Dict, List, Optional
from datetime import datetime
from urllib.parse import urlparse

from config import DEFAULT_CONFIG, IGNORED_EXTENSIONS, TARGETS_DIR, STATE_FILE, RESULTS_FILE
from utils.url_utils import URLUtils
from utils.logger import Logger
from utils.headers import HeaderManager
from utils.rate_limiter import RateLimiter
from utils.proxy_handler import ProxyHandler
from utils.validators import Validators
from core.queue_manager import QueueManager
from core.fetcher import Fetcher
from core.parser import Parser
from storage.json_writer import JSONWriter
from storage.wordlist_manager import WordlistManager
from storage.state_manager import StateManager
from modules.js_extractor import JSExtractor
from modules.robots_parser import RobotsParser
from modules.sitemap_parser import SitemapParser
from modules.wildcard_detector import WildcardDetector

class Crawler:
    """Main crawler class"""
    
    def __init__(self, target: str, **kwargs):
        self.target = target
        self.target_domain = URLUtils.get_domain(target)
        self.config = {**DEFAULT_CONFIG, **kwargs}
        
        # Setup directories
        self.output_dir = TARGETS_DIR / self.target_domain
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.logger = Logger(
            log_file=self.output_dir / "crawl.log",
            verbose=self.config.get('verbose', False),
            quiet=self.config.get('quiet', False)
        )
        
        self.queue = QueueManager(logger=self.logger if self.config.get('verbose') else None)
        self.header_manager = HeaderManager(
            user_agent=self.config.get('user_agent'),
            custom_headers=self.config.get('headers', [])
        )
        self.rate_limiter = RateLimiter(self.config['rate'])
        self.proxy_handler = ProxyHandler(self.config.get('proxy'))
        
        # Storage
        self.json_writer = JSONWriter(self.output_dir / RESULTS_FILE)
        self.wordlist_manager = WordlistManager(self.output_dir)
        self.state_manager = StateManager(self.output_dir / STATE_FILE)
        
        # Modules
        self.js_extractor = JSExtractor(self.target_domain, self.logger)
        self.robots_parser = RobotsParser(self.logger)
        self.sitemap_parser = SitemapParser(self.logger)
        self.wildcard_detector = WildcardDetector(self.logger)
        
        # Data storage
        self.discovered_urls: Set[str] = set()
        self.directories: Set[str] = set()
        self.parameters: Set[str] = set()
        self.js_endpoints: Set[str] = set()
        self.errors: List[Dict] = []
        
        # Stats
        self.start_time = None
        self.stats = {
            'urls_crawled': 0,
            'urls_discovered': 0,
            'directories': 0,
            'parameters': 0,
            'js_endpoints': 0,
            'errors': 0,
        }
        
        # Control flags
        self.running = False
        self.paused = False
        self.interrupted = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.debug(f"[INIT] Crawler initialized for {target}")
        self.logger.debug(f"[INIT] Config: {self.config}")
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.logger.warning("\n[!] Interrupt received, saving state...")
        self.interrupted = True
        self.running = False
    
    def _should_crawl(self, url: str, depth: int) -> bool:
        """Check if URL should be crawled"""
        # Check depth
        if depth > self.config['depth']:
            self.logger.debug(f"[FILTER] Rejected (depth limit): {url[:60]}...")
            return False
        
        # Check scope
        if not URLUtils.is_in_scope(url, self.target_domain, self.config['include_subdomains']):
            if not self.config['crawl_external']:
                self.logger.debug(f"[FILTER] Rejected (out of scope): {url[:60]}...")
                return False
        
        # Check extension
        ext = URLUtils.get_file_extension(url)
        if ext in IGNORED_EXTENSIONS:
            self.logger.debug(f"[FILTER] Rejected (ignored ext .{ext}): {url[:60]}...")
            return False
        
        self.logger.debug(f"[FILTER] Accepted: {url[:60]}...")
        return True
    
    async def _crawl_worker(self, worker_id: int):
        """Worker coroutine"""
        self.logger.debug(f"[WORKER-{worker_id}] Starting worker")
        
        async with Fetcher(
            self.header_manager,
            self.rate_limiter,
            self.proxy_handler,
            self.config['timeout'],
            self.config['max_redirects'],
            self.config['verify_ssl'],
            self.logger
        ) as fetcher:
            
            while self.running and not self.interrupted:
                try:
                    item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    if self.queue.empty():
                        self.logger.debug(f"[WORKER-{worker_id}] Queue empty, exiting")
                        break
                    continue
                
                if item is None:
                    continue
                
                url, depth = item
                self.logger.debug(f"[WORKER-{worker_id}] Processing: {url[:60]}... (depth={depth})")
                
                # Fetch
                response, error = await fetcher.fetch(url)
                
                if error:
                    self.logger.debug(f"[WORKER-{worker_id}] Error fetching {url}: {error}")
                    self.errors.append({'url': url, 'error': error})
                    self.stats['errors'] += 1
                    continue
                
                self.stats['urls_crawled'] += 1
                self.logger.debug(f"[WORKER-{worker_id}] Successfully fetched: {url} (status={response['status']})")
                
                # Parse
                parser = Parser(self.target, self.logger if self.config.get('verbose') else None)
                parse_result = parser.parse(response['text'], url)
                
                # Store result
                result_entry = {
                    'url': url,
                    'title': parse_result['title'],
                    'status': response['status'],
                    'content_type': response['content_type'],
                    'length': response['length'],
                    'depth': depth,
                    'redirect': response['final_url'] if response['redirected'] else None,
                }
                
                await self.json_writer.write_entry(result_entry)
                self.discovered_urls.add(url)
                self.logger.debug(f"[WORKER-{worker_id}] Saved result for {url}")
                
                # Update stats
                new_dirs = parse_result['directories'] - self.directories
                new_params = parse_result['parameters'] - self.parameters
                self.directories.update(parse_result['directories'])
                self.parameters.update(parse_result['parameters'])
                
                if new_dirs and self.config.get('verbose'):
                    self.logger.debug(f"[WORKER-{worker_id}] New directories: {new_dirs}")
                if new_params and self.config.get('verbose'):
                    self.logger.debug(f"[WORKER-{worker_id}] New parameters: {new_params}")
                
                # Process JS files
                for js_url in parse_result['js_files']:
                    self.logger.debug(f"[WORKER-{worker_id}] Processing JS: {js_url}")
                    js_content, js_error = await fetcher.fetch_js(js_url)
                    if js_content:
                        endpoints = parser.extract_js_endpoints(js_content)
                        new_endpoints = endpoints - self.js_endpoints
                        self.js_endpoints.update(endpoints)
                        
                        if new_endpoints and self.config.get('verbose'):
                            self.logger.debug(f"[WORKER-{worker_id}] New JS endpoints: {new_endpoints}")
                        
                        # Save JS endpoints
                        interesting = parser.find_interesting_paths(js_content)
                        self.js_endpoints.update(interesting)
                
                # Queue new URLs
                new_links = 0
                for link in parse_result['links']:
                    if self._should_crawl(link, depth + 1):
                        added = await self.queue.add(link, depth + 1)
                        if added:
                            new_links += 1
                
                if new_links > 0:
                    self.logger.debug(f"[WORKER-{worker_id}] Queued {new_links} new URLs from {url}")
                
                # Update live stats
                self.stats['urls_discovered'] = len(self.discovered_urls)
                self.stats['directories'] = len(self.directories)
                self.stats['parameters'] = len(self.parameters)
                self.stats['js_endpoints'] = len(self.js_endpoints)
                
                # Periodic save
                if self.stats['urls_crawled'] % 100 == 0:
                    self.logger.debug(f"[WORKER-{worker_id}] Periodic save (crawled {self.stats['urls_crawled']})")
                    await self._save_progress()
            
            self.logger.debug(f"[WORKER-{worker_id}] Worker finished")
    
    async def _save_progress(self):
        """Save current progress"""
        self.logger.debug("[SAVE] Saving progress...")
        
        await self.json_writer.flush()
        
        # Save wordlists
        self.wordlist_manager.save_directories(self.directories)
        self.wordlist_manager.save_parameters(self.parameters)
        self.wordlist_manager.save_js_endpoints(self.js_endpoints)
        
        # Save state
        state = {
            'target': self.target,
            'seen_urls': list(self.queue.get_seen_urls()),
            'discovered_urls': list(self.discovered_urls),
            'directories': list(self.directories),
            'parameters': list(self.parameters),
            'js_endpoints': list(self.js_endpoints),
            'stats': self.stats,
            'config': self.config,
        }
        self.state_manager.save(state)
        self.logger.debug("[SAVE] Progress saved")
    
    async def crawl(self):
        """Main crawl method"""
        self.running = True
        self.start_time = datetime.now()
        
        self.logger.info(f"[*] Starting crawl of {self.target}")
        self.logger.info(f"[*] Output directory: {self.output_dir}")
        
        # Pre-flight: robots.txt and sitemap
        await self._preflight()
        
        # Add seed URL
        self.logger.debug(f"[CRAWL] Adding seed URL: {self.target}")
        await self.queue.add(self.target, 0)
        
        # Create workers
        self.logger.debug(f"[CRAWL] Starting {self.config['workers']} workers")
        workers = [
            asyncio.create_task(self._crawl_worker(i))
            for i in range(self.config['workers'])
        ]
        
        # Wait for completion or interrupt
        try:
            await asyncio.gather(*workers)
        except asyncio.CancelledError:
            self.logger.debug("[CRAWL] Workers cancelled")
        
        self.running = False
        
        # Final save
        self.logger.debug("[CRAWL] Final save...")
        await self._save_progress()
        
        # Print summary
        self._print_summary()
        
        return not self.interrupted
    
    async def _preflight(self):
        """Pre-flight checks and discoveries with verbose logging"""
        self.logger.info("[*] Running pre-flight checks...")
        self.logger.debug(f"[PREFLIGHT] Target: {self.target}")
        self.logger.debug(f"[PREFLIGHT] Timeout: {self.config['timeout']}s")
        self.logger.debug(f"[PREFLIGHT] Max redirects: {self.config['max_redirects']}")
        
        if self.proxy_handler and self.proxy_handler.is_configured():
            self.logger.info(f"[*] Using proxy: {self.proxy_handler.proxy_url}")
        
        try:
            async with Fetcher(
                self.header_manager,
                self.rate_limiter,
                self.proxy_handler,
                self.config['timeout'],
                self.config['max_redirects'],
                self.config['verify_ssl'],
                self.logger
            ) as fetcher:
                
                # Check robots.txt with timeout
                robots_url = f"{self.target.rstrip('/')}/robots.txt"
                self.logger.info(f"[*] Checking robots.txt: {robots_url}")
                self.logger.debug(f"[PREFLIGHT] Creating DNS lookup for {URLUtils.get_domain(robots_url)}")
                
                try:
                    self.logger.debug("[PREFLIGHT] Sending GET request to robots.txt...")
                    response, error = await asyncio.wait_for(
                        fetcher.fetch(robots_url), 
                        timeout=15
                    )
                    
                    if error:
                        self.logger.info(f"[-] robots.txt error: {error}")
                        self.logger.debug(f"[PREFLIGHT] robots.txt fetch error: {error}")
                    elif response:
                        self.logger.info(f"[+] robots.txt status: {response['status']}")
                        self.logger.debug(f"[PREFLIGHT] robots.txt headers: {dict(response['headers'])}")
                        self.logger.debug(f"[PREFLIGHT] robots.txt content length: {len(response['text'])}")
                        
                        if response['status'] == 200:
                            disallowed = self.robots_parser.parse(response['text'])
                            self.logger.info(f"[+] Found robots.txt with {len(disallowed)} disallowed paths")
                            
                            if disallowed and self.config.get('verbose'):
                                self.logger.debug(f"[PREFLIGHT] Disallowed paths: {list(disallowed)}")
                            
                            # Add disallowed paths to directories for wordlist
                            for path in disallowed:
                                full_url = URLUtils.normalize(self.target.rstrip('/') + path, self.target)
                                if full_url:
                                    self.directories.update(URLUtils.extract_directories(full_url))
                        else:
                            self.logger.info(f"[!] robots.txt returned status {response['status']}")
                            
                except asyncio.TimeoutError:
                    self.logger.warning("[!] robots.txt check timed out after 15s")
                    self.logger.debug("[PREFLIGHT] Timeout exception in robots.txt fetch")
                except Exception as e:
                    self.logger.debug(f"[PREFLIGHT] robots.txt exception: {type(e).__name__}: {e}")
                    self.logger.info(f"[-] robots.txt error: {type(e).__name__}")
                
                # Check sitemap with timeout
                sitemap_urls = [
                    f"{self.target.rstrip('/')}/sitemap.xml",
                    f"{self.target.rstrip('/')}/sitemap_index.xml",
                ]
                
                self.logger.info(f"[*] Checking {len(sitemap_urls)} sitemap locations...")
                
                for sitemap_url in sitemap_urls:
                    self.logger.info(f"[*] Checking sitemap: {sitemap_url}")
                    self.logger.debug(f"[PREFLIGHT] DNS lookup for {URLUtils.get_domain(sitemap_url)}")
                    
                    try:
                        self.logger.debug(f"[PREFLIGHT] Sending GET request to {sitemap_url}...")
                        response, error = await asyncio.wait_for(
                            fetcher.fetch(sitemap_url),
                            timeout=15
                        )
                        
                        if error:
                            self.logger.info(f"[-] Sitemap error: {error}")
                            self.logger.debug(f"[PREFLIGHT] Sitemap fetch error: {error}")
                            continue
                            
                        if response:
                            self.logger.info(f"[+] Sitemap status: {response['status']}")
                            self.logger.debug(f"[PREFLIGHT] Sitemap headers: {dict(response['headers'])}")
                            self.logger.debug(f"[PREFLIGHT] Sitemap content length: {len(response['text'])}")
                            
                            if response['status'] == 200:
                                urls = self.sitemap_parser.parse(response['text'])
                                self.logger.info(f"[+] Found sitemap with {len(urls)} URLs")
                                
                                if urls and self.config.get('verbose'):
                                    self.logger.debug(f"[PREFLIGHT] First 10 URLs: {list(urls)[:10]}")
                                
                                for url in urls:
                                    normalized = URLUtils.normalize(url, self.target)
                                    if normalized and self._should_crawl(normalized, 0):
                                        await self.queue.add(normalized, 0)
                                break
                            else:
                                self.logger.info(f"[!] Sitemap returned status {response['status']}")
                        else:
                            self.logger.info(f"[-] No response from sitemap")
                            
                    except asyncio.TimeoutError:
                        self.logger.warning(f"[!] Sitemap timed out: {sitemap_url}")
                        self.logger.debug(f"[PREFLIGHT] Timeout exception for {sitemap_url}")
                    except Exception as e:
                        self.logger.debug(f"[PREFLIGHT] Sitemap exception: {type(e).__name__}: {e}")
                        self.logger.info(f"[-] Sitemap error: {type(e).__name__}")
                
                self.logger.info("[*] Pre-flight checks completed")
                self.logger.debug(f"[PREFLIGHT] Summary: {self.queue.qsize()} URLs in queue, {len(self.directories)} directories found")
                        
        except Exception as e:
            self.logger.error(f"[-] Pre-flight error: {e}")
            self.logger.debug(f"[PREFLIGHT] Fatal exception: {type(e).__name__}: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
    
    def _print_summary(self):
        """Print final summary"""
        duration = datetime.now() - self.start_time
        
        print("\n" + "="*50)
        print("Scan Summary")
        print("="*50)
        print(f"Target: {self.target}")
        print(f"Duration: {duration}")
        print(f"Total URLs discovered: {self.stats['urls_discovered']}")
        print(f"URLs crawled: {self.stats['urls_crawled']}")
        print(f"Unique directories: {self.stats['directories']}")
        print(f"Unique parameters: {self.stats['parameters']}")
        print(f"JavaScript endpoints: {self.stats['js_endpoints']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Output: {self.output_dir}")
        print("="*50)
    
    def resume(self, state_file: Path):
        """Resume from saved state"""
        self.logger.debug(f"[RESUME] Loading state from {state_file}")
        
        state = self.state_manager.load(state_file)
        if state:
            self.logger.info(f"[*] Resuming crawl from {state_file}")
            self.discovered_urls = set(state.get('discovered_urls', []))
            self.directories = set(state.get('directories', []))
            self.parameters = set(state.get('parameters', []))
            self.js_endpoints = set(state.get('js_endpoints', []))
            self.stats = state.get('stats', self.stats)
            
            self.logger.debug(f"[RESUME] Restored {len(self.discovered_urls)} URLs, {len(self.directories)} directories")
            
            # Restore queue state
            seen = state.get('seen_urls', [])
            self.queue.load_state(seen)
            
            # Re-add discovered but not fully processed URLs
            for url in self.discovered_urls:
                if url not in seen:
                    self.queue.add(url, 0)
            
            return True
        return False
