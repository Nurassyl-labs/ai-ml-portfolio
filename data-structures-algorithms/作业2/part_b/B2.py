import time
import random
import matplotlib.pyplot as plt

def merge_sort(numbers):
    if len(numbers) <= 1:
        return numbers
    middle = len(numbers)//2
    left = merge_sort(numbers[:middle])
    right = merge_sort(numbers[middle:])
    merged = []
    li = ri = 0
    while li < len(left) and ri < len(right):
        if left[li] <= right[ri]:
            merged.append(left[li])
            li += 1
        else:
            merged.append(right[ri])
            ri += 1
    merged.extend(left[li:] or right[ri:])
    return merged
def test_sort_time(sort_func, data_generator, sizes):
    times = []
    for size in sizes:
        data = data_generator(size)
        start = time.perf_counter()
        sort_func(data)
        end = time.perf_counter()
        times.append(end - start)
    return times

sizes = [2**i for i in range(8, 15)]
ms_avg = test_sort_time(merge_sort, lambda n: random.sample(range(n * 10), n), sizes)
ms_worst = test_sort_time(merge_sort, lambda n: list(range(n, 0, -1)), sizes)

plt.figure(figsize=(10, 6))
plt.plot(sizes, ms_avg, marker='o', label="Merge Sort Average Case")
plt.plot(sizes, ms_worst, marker='s', label="Merge sort worst case")
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Input scale")
plt.ylabel("Run time")
plt.title("B2: Merge sort time complexity verification")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("B2_merge_sort_time.png")
plt.show()