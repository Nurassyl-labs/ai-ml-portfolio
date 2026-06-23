

n = int(input())

for _ in range(n):
    string, text = input().split()
    text = int(text)
    length = len(string)
    text = text % length
    if text < 0:
        text = length + text
    
    result = string[-text:] + string[:-text]
    
    print(result)