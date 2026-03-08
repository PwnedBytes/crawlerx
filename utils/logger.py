# utils/logger.py
"""
Logging utilities for CrawlerX
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class Logger:
    """Custom logger for CrawlerX"""
    
    def __init__(self, name: str = "CrawlerX", log_file: Optional[Path] = None, 
                 verbose: bool = False, quiet: bool = False):
        self.name = name
        self.verbose = verbose
        self.quiet = quiet
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Console handler
        if not quiet:
            console_handler = logging.StreamHandler(sys.stdout)
            console_level = logging.DEBUG if verbose else logging.INFO
            console_handler.setLevel(console_level)
            
            if verbose:
                console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
            else:
                console_format = logging.Formatter('%(message)s')
            console_handler.setFormatter(console_format)
            self.logger.addHandler(console_handler)
        
        # File handler - always log everything to file
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
    
    def debug(self, msg: str):
        """Log debug message"""
        self.logger.debug(msg)
    
    def info(self, msg: str):
        """Log info message"""
        self.logger.info(msg)
    
    def warning(self, msg: str):
        """Log warning message"""
        self.logger.warning(msg)
    
    def error(self, msg: str):
        """Log error message"""
        self.logger.error(msg)
    
    def critical(self, msg: str):
        """Log critical message"""
        self.logger.critical(msg)
    
    def success(self, msg: str):
        """Log success message"""
        self.logger.info(f"[+] {msg}")
    
    def status(self, msg: str):
        """Log status update"""
        if not self.quiet:
            self.logger.info(f"[*] {msg}")
