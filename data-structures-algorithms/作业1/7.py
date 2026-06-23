def parse_polynomial(line):
    """
    Преобразует строку с коэффициентами и степенями в словарь, где ключ — степень, значение — коэффициент.
    """
    terms = list(map(int, line.split()))  # Разбиваем строку на числа
    polynomial = {}  # Словарь для хранения полинома

    # Обрабатываем пары (коэффициент, степень)
    for i in range(0, len(terms), 2):
        coeff = terms[i]      # Коэффициент
        exp = terms[i + 1]    # Степень

        # Если степень отрицательная, прекращаем обработку
        if exp < 0:
            break

        # Добавляем коэффициент к соответствующей степени
        polynomial[exp] = polynomial.get(exp, 0) + coeff

    return polynomial


def add_polynomials(poly1, poly2):
    """
    Складывает два полинома и возвращает результат.
    """
    result = poly1.copy()  # Копируем первый полином, чтобы не изменять оригинал

    # Добавляем коэффициенты второго полинома
    for exp, coeff in poly2.items():
        result[exp] = result.get(exp, 0) + coeff

    # Убираем нулевые коэффициенты
    return {exp: coeff for exp, coeff in result.items() if coeff != 0}


def format_polynomial(polynomial):
    """
    Форматирует полином в строку вида "[coeff exp] [coeff exp] ...".
    """
    # Сортируем степени по убыванию
    sorted_terms = sorted(polynomial.items(), key=lambda x: -x[0])

    # Форматируем каждый член полинома
    return " ".join(f"[{coeff} {exp}]" for exp, coeff in sorted_terms)


def main():
    """
    Основная функция программы.
    """
    n = int(input().strip())  # Количество тестов
    results = []  # Список для хранения результатов

    for _ in range(n):
        # Читаем и парсим первый полином
        poly1 = parse_polynomial(input().strip())
        # Читаем и парсим второй полином
        poly2 = parse_polynomial(input().strip())
        # Складываем полиномы
        sum_poly = add_polynomials(poly1, poly2)
        # Форматируем результат и добавляем в список
        results.append(format_polynomial(sum_poly))

    # Выводим результаты
    for res in results:
        print(res)


if __name__ == "__main__":
    main()