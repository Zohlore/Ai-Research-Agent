import redis
import json
import hashlib
from functools import wraps
from logger import logger

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db)
            self.client.ping()
            self.enabled = True
            logger.info("Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.enabled = False
    
    def get_key(self, query: str) -> str:
        """Generate a cache key from a query."""
        return f"research:{hashlib.md5(query.encode()).hexdigest()}"
    
    def get(self, query: str) -> dict | None:
        """Get cached result."""
        if not self.enabled:
            return None
        key = self.get_key(query)
        data = self.client.get(key)
        if data:
            logger.info(f"Cache hit for: {query[:50]}...")
            return json.loads(data)
        return None
    
    def set(self, query: str, result: dict, ttl: int = 3600):
        """Cache result."""
        if not self.enabled:
            return
        key = self.get_key(query)
        self.client.setex(key, ttl, json.dumps(result))
        logger.info(f"Cached: {query[:50]}...")

# Global cache instance
cache = RedisCache()