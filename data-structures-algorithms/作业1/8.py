def is_narcissistic(num):
    digits = list(map(int, str(num)))
    power = len(digits)
    return sum(d ** power for d in digits) == num

def find_narcissistic_numbers(m, n):
    result = [str(num) for num in range(m, n + 1) if is_narcissistic(num)]
    return " ".join(result) if result else "NO"

k = int(input().strip())
queries = [tuple(map(int, input().strip().split())) for _ in range(k)]

for m, n in queries:
    print(find_narcissistic_numbers(m, n))
