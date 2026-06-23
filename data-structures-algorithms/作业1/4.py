#змейку-матрица
'''
rows = 3
cols = 4
tab = [[0]*cols for _ in range(rows)]
index = 0
for row in range(rows):
    if row % 2 == 0:
        for col in range(0, cols, +1):
            index += 1
            tab[row][col] = index
    else:
        for col in range(cols-1, -1,-1):
            index += 1
            tab[row][col] = index
for row in tab:
    print('\t'.join(map(str, row)))
'''
'''
rows = 3
cols = 4
tab = [[0]*cols for _ in range(rows)]
index = 0
for col in range(cols):
    if col % 2 == 0:
        for row in range(0, rows, +1):
            index += 1
            tab[row][col] = index
    else:
        for row in range(rows-1, -1,-1):
            index += 1
            tab[row][col] = index

for row in tab:
    print('\t'.join(map(str, row)))
'''

size = 3

tab = [[0]*size for _ in range(size)]

index = 0; x = -1; y = 1

while True:
    while y >0 and x<size-1:
        y-=1; x+=1
        index +=1; tab[y][x] = index
    if y == 0 and x<size-1:
        x+=1
    else:
        y+=1
    index +=1;tab[y][x] = index
    break

for line in tab:
    print(*line)