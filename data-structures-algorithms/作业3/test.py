from html.parser import HTMLParser
from collections import deque

class HTMLTagValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = deque()
        self.errors = []
    
    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)
    
    def handle_endtag(self, tag):
        if not self.stack:
            self.errors.append(f"Неожиданный закрывающий тег </{tag}>")
        elif self.stack[-1] == tag:
            self.stack.pop()
        else:
            expected = self.stack[-1]
            self.errors.append(f"Ожидался закрывающий тег </{expected}>, но получен </{tag}>")
    
    def validate(self, html):
        self.stack.clear()
        self.errors.clear()
        self.feed(html)
        
        # Проверяем оставшиеся незакрытые теги
        for tag in reversed(self.stack):
            self.errors.append(f"Отсутствует закрывающий тег </{tag}>")
        
        return not bool(self.errors), self.errors

# Пример использования
html_content = """
<html>
<head>
    <title>
    Example
    </title>
</head>
<body>
<h1>Hello, world</h1>
</body>
</html>
"""

validator = HTMLTagValidator()
is_valid, errors = validator.validate(html_content)

if is_valid:
    print("HTML разметка корректна")
else:
    print("Найдены ошибки в HTML разметке:")
    for error in errors:
        print(f"- {error}")