# storage/wordlist_manager.py
"""
Wordlist Manager
"""

from pathlib import Path
from typing import Set, List
import aiofiles

class WordlistManager:
    """Manage wordlist generation and storage"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.dirs_file = output_dir / "directories.txt"
        self.params_file = output_dir / "parameters.txt"
        self.js_file = output_dir / "js_endpoints.txt"
    
    def save_directories(self, directories: Set[str]):
        """Save directory wordlist"""
        sorted_dirs = sorted(directories)
        self._write_sync(self.dirs_file, sorted_dirs)
    
    def save_parameters(self, parameters: Set[str]):
        """Save parameter wordlist"""
        sorted_params = sorted(parameters)
        self._write_sync(self.params_file, sorted_params)
    
    def save_js_endpoints(self, endpoints: Set[str]):
        """Save JS endpoints"""
        sorted_endpoints = sorted(endpoints)
        self._write_sync(self.js_file, sorted_endpoints)
    
    def _write_sync(self, filepath: Path, items: List[str]):
        """Synchronous write (for compatibility)"""
        try:
            with open(filepath, 'w') as f:
                for item in items:
                    f.write(f"{item}\n")
        except Exception:
            pass
    
    async def merge_to_master(self, master_dirs: Path, master_params: Path):
        """Merge current wordlists to master lists"""
        try:
            # Read current
            current_dirs = set()
            if self.dirs_file.exists():
                async with aiofiles.open(self.dirs_file, 'r') as f:
                    content = await f.read()
                    current_dirs = set(line.strip() for line in content.split('\n') if line.strip())
            
            # Read master
            master_dirs_set = set()
            if master_dirs.exists():
                async with aiofiles.open(master_dirs, 'r') as f:
                    content = await f.read()
                    master_dirs_set = set(line.strip() for line in content.split('\n') if line.strip())
            
            # Merge and write
            merged = sorted(master_dirs_set | current_dirs)
            async with aiofiles.open(master_dirs, 'w') as f:
                for item in merged:
                    await f.write(f"{item}\n")
                    
        except Exception:
            pass
