import time
import matplotlib.pyplot as plt
sizes = [10**2, 10**3, 10**4, 10**5]
repeat = 100
list_del_times = []
dict_del_times = []
for size in sizes:
    total_list_time = 0
    for _ in range(repeat):
        lst = list(range(size))
        index = size//2
        start = time.perf_counter()
        lst.pop(index)
        end = time.perf_counter()
        total_list_time += (end - start)
    avg_list_del_time = total_list_time / repeat
    list_del_times.append(avg_list_del_time)
    dct = {i: i for i in range(size)}
    keys_to_delete = list(dct.keys())[:repeat]
    start = time.perf_counter()
    for k in keys_to_delete:
        del dct[k]
    end = time.perf_counter()
    avg_dict_del_time = (end - start) / repeat
    dict_del_times.append(avg_dict_del_time)

plt.figure(figsize=(8, 5))
plt.plot(sizes, list_del_times, label='list delete the middle element', marker='o', linestyle='-', color='b')
plt.plot(sizes, dict_del_times, label='dict delete key', marker='s', linestyle='-', color='r')
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Data scale (logarithmic scale)")
plt.ylabel("Average deletion time (seconds, logarithmic scale)")
plt.title("A3: Comparison of list vs dict deletion performance")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("A3_list_low.png")
plt.show()