"""
Cache module for managing temporary data storage.
"""
from .surreal_cache_manager import SurrealCacheManager

# Global cache instance
_cache_manager = None

async def initialize_cache():
    """Initialize the cache manager."""
    global _cache_manager
    _cache_manager = SurrealCacheManager()
    await _cache_manager.initialize()
    return _cache_manager

async def close_cache():
    """Close the cache manager."""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None

def get_cache_manager():
    """Get the cache manager instance."""
    return _cache_manager

__all__ = ["initialize_cache", "close_cache", "get_cache_manager", "SurrealCacheManager"]
