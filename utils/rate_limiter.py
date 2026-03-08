# utils/rate_limiter.py
"""
Rate limiting for async requests
"""

import asyncio
import time
from typing import Optional

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, rate: int = 10):
        """
        Initialize rate limiter
        rate: requests per second
        """
        self.rate = rate
        self.tokens = rate
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make request"""
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_update
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)
                self.tokens = 0
            else:
                self.tokens -= 1
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
