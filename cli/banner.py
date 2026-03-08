# cli/banner.py
"""
Terminal Banner and Display
"""

import sys
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class Banner:
    """Display banners and colored output"""
    
    VERSION = "1.0"
    
    @staticmethod
    def show():
        """Display CrawlerX banner"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   {Fore.GREEN}██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗██████╗{Fore.CYAN}   ║
║  {Fore.GREEN}██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔══██╗{Fore.CYAN}  ║
║  {Fore.GREEN}██║     ██████╔╝███████║██║ █╗ ██║██║     █████╗  ██████╔╝{Fore.CYAN}  ║
║  {Fore.GREEN}██║     ██╔══██╗██╔══██║██║███╗██║██║     ██╔══╝  ██╔══██╗{Fore.CYAN}  ║
║  {Fore.GREEN}╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████╗██║  ██║{Fore.CYAN}  ║
║   {Fore.GREEN}╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚═╝  ╚═╝{Fore.CYAN}   ║
║                                                          ║
║              {Fore.YELLOW}High-Performance Web Crawler{Fore.CYAN}                 ║
║                   {Fore.MAGENTA}Version {Banner.VERSION}{Fore.CYAN}                      ║
║              {Fore.WHITE}Developed by: Pwned Bytes{Fore.CYAN}                    ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    @staticmethod
    def success(msg: str):
        """Print success message"""
        print(f"{Fore.GREEN}[+] {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def error(msg: str):
        """Print error message"""
        print(f"{Fore.RED}[-] {msg}{Style.RESET_ALL}", file=sys.stderr)
    
    @staticmethod
    def warning(msg: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}[!] {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def info(msg: str):
        """Print info message"""
        print(f"{Fore.CYAN}[*] {msg}{Style.RESET_ALL}")
    
    @staticmethod
    def debug(msg: str):
        """Print debug message"""
        print(f"{Fore.WHITE}[D] {msg}{Style.RESET_ALL}")


class Interface:
    """Live interface for crawl statistics"""
    
    def __init__(self):
        self.stats = {}
        self.running = False
    
    def update(self, stats: dict):
        """Update and display stats"""
        self.stats = stats
        self._display()
    
    def _display(self):
        """Display current stats"""
        # Clear line and print stats
        output = f"\r{Fore.CYAN}URLs: {Fore.WHITE}{self.stats.get('urls_crawled', 0)}{Fore.CYAN} | "
        output += f"Queue: {Fore.WHITE}{self.stats.get('queued', 0)}{Fore.CYAN} | "
        output += f"Dirs: {Fore.WHITE}{self.stats.get('directories', 0)}{Fore.CYAN} | "
        output += f"Params: {Fore.WHITE}{self.stats.get('parameters', 0)}{Fore.CYAN} | "
        output += f"JS: {Fore.WHITE}{self.stats.get('js_endpoints', 0)}{Style.RESET_ALL}"
        
        # Pad with spaces to clear previous line
        output += " " * 10
        
        print(output, end='', flush=True)
    
    def finish(self):
        """Finish display"""
        print()  # New line
