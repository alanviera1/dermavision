import time

from dermavision.modules.climate.cache import TTLCache


def test_cache_hit() -> None:
    cache = TTLCache(ttl_seconds=60.0)
    key = ("42.0", "-3.6")
    cache.put(key, {"uv_index": 7})
    assert cache.get(key) == {"uv_index": 7}


def test_cache_miss_after_clear() -> None:
    cache = TTLCache(ttl_seconds=60.0)
    cache.put(("k",), 1)
    cache.clear()
    assert cache.get(("k",)) is None


def test_cache_expiry() -> None:
    cache = TTLCache(ttl_seconds=0.01)
    cache.put(("k",), 1)
    time.sleep(0.02)
    assert cache.get(("k",)) is None
