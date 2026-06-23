    
word_to_digit = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9"
}
def convert_to_number(s):
    words = s.split("-") 
    digits = [word_to_digit[word] for word in words]
    return int("".join(digits))

a = int(input())
for _ in range(a):
    s = input().strip()
    print(convert_to_number(s))


