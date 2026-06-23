k = int(input().strip())
results = []

for _ in range(k):
    n = int(input().strip())
    total = 0
    fact = 1
    for i in range(1, n + 1):
        fact *= i
        total += fact
    results.append(str(total))

print("\n".join(results))