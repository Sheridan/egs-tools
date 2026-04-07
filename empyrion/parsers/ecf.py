import pprint
from rich import print as rprint
import empyrion.helpers.color as clr

class CEcf:
  def __init__(self, filename, name, key_field):
    self._filename = filename
    self._name = name
    self._key_field = key_field
    self._data = {}
    self._name_index = []
    self._content = ""
    self._content_len = 0
    self._position = -1
    self._postprocess_fields = ['Id', 'Name']
    self._load()
    self._parse()

  def _load(self):
    rprint(clr.loadf(self._filename))
    with open(self._filename, 'r', encoding='utf-8') as f:
      self._content = f.read()
      self._content_len = len(self._content)

  def _isEOF(self):
    return self._position >= self._content_len

  def _currentChar(self):
    if not self._isEOF():
      # print(self._content[self._position], end="")
      return self._content[self._position]
    return None

  def _futureChar(self):
    return self._content[self._position + 1]

  def _nextChar(self):
    self._position += 1
    return self._currentChar()

  def _isCommentStart(self):
    return self._currentChar() == "#" or (self._currentChar() == "/" and self._futureChar() == "*")

  def _isCommentEnd(self):
    return self._currentChar() == "\n" or (self._currentChar() == "*" and self._futureChar() == "/")

  def _skipComment(self):
    comment = ""
    while True:
      comment += self._nextChar()
      if self._isCommentEnd():
        break

  def _parseVariable(self, char):
    name = ""
    delimiter = False
    value = ""
    while char != "\n":
      if self._isCommentStart():
        self._skipComment()
        break
      if char != ':' and not delimiter:
        name += char
      if char != ':' and delimiter:
        value += char
      if char == ':':
        if not delimiter:
          delimiter = True
        else:
          value += char
      char = self._nextChar()
    return (name.strip(), value.strip())

  def _hasColonOutsideQuotes(self, s):
    in_single_quotes = False
    in_double_quotes = False

    for char in s:
        if char == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
        elif char == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
        elif char == ':' and not in_single_quotes and not in_double_quotes:
            return True

    return False

  def _splitVariable(self, value):
    # print(value)
    if not self._hasColonOutsideQuotes(value):
      return value
    variable_data = []
    current = ""
    in_double_quotes = False
    in_single_quotes = False

    for char in value:
        if char == '"' and not in_single_quotes:
            in_double_quotes = not in_double_quotes
            current += char
        elif char == "'" and not in_double_quotes:
            in_single_quotes = not in_single_quotes
            current += char
        elif char == ',' and not in_double_quotes and not in_single_quotes:
            variable_data.append(current.strip())
            current = ""
        else:
            current += char

    if current:
        variable_data.append(current.strip())

    result = {'value': variable_data[0]}
    for item in variable_data[1:]:
      splitted = item.split(':')
      result[splitted[0].strip()] = splitted[1].strip()

    return result

  def _sectionPostprocess(self, section):
    # pprint.pprint(section)
    # if 'Id' in section:
    #   print(section['Id'])
    #   print(type(section['Id']))
    for field_name in self._postprocess_fields:
      if field_name in section and isinstance(section[field_name], dict):
        for key in section[field_name]:
          # print(key)
          if key != 'value':
            section[key] = section[field_name][key]
        section[field_name] = section[field_name]['value']
    return section

  def _parseSection(self, char):
    section_type_parse = True
    section_type = ""
    section = {}
    while char != '}':
      char = self._nextChar()
      if self._isCommentStart():
        self._skipComment()
        continue
      if char.isspace():
        if section_type_parse and len(section_type) > 0:
          section_type_parse = False
        continue
      if char.isalnum():
        if section_type_parse:
          section_type += char
        else:
          variable = self._parseVariable(char)
          # pprint.pprint(section, indent=2, width=160)
          section[variable[0]] = self._splitVariable(variable[1])
      if char == '{':
        subsection = self._parseSubSection(char)
        self._appendSubSection(subsection[0], subsection[1], subsection[2], section)
    # print(section_type)
    # pprint.pprint(section, indent=2, width=160)
    return (section_type.strip(), self._sectionPostprocess(section))

  def _parseSubSection(self, char):
    subsection_type_parse = True
    subsection_type = ""
    subsection_name_parse = False
    subsection_name = ""
    subsection = {}
    while char != '}':
      char = self._nextChar()
      if self._isCommentStart():
        self._skipComment()
        continue
      if char.isspace():
        if subsection_type_parse and len(subsection_type) > 0:
          subsection_type_parse = False
          subsection_name_parse = True
        if subsection_name_parse and len(subsection_name) > 0:
          subsection_name_parse = False
        continue
      if char.isalnum():
        if subsection_type_parse:
          subsection_type += char
          continue
        if subsection_name_parse:
          subsection_name += char
          continue

        variable = self._parseVariable(char)
        # pprint.pprint(variable, indent=2, width=160)
        subsection[variable[0]] = self._splitVariable(variable[1])
    return (subsection_type.strip(), subsection_name.strip(), subsection)

  def _appendSubSection(self, type, name, content, section):
    if type not in section:
      section[type] = {}
    section[type][name] = content

  def _appendSection(self, name, content):
    if name not in self._data:
      self._data[name] = {}
    # pprint.pprint(content)
    section_key = content[self._key_field]
    # if section_key not in self._name_index:
    #   self._name_index.append(section_key)
    self._data[name][section_key] = content

  def _parse(self):
    while not self._isEOF():
      char = self._nextChar()
      if char:
        if self._isCommentStart():
          self._skipComment()
          continue
        if char.isspace():
          continue
        if char == '{':
          section = self._parseSection(char)
          self._appendSection(section[0], section[1])

  def keys(self):
    return sorted(self._data[self._name].keys())

  def count(self):
    return len(self._data[self._name])

  def exists(self, key):
    return key in self._data[self._name]

  def search(self, field, value):
    result = []
    for section_key in self._data[self._name]:
      section = self._data[self._name][section_key]
      if field in section and section[field] == value:
        result.append(section)
    return result

  def get(self, key):
    if self.exists(key):
      # pprint.pprint(self._data[self._name][key])
      return self._data[self._name][key]
    return None
