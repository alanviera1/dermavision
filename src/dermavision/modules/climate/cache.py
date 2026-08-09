from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    def __init__(self, ttl_seconds: float) -> None:
        self._ttl_seconds = ttl_seconds
        self._store: dict[tuple[str, ...], tuple[float, T]] = {}

    def get(self, key: tuple[str, ...]) -> T | None:
        item = self._store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if self._expired(expires_at):
            del self._store[key]
            return None
        return value

    def put(self, key: tuple[str, ...], value: T) -> None:
        self._store[key] = (self._now() + self._ttl_seconds, value)

    def clear(self) -> None:
        self._store.clear()

    def _expired(self, expires_at: float) -> bool:
        return self._now() > expires_at

    @staticmethod
    def _now() -> float:
        import time

        return time.monotonic()
