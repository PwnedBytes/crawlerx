# cli/interface.py
"""
Live Terminal Interface Manager
"""

import sys
import time
import asyncio
from typing import Dict, Optional
from colorama import Fore, Style, init, Cursor

# Initialize colorama
init(autoreset=True)

class Interface:
    """Live interface for real-time crawl statistics"""
    
    def __init__(self, quiet: bool = False):
        self.quiet = quiet
        self.running = False
        self.start_time = time.time()
        self.last_update = 0
        self.update_interval = 0.5  # Update every 0.5 seconds
        
        # Statistics
        self.stats = {
            'urls_crawled': 0,
            'urls_discovered': 0,
            'queue_size': 0,
            'parameters_found': 0,
            'directories_found': 0,
            'js_endpoints': 0,
            'errors': 0,
            'current_url': '',
            'status_code': 0,
        }
        
        # Terminal dimensions
        self.terminal_width = 80
        self._update_terminal_size()
    
    def _update_terminal_size(self):
        """Update terminal dimensions"""
        try:
            import os
            self.terminal_width = os.get_terminal_size().columns
        except:
            pass
    
    def start(self):
        """Start the interface"""
        if self.quiet:
            return
        
        self.running = True
        self.start_time = time.time()
        self._clear_screen()
        self._draw_banner()
    
    def stop(self):
        """Stop the interface"""
        self.running = False
        if not self.quiet:
            print()  # New line after stopping
    
    def update(self, stats: Dict):
        """Update statistics"""
        self.stats.update(stats)
        
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._render()
            self.last_update = current_time
    
    def _clear_screen(self):
        """Clear terminal screen"""
        print('\033[2J\033[H', end='')
    
    def _draw_banner(self):
        """Draw static banner section"""
        banner = f"""{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                   CrawlerX Live Monitor                      ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)
    
    def _render(self):
        """Render current statistics"""
        if self.quiet:
            return
        
        # Move cursor to stats area (after banner)
        print(f'\033[6;0H', end='')
        
        # Clear lines
        for _ in range(10):
            print('\033[K')  # Clear line
        
        # Move back up
        print(f'\033[6;0H', end='')
        
        # Calculate elapsed time
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Format stats lines
        lines = [
            f"{Fore.CYAN}╔{'═' * 62}╗",
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}Runtime:{Style.RESET_ALL} {time_str:<52}{Fore.CYAN}║",
            f"{Fore.CYAN}╠{'═' * 62}╣",
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}URLs Crawled:{Style.RESET_ALL}    {self.stats['urls_crawled']:>8}    {Fore.YELLOW}Queue:{Style.RESET_ALL} {self.stats['queue_size']:>8}      {Fore.CYAN}║",
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}URLs Discovered:{Style.RESET_ALL} {self.stats['urls_discovered']:>8}    {Fore.RED}Errors:{Style.RESET_ALL} {self.stats['errors']:>7}      {Fore.CYAN}║",
            f"{Fore.CYAN}╠{'═' * 62}╣",
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}Directories:{Style.RESET_ALL}     {self.stats['directories_found']:>8}    {Fore.BLUE}Parameters:{Style.RESET_ALL} {self.stats['parameters_found']:>5}   {Fore.CYAN}║",
            f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.MAGENTA}JS Endpoints:{Style.RESET_ALL}    {self.stats['js_endpoints']:>8}                            {Fore.CYAN}║",
            f"{Fore.CYAN}╠{'═' * 62}╣",
        ]
        
        # Current URL (truncated if too long)
        current = self.stats.get('current_url', '')[:50]
        status = self.stats.get('status_code', 0)
        status_color = Fore.GREEN if 200 <= status < 300 else Fore.YELLOW if 300 <= status < 400 else Fore.RED if status >= 400 else Fore.WHITE
        
        lines.append(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}Current:{Style.RESET_ALL} {current:<51}{Fore.CYAN}║")
        lines.append(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.CYAN}Status:{Style.RESET_ALL}  {status_color}{status}{Style.RESET_ALL}                                                {Fore.CYAN}║")
        lines.append(f"{Fore.CYAN}╚{'═' * 62}╝{Style.RESET_ALL}")
        
        # Print all lines
        for line in lines:
            print(line)
        
        sys.stdout.flush()
    
    def log_message(self, message: str, level: str = 'info'):
        """Log a message below the stats area"""
        if self.quiet:
            return
        
        # Save cursor position
        print('\033[s', end='')
        
        # Move to bottom
        print('\033[20;0H', end='')
        
        # Color based on level
        color = Fore.CYAN
        prefix = '*'
        if level == 'success':
            color = Fore.GREEN
            prefix = '+'
        elif level == 'warning':
            color = Fore.YELLOW
            prefix = '!'
        elif level == 'error':
            color = Fore.RED
            prefix = '-'
        
        # Print message
        print(f"{color}[{prefix}]{Style.RESET_ALL} {message}")
        
        # Restore cursor and re-render
        print('\033[u', end='')
        self._render()
    
    def print_summary(self, stats: Dict):
        """Print final summary"""
        if not self.quiet:
            print('\n' + '=' * 50)
            print(f"{Fore.CYAN}Scan Summary{Style.RESET_ALL}")
            print('=' * 50)
            print(f"Total URLs discovered: {stats.get('urls_discovered', 0)}")
            print(f"URLs crawled: {stats.get('urls_crawled', 0)}")
            print(f"Unique directories: {stats.get('directories', 0)}")
            print(f"Unique parameters: {stats.get('parameters', 0)}")
            print(f"JavaScript endpoints: {stats.get('js_endpoints', 0)}")
            print(f"Errors: {stats.get('errors', 0)}")
            print('=' * 50)


class SimpleInterface:
    """Simple non-interactive interface for quiet mode"""
    
    def __init__(self):
        self.stats = {}
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def update(self, stats: Dict):
        self.stats = stats
    
    def log_message(self, message: str, level: str = 'info'):
        print(message)
    
    def print_summary(self, stats: Dict):
        print(f"\nCompleted: {stats.get('urls_crawled', 0)} URLs crawled")
