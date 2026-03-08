# storage/json_writer.py
"""
JSON Results Writer
"""

import json
import aiofiles
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class JSONWriter:
    """Async JSON writer for crawl results"""
    
    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.buffer: List[Dict] = []
        self.buffer_size = 10
        self.lock = asyncio.Lock()
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialize output file with header"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write initial structure
        initial_data = {
            'crawler': 'CrawlerX',
            'version': '1.0',
            'start_time': datetime.now().isoformat(),
            'results': []
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(initial_data, f, indent=2)
    
    async def write_entry(self, entry: Dict[str, Any]):
        """Write single entry to buffer"""
        async with self.lock:
            self.buffer.append(entry)
            
            if len(self.buffer) >= self.buffer_size:
                await self._flush_buffer()
    
    async def _flush_buffer(self):
        """Flush buffer to disk"""
        if not self.buffer:
            return
        
        try:
            # Read existing
            async with aiofiles.open(self.output_file, 'r') as f:
                content = await f.read()
                data = json.loads(content)
            
            # Append new entries
            data['results'].extend(self.buffer)
            data['last_updated'] = datetime.now().isoformat()
            
            # Write back
            async with aiofiles.open(self.output_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            
            self.buffer = []
            
        except Exception as e:
            # If fails, keep buffer for next try
            pass
    
    async def flush(self):
        """Force flush buffer"""
        async with self.lock:
            await self._flush_buffer()
    
    async def write_metadata(self, metadata: Dict):
        """Write metadata to file"""
        async with self.lock:
            try:
                async with aiofiles.open(self.output_file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                
                data['metadata'] = metadata
                
                async with aiofiles.open(self.output_file, 'w') as f:
                    await f.write(json.dumps(data, indent=2))
                    
            except Exception:
                pass
