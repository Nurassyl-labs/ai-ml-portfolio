n = int(input())
p = []

for i in range(n):
    row = [1] * (i + 1)  # Создаем строку с единицами
    for j in range(i + 1):
        if j != 0 and j != i:  # Если это не первый и не последний элемент
            row[j] = p[i - 1][j - 1] + p[i - 1][j]  # Заполняем сумму
    p.append(row)

# Выводим строки, разделяя числа пробелами
for r in p:
    print(" ".join(map(str, r)))