def gen_array(n, m):
    matrix = [[0] * m for _ in range(n)]
    num = 1
    for diagonal in range(n + m - 1):
        if diagonal < n:
            row = diagonal
            col = 0
        else:
            row = n - 1
            col = diagonal - n + 1
        while row >= 0 and col < m:
            if diagonal % 2 == 0: 
                matrix[row][col] = num
            else: 
                matrix[col][row] = num
            num += 1
            row -= 1
            col += 1
    return matrix

N = int(input()) 

arr = gen_array(N, N)
for row in arr:
    print(' '.join(map(str, row)))