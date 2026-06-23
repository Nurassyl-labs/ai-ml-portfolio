def parse_polynomial(line):
    terms = list(map(int, line.split())) 
    polynomial = {} 
    for i in range(0, len(terms), 2):
        coeff = terms[i]
        exp = terms[i + 1] 
        if exp < 0:
            break
        polynomial[exp] = polynomial.get(exp, 0) + coeff

    return polynomial


def add_polynomials(poly1, poly2):
    result = poly1.copy()
    for exp, coeff in poly2.items():
        result[exp] = result.get(exp, 0) + coeff
    return {exp: coeff for exp, coeff in result.items() if coeff != 0}


def format_polynomial(polynomial):
    sorted_terms = sorted(polynomial.items(), key=lambda x: -x[0])
    return " ".join(f"[{coeff} {exp}]" for exp, coeff in sorted_terms)


def main():
    n = int(input().strip())
    results = [] 
    for _ in range(n):
        poly1 = parse_polynomial(input().strip())
        poly2 = parse_polynomial(input().strip())
        sum_poly = add_polynomials(poly1, poly2)
        results.append(format_polynomial(sum_poly))
    for res in results:
        print(res)
if __name__ == "__main__":
    main()