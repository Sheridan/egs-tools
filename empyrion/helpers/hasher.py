import hashlib
import json
from empyrion.options import options
from empyrion.helpers.filesystem import append_to_file

class CHasher:
  def __init__(self, group, key):
    self._key = key
    self._group = group
    self._data = [self._group, self._key]
    self._hash = None

  def _normalize(self, obj):
    if isinstance(obj, dict):
      return {k: self._normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, set, tuple)):
      items = [self._normalize(item) for item in obj]
      return sorted(items, key=lambda x: json.dumps(x, sort_keys=True, default=str))
    return obj

  def append(self, data):
    self._data.append(data)

  def hash(self):
    if self._hash is None:
      normalized = self._normalize(self._data)
      data_bytes = json.dumps(normalized, sort_keys=True, ensure_ascii=False).encode('utf-8')
      self._hash = hashlib.sha256(data_bytes).hexdigest()
      if options.get("debug_hasher", False):
        append_to_file('hasher', f'[{self._key}:{self._group}] [{self._hash}] {data_bytes.decode("utf-8")}')
    return self._hash

  def key(self):
    return self._key

  def group(self):
    return self._group
