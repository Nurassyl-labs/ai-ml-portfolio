
k = int(input().strip())

queries = []
for _ in range(k):
    m, n = map(int, input().strip().split())
    queries.append((m, n))
for m, n in queries:
    result = [] 
    for num in range(m, n + 1):
        digits = list(map(int, str(num)))
        power = len(digits)
        if sum(d ** power for d in digits) == num:
            result.append(str(num))
    if result:
        print(" ".join(result))  
    else:
        print("NO") 