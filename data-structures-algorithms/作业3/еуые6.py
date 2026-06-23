'''n = int(input())
results = []

for _ in range(n):
    n = int(input())
    candidate = None
    count = 0
    
    for _ in range(n):
        num = int(input())
        if count == 0:
            candidate = num
            count = 1
        elif num == candidate:
            count += 1
        else:
            count -= 1
    
    results.append(str(candidate))

print('\n'.join(results))
'''
for i in range(2):
    for j in range(3):
        print(f"{i}-{j}", end=" ")
    print()

c = 0
l = []
f = []

for i in range(1000,10000):

    b=str(i)
    for j in b:
        m = int(j)
        l.append(m)
        if len(l) == 4:
            k = sum(l)
            l = []
            if k == 20:
                b = int(b)
                f.append(b)
print(sum(f))