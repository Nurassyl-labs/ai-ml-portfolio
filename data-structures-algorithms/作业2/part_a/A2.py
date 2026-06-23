import time
import matplotlib.pyplot as plt
import random

sizes = [10**2, 10**3, 10**4, 10**5, 10**6]
get_times = []
set_times = []
repeat = 10000
for size in sizes:
    d = {i: i for i in range(size)} 
    key = random.randint(0, size - 1)
    start = time.perf_counter()
    for _ in range(repeat):
        _ = d[key]
    end = time.perf_counter()
    avg_get_time = (end - start) / repeat
    get_times.append(avg_get_time)
    start = time.perf_counter()
    for _ in range(repeat):
        d[key] = _
    end = time.perf_counter()
    avg_set_time = (end - start) / repeat
    set_times.append(avg_set_time)

plt.figure(figsize=(8, 5))
plt.plot(sizes, get_times, label='dict get (d[key])', marker='o', linestyle='-', color='b')
plt.plot(sizes, set_times, label='dict set (d[key] = val)', marker='s', linestyle='-', color='r')
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Dictionary scale (logarithmic scale)")
plt.ylabel("Average operation time (seconds, logarithmic scale)")
plt.title("A2: Verification of the time complexity of dict get/set operations")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("A2_dict_get_set_time.png")
plt.show()