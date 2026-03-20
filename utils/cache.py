from cachetools import TTLCache
from config import CACHE_TTL, CACHE_MAX_SIZE

_cache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL)


def get_cache(key):
    return _cache.get(key)


def set_cache(key, value):
    _cache[key] = value
