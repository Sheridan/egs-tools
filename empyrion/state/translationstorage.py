from empyrion.jsonstorage import CJsonStorage
from empyrion.helpers.hasher import CHasher

class CTranslationStorage(CJsonStorage):
  def __init__(self, name):
    self._name = name
    super().__init__('trash/storage.json')

  def _contextHash(self, key, context):
    hasher = CHasher(self._name, key)
    hasher.append(context)
    return hasher.hash()

  def set(self, key, original_text, translated_text, context):
    self._set('storage', self._name, key, {
      'original_text': original_text,
      'translated_text': translated_text,
      'context_hash': self._contextHash(key, context)
    })

  def exists(self, key, original_text, context):
    section = self._section('storage', self._name)
    if section is None:
      return False
    if key not in section:
      return False
    return section[key]['original_text'] == original_text and section[key]['context_hash'] == self._contextHash(key, context)

  def get(self, key):
    section = self._section('storage', self._name)
    if section is None:
      return ''
    if key in section and 'translated_text' in section[key]:
      return section[key]['translated_text']
    return ''

  def rm(self, key):
    self._rm('storage', self._name, key)
