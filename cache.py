import hashlib
import json
from datetime import datetime, timedelta
from logger import logger

class SimpleCache:
    """
    A simple in‑memory cache with TTL (Time‑To‑Live).
    No Redis required – works anywhere.
    """
    def __init__(self):
        self._cache = {}
        self._ttl_seconds = 3600  # 1 hour default
    
    def _get_key(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str):
        key = self._get_key(query)
        entry = self._cache.get(key)
        if entry:
            data, timestamp = entry
            age = (datetime.now() - timestamp).total_seconds()
            if age < self._ttl_seconds:
                logger.info(f"✅ Cache HIT for: {query[:50]}...")
                return data
            else:
                # expired
                del self._cache[key]
        logger.info(f"❌ Cache MISS for: {query[:50]}...")
        return None
    
    def set(self, query: str, data: dict):
        key = self._get_key(query)
        self._cache[key] = (data, datetime.now())
        logger.info(f"💾 Cached: {query[:50]}...")

# Global instance
cache = SimpleCache()