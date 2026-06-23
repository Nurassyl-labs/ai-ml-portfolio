import time
import random
import matplotlib.pyplot as plt

def quick_sort(arr):
    stack = [(0, len(arr) - 1)]
    while stack:
        start, end = stack.pop()
        if start >= end:
            continue
        pivot = arr[start]
        low, high = start, end
        while low < high:
            while low < high and arr[high] >= pivot:
                high -= 1
            arr[low] = arr[high]
            while low < high and arr[low] <= pivot:
                low += 1
            arr[high] = arr[low]
        arr[high] = pivot
        stack.append((start, low - 1))
        stack.append((low + 1, end))

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
qs_avg = test_sort_time(quick_sort, lambda n: random.sample(range(n * 10), n), sizes)
qs_worst = test_sort_time(quick_sort, lambda n: list(range(n, 0, -1)), sizes)

plt.figure(figsize=(10, 6))
plt.plot(sizes, qs_avg, marker='o', label="Quick sort average case")
plt.plot(sizes, qs_worst, marker='s', label="Quick sort worst case")
plt.xscale('log')
plt.yscale('log')
plt.xlabel("Input scale")
plt.ylabel("Run time")
plt.title("B1: Quick sort time complexity verification")
plt.legend()
plt.grid(True, which="both", ls="--")
plt.tight_layout()
plt.savefig("B1_quick_sort_time.png")
plt.show()