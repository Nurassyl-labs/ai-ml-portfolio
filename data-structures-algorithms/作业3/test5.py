def process_expression(expr):
    # Удаляем все пробелы из выражения
    expr = expr.replace(' ', '')
    
    # Инвертируем выражение и меняем скобки местами
    reversed_expr = []
    for c in expr[::-1]:
        if c == '(':
            reversed_expr.append(')')
        elif c == ')':
            reversed_expr.append('(')
        else:
            reversed_expr.append(c)
    reversed_expr = ''.join(reversed_expr)
    
    stack = []
    output = []
    i = 0
    n = len(reversed_expr)
    
    while i < n:
        char = reversed_expr[i]
        
        if char.isalpha():  # Операнд (может быть из нескольких символов)
            operand = [char]
            i += 1
            while i < n and reversed_expr[i].isalpha():
                operand.append(reversed_expr[i])
                i += 1
            output.append(''.join(reversed(operand)))
            continue
            
        elif char == '(':
            stack.append(char)
            
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Удаляем '('
            
        else:  # Оператор
            precedence = {'*':3, '/':3, '+':2, '-':2}
            # Учитываем левую ассоциативность (<= вместо <)
            while stack and stack[-1] != '(' and precedence[char] <= precedence.get(stack[-1], 0):
                output.append(stack.pop())
            stack.append(char)
            
        i += 1
    
    # Добавляем оставшиеся операторы
    while stack:
        output.append(stack.pop())
    
    # Инвертируем результат и добавляем пробелы
    return ' '.join(output[::-1])

# Основная программа
N = int(input())
for _ in range(N):
    expr = input().strip()
    # Обрабатываем случай с одним операндом
    if all(c.isalpha() or c == ' ' for c in expr):
        print(expr.replace(' ', ''))
    else:
        print(process_expression(expr))