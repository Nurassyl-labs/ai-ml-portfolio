def gen_array(n, m):
    matrix = [[0]*m for _ in range(n)]
    num = 1
    for k in range(n + m):
        for j in range(min(k, m - 1), -1, -1):
            i = k - j
            if i < n:
                matrix[i][j] = num 
                num += 1
    return matrix
 
a,b = map(int, input().split())
arr = gen_array(a, b)
for row in arr:
    print(''.join([f'{elem:3d}' for elem in row]))

