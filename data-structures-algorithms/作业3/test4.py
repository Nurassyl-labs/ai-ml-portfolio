n = int(input())
for _ in range(n):
    e = input().strip()
    e = e.replace(' ', '')
    reversed_e = []
    for c in e[::-1]:
        if c == '(':
            reversed_e.append(')')
        elif c == ')':
            reversed_e.append('(')
        else:
            reversed_e.append(c)
    reversed_e = ''.join(reversed_e)
    
    stack = []
    output = []
    i = 0
    n = len(reversed_e)
    
    while i < n:
        char = reversed_e[i]
        if char.isalpha():
            operand = [char]
            i += 1
            while i < n and reversed_e[i].isalpha():
                operand.append(reversed_e[i])
                i += 1
            output.append(''.join(reversed(operand)))
            continue    
        elif char == '(':
            stack.append(char)   
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  
        else:
            precedence = {'*':3, '/':3, '+':2, '-':2}
            while stack and stack[-1] != '(' and precedence[char] <= precedence.get(stack[-1], 0):
                output.append(stack.pop())
            stack.append(char)
            
        i += 1
    while stack:
        output.append(stack.pop())
    prefix = ' '.join(output[::-1])
    print(prefix)