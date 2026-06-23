import time
import matplotlib.pyplot as plt

sizes = [10**2, 10**3, 10**4, 10**5, 10**6]
times = []
repeat = 10000 

for size in sizes:
    lst = list(range(size)) 
    index = size // 2 
    start = time.perf_counter() 
    for _ in range(repeat):
        _ = lst[index]
    end = time.perf_counter()
    avg_time = (end - start) / repeat
    times.append(avg_time)
plt.figure(figsize=(8, 5))
plt.plot(sizes, times, marker='o', linestyle='-', color='b')
plt.xscale('log')
plt.yscale('log')
plt.xlabel("List size (logarithmic scale)")
plt.ylabel("Average access time (seconds, logarithmic scale)")
plt.title("A1: Verification of time complexity of list[i] index access")
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("A1_list_index_time.png")
plt.show()