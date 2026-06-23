import time
import random

def my_binary_search(nums, target, left, right):
    """
    简单递归二分查找（不切片）。
    如果列表很长，递归层数会很深，可能会触发 RecursionError。
    """
    #如果范围无效，就返回-1
    if left > right:
        return -1

    mid = (left + right) // 2
    #找到了
    if nums[mid] == target:
        return mid
    #目标在右半部分
    if nums[mid] < target:
        return my_binary_search(nums, target, mid + 1, right)
    #目标在左半部分
    return my_binary_search(nums, target, left, mid - 1)


def slice_binary_search(nums, target):
    """
    用切片实现的递归二分，直观但性能不好。
    这里演示一下思路：切片会产生新列表，浪费空间和时间。
    """
    if not nums:
        return -1

    mid = len(nums) // 2
    if nums[mid] == target:
        return mid

    if nums[mid] < target:
        #记得：切片后的索引要加上 mid + 1
        idx_in_sub = slice_binary_search(nums[mid + 1 :], target)
        if idx_in_sub < 0:
            return -1
        return mid + 1 + idx_in_sub

    #如果nums[mid]>target，就在左边找
    return slice_binary_search(nums[:mid], target)


def quicksort_inplace(arr):
    """
    原地快速排序(Hoare 分区法)，稍微改自常见模板。
    这个版本会修改传入的列表，返回值也指向同一个列表。
    """
    def _partition(lo, hi):
        pivot = arr[(lo + hi) // 2]  #取中间位置作为pivot
        i, j = lo, hi
        #这里用while+双指针的Hoare分区
        while True:
            while arr[i] < pivot:
                i += 1
            while arr[j] > pivot:
                j -= 1
            if i >= j:
                return j
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
            j -= 1

    def _quicksort(lo, hi):
        if lo < hi:
            p = _partition(lo, hi)
            _quicksort(lo, p)
            _quicksort(p + 1, hi)

    _quicksort(0, len(arr) - 1)
    return arr  #返回排序后的列表（与传入对象同一个）


if __name__ == "__main__":
    #测试一下小规模数据
    sample = list(range(20))
    target_value = 13
    print("原始列表：", sample)
    idx1 = my_binary_search(sample, target_value, 0, len(sample) - 1)
    print(f"my_binary_search 查找 {target_value} 的索引 → {idx1}")

    idx2 = slice_binary_search(sample, target_value)
    print(f"slice_binary_search 查找 {target_value} 的索引 → {idx2}\n")

    #随机生成一个 10 个元素的乱序列表，试试快速排序
    rnd_list = [random.randint(0, 100) for _ in range(10)]
    print("乱序列表：", rnd_list)
    sorted_list = quicksort_inplace(rnd_list.copy())
    print("quicksort_inplace 排序后：", sorted_list)

    #性能对比：二分查找在大规模列表上
    big_list = list(range(100_000))
    big_target = 99_999

    t_start = time.time()
    res1 = my_binary_search(big_list, big_target, 0, len(big_list) - 1)
    t1 = time.time() - t_start

    t_start = time.time()
    res2 = slice_binary_search(big_list, big_target)
    t2 = time.time() - t_start

    print(f"\n大规模测试 (长度={len(big_list)})")
    print(f"my_binary_search 耗时：{t1:.6f} 秒")
    print(f"slice_binary_search 耗时：{t2:.6f} 秒")

#再测一次快速排序的时间（以防生成的 rnd_list 被修改）
    rnd_large = random.sample(range(1_000_000), 20_000)
    t_start = time.time()
    quicksort_inplace(rnd_large)
    t3 = time.time() - t_start
    print(f"\nquicksort_inplace 对 20_000 个随机数排序耗时：{t3:.6f} 秒")
