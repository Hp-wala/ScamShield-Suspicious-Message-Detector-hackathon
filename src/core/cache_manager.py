import threading
from functools import lru_cache


class CacheManager:
    def __init__(self):
        self._lock = threading.RLock()

    def cached(self, maxsize: int = 128):
        def decorator(func):
            cached_func = lru_cache(maxsize=maxsize)(func)

            def wrapper(*args, **kwargs):
                with self._lock:
                    return cached_func(*args, **kwargs)

            wrapper.cache_clear = cached_func.cache_clear
            wrapper.cache_info = cached_func.cache_info
            return wrapper

        return decorator
