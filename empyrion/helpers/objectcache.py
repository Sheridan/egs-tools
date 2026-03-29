import copy
from typing import Any


class ObjectCache:
  def __init__(self):
    self._cache: dict[str, Any] = {}

  def set(self, key: str, value: Any) -> None:
    self._cache[key] = copy.deepcopy(value)
    return self._cache[key]

  def get(self, key: str, default: Any = None) -> Any:
    if key in self._cache:
      return copy.deepcopy(self._cache[key])
    return default

  def delete(self, key: str) -> bool:
    if key in self._cache:
      del self._cache[key]
      return True
    return False

  def contains(self, key: str) -> bool:
    return key in self._cache

  def clear(self) -> None:
    self._cache.clear()

  def size(self) -> int:
    return len(self._cache)

  def keys(self) -> list[str]:
    return list(self._cache.keys())

  def __len__(self) -> int:
    return len(self._cache)

  def __contains__(self, key: str) -> bool:
    return key in self._cache

  def __repr__(self) -> str:
    return f"ObjectCache(size={len(self._cache)})"
