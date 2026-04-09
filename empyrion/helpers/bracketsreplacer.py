import re

class CBracketsReplacer:
    def __init__(self, text):
        self._text = text

    def should_replace(self, inner: str) -> bool:
        if re.search(r'[^\s]=[^\s]', inner):
            return False
        if ' ' in inner:
            return True
        if '{' in inner:
            return True
        # Ищем любую пару скобок внутри (нежадный захват)
        if re.search(r'\[.*?\]|<.*?>', inner):
            return True
        return False

    def repl_square(self, match):
        inner = match.group(1)
        if self.should_replace(inner):
            return f'〔{inner}〕'
        return match.group(0)

    def repl_angle(self, match):
        inner = match.group(1)
        if self.should_replace(inner):
            return f'⦑{inner}⦒'   # или ⦑⦒ по желанию
        return match.group(0)

    def replace(self) -> str:
        text = re.sub(r'\[(.*?)\]', self.repl_square, self._text)
        text = re.sub(r'<(.*?)>', self.repl_angle, text)
        return text
