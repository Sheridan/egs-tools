import hashlib
from empyrion.options import options
from empyrion.helpers.filesystem import append_to_file
class CHasher:
  def __init__(self, group, key):
    self._key = key
    self._group = group
    self._data = b''
    self.append(self._group + self._key)
    self._hash = None

  def _normalize(self, obj):
    if isinstance(obj, dict):
      return tuple(sorted((k, self._normalize(v)) for k, v in obj.items()))
    if isinstance(obj, list):
      return tuple(self._normalize(item) for item in obj)
    if isinstance(obj, set):
      return tuple(sorted(self._normalize(item) for item in obj))
    if isinstance(obj, tuple):
      return tuple(self._normalize(item) for item in obj)
    return obj

  def append(self, data):
    self._data += repr(self._normalize(data)).encode('utf-8')

  def hash(self):
    if self._hash is None:
      self._hash = hashlib.sha256(self._data).hexdigest()
      if options.get("debug_hasher", False):
        append_to_file('hasher', f'[{self._key}:{self._group}] [{self._hash}] {self._data}')
    return self._hash

  def key(self):
    return self._key

  def group(self):
    return self._group
