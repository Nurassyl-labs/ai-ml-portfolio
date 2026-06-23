def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_days_in_month(year, month):
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if month == 2 and is_leap_year(year):
        return 29
    return days_in_month[month - 1]

def get_start_day(year, month):
    total_days = 0
    for y in range(1900, year):
        total_days += 366 if is_leap_year(y) else 365
    for m in range(1, month):
        total_days += get_days_in_month(year, m)
    return (total_days + 1) % 7 

def print_calendar(year, month):
    days = get_days_in_month(year, month)
    start_day = get_start_day(year, month)
    
    print("Sun Mon Tue Wed Thu Fri Sat")
    print(" " * (start_day * 4), end="")
    
    for day in range(1, days + 1):
        print(f"{day:3} ", end="")
        if (start_day + day) % 7 == 0:
            print()
    print()

year, month = map(int, input().split())
print_calendar(year, month)
