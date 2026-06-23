class People:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def getName(self):
        return self.name

    def getAge(self):
        return self.age

class Student(People):
    def __init__(self, sno, name, age):
        super().__init__(name, age)
        self.sno = sno

    def getSno(self):
        return self.sno

class Xdict(dict):
    def getKeys(self, value):
        return [k for k, v in self.items() if v == value]

N, M = map(int, input().split())

students_xdict = Xdict()

for _ in range(N):
    sno, name, age = input().split()
    s = Student(sno, name, age)
    print(f"{s.getSno()} {super(Student, s).getName()} {super(Student, s).getAge()}")
    students_xdict[sno] = name

for _ in range(M):
    query_name = input()
    results = students_xdict.getKeys(query_name)
    if len(results) == 0:
        print("None")
    else:
        print(" ".join(results))

