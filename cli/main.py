# cli/main.py
"""
Main CLI Entry Point
"""

import argparse
import asyncio
import sys
from pathlib import Path

from cli.banner import Banner, Interface
from utils.validators import Validators
from utils.logger import Logger
from core.crawler import Crawler
from config import TARGETS_DIR

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description='CrawlerX - High-Performance Web Crawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -u https://example.com
  %(prog)s -u https://example.com --depth 5 --workers 20
  %(prog)s -l domains.txt --rate 10 --proxy http://127.0.0.1:8080
  %(prog)s --resume example.com
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-u', '--url', help='Single target URL')
    input_group.add_argument('-l', '--list', help='File containing target URLs')
    input_group.add_argument('--resume', help='Resume previous scan by domain')
    
    # Performance options
    parser.add_argument('-w', '--workers', type=int, default=10,
                       help='Number of concurrent workers (default: 10)')
    parser.add_argument('-r', '--rate', type=int, default=10,
                       help='Requests per second (default: 10)')
    parser.add_argument('-d', '--depth', type=int, default=3,
                       help='Maximum crawl depth (default: 3)')
    
    # Scope options
    parser.add_argument('--include-subdomains', action='store_true',
                       help='Include subdomains in crawl scope')
    parser.add_argument('--crawl-external', action='store_true',
                       help='Crawl external links')
    
    # Network options
    parser.add_argument('--proxy', help='Proxy URL (http://host:port)')
    parser.add_argument('-H', '--header', action='append', dest='headers',
                       help='Custom header (format: "Name: Value")')
    parser.add_argument('--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')
    
    # Output options
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (no banner)')
    parser.add_argument('--no-verify-ssl', action='store_true',
                       help='Disable SSL verification')
    
    return parser

async def crawl_single(url: str, args):
    """Crawl single target"""
    config = {
        'workers': args.workers,
        'rate': args.rate,
        'depth': args.depth,
        'include_subdomains': args.include_subdomains,
        'crawl_external': args.crawl_external,
        'proxy': args.proxy,
        'headers': args.headers or [],
        'timeout': args.timeout,
        'verify_ssl': not args.no_verify_ssl,
        'verbose': args.verbose,
        'quiet': args.quiet,
    }
    
    crawler = Crawler(url, **config)
    success = await crawler.crawl()
    return success

async def crawl_multiple(urls: list, args):
    """Crawl multiple targets"""
    for url in urls:
        Banner.info(f"Starting crawl of {url}")
        success = await crawl_single(url, args)
        
        if not success:
            Banner.warning(f"Crawl interrupted for {url}")
            break
    
    Banner.success("All crawls completed")

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Show banner
    if not args.quiet:
        Banner.show()
    
    # Handle resume
    if args.resume:
        state_file = TARGETS_DIR / args.resume / "crawl_state.json"
        if not state_file.exists():
            Banner.error(f"No state file found for {args.resume}")
            sys.exit(1)
        
        # Create crawler with resume
        crawler = Crawler(f"https://{args.resume}")  # Protocol doesn't matter for resume
        crawler.resume(state_file)
        
        try:
            asyncio.run(crawler.crawl())
        except KeyboardInterrupt:
            Banner.warning("Crawl interrupted by user")
        return
    
    # Validate inputs
    if args.url:
        is_valid, error = Validators.validate_url(args.url)
        if not is_valid:
            Banner.error(error)
            sys.exit(1)
        
        targets = [args.url]
    
    elif args.list:
        is_valid, targets, error = Validators.validate_domain_list(args.list)
        if not is_valid:
            Banner.error(error)
            sys.exit(1)
        
        Banner.info(f"Loaded {len(targets)} targets from {args.list}")
    
    # Validate performance options
    valid, workers, error = Validators.validate_workers(args.workers)
    if not valid:
        Banner.error(error)
        sys.exit(1)
    args.workers = workers
    
    valid, rate, error = Validators.validate_rate(args.rate)
    if not valid:
        Banner.error(error)
        sys.exit(1)
    args.rate = rate
    
    valid, depth, error = Validators.validate_depth(args.depth)
    if not valid:
        Banner.error(error)
        sys.exit(1)
    args.depth = depth
    
    # Validate proxy
    if args.proxy:
        valid, error = Validators.validate_proxy(args.proxy)
        if not valid:
            Banner.error(error)
            sys.exit(1)
    
    # Run crawler
    try:
        if len(targets) == 1:
            asyncio.run(crawl_single(targets[0], args))
        else:
            asyncio.run(crawl_multiple(targets, args))
            
    except KeyboardInterrupt:
        Banner.warning("Crawl interrupted by user")
        sys.exit(130)
    except Exception as e:
        Banner.error(f"Fatal error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
