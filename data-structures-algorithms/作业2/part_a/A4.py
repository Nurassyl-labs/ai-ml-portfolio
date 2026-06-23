import time
import matplotlib.pyplot as plt
import random
sizes = [10**2, 10**3, 10**4, 10**5, 10**6]
insert_times = []
lookup_times = []
for size in sizes:
    data = random.sample(range(size * 2), size)
    s = set() 
    start = time.perf_counter()
    for val in data:
        s.add(val)
    end = time.perf_counter()
    avg_insert_time = (end - start) / size
    insert_times.append(avg_insert_time)
    start = time.perf_counter()
    for val in data:
        _ = val in s
    end = time.perf_counter()
    avg_lookup_time = (end - start) / size
    lookup_times.append(avg_lookup_time)
plt.figure(figsize=(8, 5))
plt.plot(sizes, insert_times, label='set add', marker='o', linestyle='-', color='b')
plt.plot(sizes, lookup_times, label='set in', marker='s', linestyle='-', color='r')
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Collection size (logarithmic scale)")
plt.ylabel("Average operation time (seconds, logarithmic scale)")
plt.title("A4: Verification of the time complexity of set insertion and search operations")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("A4_set_insert_lookup_time.png")
plt.show()