# core/queue_manager.py
"""
Async URL Queue Manager
"""

import asyncio
from typing import Set, Optional, List
from collections import deque

class QueueManager:
    """Manages URL queue with deduplication"""
    
    def __init__(self, maxsize: int = 0, logger=None):
        self.queue = asyncio.Queue(maxsize=maxsize)
        self.seen_urls: Set[str] = set()
        self.queued_urls: Set[str] = set()
        self.lock = asyncio.Lock()
        self.total_queued = 0
        self.total_processed = 0
        self.logger = logger
    
    async def add(self, url: str, depth: int = 0) -> bool:
        """
        Add URL to queue if not seen
        Returns: True if added, False if already seen
        """
        async with self.lock:
            if url in self.seen_urls or url in self.queued_urls:
                if self.logger:
                    self.logger.debug(f"[QUEUE] Rejected (duplicate): {url[:80]}...")
                return False
            
            self.queued_urls.add(url)
            self.total_queued += 1
            
            if self.logger:
                self.logger.debug(f"[QUEUE] Added: {url[:80]}... (depth={depth}, queue_size={self.queue.qsize()})")
            
        await self.queue.put((url, depth))
        return True
    
    async def get(self) -> Optional[tuple]:
        """Get next URL from queue"""
        try:
            url, depth = await self.queue.get()
            async with self.lock:
                self.queued_urls.discard(url)
                self.seen_urls.add(url)
                self.total_processed += 1
                
                if self.logger:
                    self.logger.debug(f"[QUEUE] Retrieved: {url[:80]}... (depth={depth}, remaining={self.queue.qsize()})")
                    
            return (url, depth)
        except asyncio.CancelledError:
            return None
    
    def mark_visited(self, url: str):
        """Mark URL as visited"""
        self.seen_urls.add(url)
    
    def is_visited(self, url: str) -> bool:
        """Check if URL was visited"""
        return url in self.seen_urls
    
    def is_queued(self, url: str) -> bool:
        """Check if URL is in queue"""
        return url in self.queued_urls
    
    def qsize(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()
    
    def empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        return {
            'queued': self.qsize(),
            'seen': len(self.seen_urls),
            'total_queued': self.total_queued,
            'total_processed': self.total_processed
        }
    
    def get_seen_urls(self) -> List[str]:
        """Get list of all seen URLs"""
        return list(self.seen_urls)
    
    def load_state(self, urls: List[str]):
        """Load previously seen URLs"""
        if self.logger:
            self.logger.debug(f"[QUEUE] Loading {len(urls)} previously seen URLs")
        self.seen_urls.update(urls)
