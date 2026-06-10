# -*- coding: utf-8 -*-
"""
算法设计与分析实验 - 排序算法部分
冒泡排序、合并排序(归并排序)、快速排序
记录比较操作次数、子问题规模
"""
import random
import time
import json
import sys
import os

# 设置递归深度
sys.setrecursionlimit(1000000)

# ===================== 全局计数器 =====================
class SortCounters:
    def __init__(self):
        self.comparisons = 0
        self.subproblem_sizes = []  # 记录每次递归调用的子问题规模

# ===================== 冒泡排序 =====================
def bubble_sort(arr):
    counter = SortCounters()
    n = len(arr)
    arr_copy = arr.copy()
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            counter.comparisons += 1
            if arr_copy[j] > arr_copy[j + 1]:
                arr_copy[j], arr_copy[j + 1] = arr_copy[j + 1], arr_copy[j]
                swapped = True
        if not swapped:
            break
    return counter

# ===================== 合并排序(归并排序) =====================
def merge_sort(arr):
    counter = SortCounters()
    arr_copy = arr.copy()
    _merge_sort_recursive(arr_copy, 0, len(arr_copy) - 1, counter)
    return counter

def _merge_sort_recursive(arr, left, right, counter):
    n = right - left + 1
    counter.subproblem_sizes.append(n)
    if left < right:
        mid = (left + right) // 2
        _merge_sort_recursive(arr, left, mid, counter)
        _merge_sort_recursive(arr, mid + 1, right, counter)
        _merge(arr, left, mid, right, counter)

def _merge(arr, left, mid, right, counter):
    n1 = mid - left + 1
    n2 = right - mid
    L = arr[left:left + n1]
    R = arr[mid + 1:mid + 1 + n2]
    i = j = 0
    k = left
    while i < n1 and j < n2:
        counter.comparisons += 1
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1
    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1

# ===================== 快速排序 =====================
def quick_sort(arr):
    counter = SortCounters()
    arr_copy = arr.copy()
    _quick_sort_recursive(arr_copy, 0, len(arr_copy) - 1, counter)
    return counter

def _quick_sort_recursive(arr, low, high, counter):
    n = high - low + 1
    counter.subproblem_sizes.append(n)
    if low < high:
        pi = _partition(arr, low, high, counter)
        _quick_sort_recursive(arr, low, pi - 1, counter)
        _quick_sort_recursive(arr, pi + 1, high, counter)

def _partition(arr, low, high, counter):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        counter.comparisons += 1
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# ===================== 主实验函数 =====================
def run_sorting_experiments():
    sizes = [10, 100, 1000, 2000, 5000, 10000, 100000]
    
    # 第一组: 100个数据做两次对比
    print("=" * 60)
    print("排序算法实验 - 开始")
    print("=" * 60)
    
    # 两次100个数据的对比实验
    print("\n--- 100个数据对比实验（两次） ---")
    comparison_100 = []
    for trial in range(2):
        random.seed(42 + trial * 1000)
        data = [random.randint(1, 10000) for _ in range(100)]
        results = {}
        results['data'] = data[:20]  # 只保存前20个作为示例
        results['data_summary'] = f"100个随机整数(1-10000), seed={42 + trial * 1000}"
        
        # 冒泡排序
        c = bubble_sort(data)
        results['bubble'] = {'comparisons': c.comparisons}
        
        # 合并排序
        c = merge_sort(data)
        results['merge'] = {'comparisons': c.comparisons}
        
        # 快速排序
        c = quick_sort(data)
        results['quick'] = {'comparisons': c.comparisons}
        
        comparison_100.append(results)
        print(f"  第{trial+1}次: 冒泡={results['bubble']['comparisons']}, "
              f"合并={results['merge']['comparisons']}, "
              f"快速={results['quick']['comparisons']}")
    
    # 不同规模实验
    print("\n--- 不同规模测试 ---")
    all_sort_results = {}
    
    BUBBLE_MAX_SIZE = 10000  # 冒泡排序最大测试规模
    
    for size in sizes:
        print(f"\n  规模 {size}: ", end="", flush=True)
        random.seed(42)
        data = [random.randint(1, 1000000) for _ in range(size)]
        
        result = {}
        result['size'] = size
        
        # 冒泡排序（仅对小规模测试）
        if size <= BUBBLE_MAX_SIZE:
            t0 = time.time()
            c = bubble_sort(data)
            t_bubble = (time.time() - t0) * 1000
            result['bubble'] = {
                'comparisons': c.comparisons,
                'time_ms': round(t_bubble, 4)
            }
            print(f"冒泡={c.comparisons}({t_bubble:.1f}ms) ", end="", flush=True)
        else:
            est_comparisons = size * (size - 1) // 2
            result['bubble'] = {
                'comparisons': est_comparisons,
                'time_ms': None,
                'note': f'规模过大，比较次数为理论值 n(n-1)/2 = {est_comparisons}'
            }
            print(f"冒泡=理论{est_comparisons}(跳过) ", end="", flush=True)
        
        # 合并排序
        t0 = time.time()
        c = merge_sort(data)
        t_merge = (time.time() - t0) * 1000
        result['merge'] = {
            'comparisons': c.comparisons,
            'time_ms': round(t_merge, 4),
            'subproblem_sizes_summary': _summarize_subproblems(c.subproblem_sizes)
        }
        print(f"合并={c.comparisons}({t_merge:.1f}ms) ", end="", flush=True)
        
        # 快速排序
        t0 = time.time()
        c = quick_sort(data)
        t_quick = (time.time() - t0) * 1000
        result['quick'] = {
            'comparisons': c.comparisons,
            'time_ms': round(t_quick, 4),
            'subproblem_sizes_summary': _summarize_subproblems(c.subproblem_sizes)
        }
        print(f"快速={c.comparisons}({t_quick:.1f}ms)", flush=True)
        
        all_sort_results[str(size)] = result
    
    return {
        'comparison_100': comparison_100,
        'all_results': all_sort_results
    }

def _summarize_subproblems(sizes_list):
    """汇总子问题规模信息"""
    if not sizes_list:
        return {}
    sizes_list = [s for s in sizes_list if s > 0]
    if not sizes_list:
        return {}
    return {
        'total_calls': len(sizes_list),
        'min_size': min(sizes_list),
        'max_size': max(sizes_list),
        'avg_size': round(sum(sizes_list) / len(sizes_list), 2),
        'leaf_calls': sum(1 for s in sizes_list if s <= 1),
        'size_distribution': _count_distribution(sizes_list)
    }

def _count_distribution(sizes_list):
    """统计子问题规模分布（前10个最大的和前10个最小的）"""
    sorted_sizes = sorted(set(sizes_list))
    return {
        'unique_sizes': len(sorted_sizes),
        'smallest_10': sorted_sizes[:10] if len(sorted_sizes) > 10 else sorted_sizes,
        'largest_10': sorted_sizes[-10:] if len(sorted_sizes) > 10 else sorted_sizes
    }

if __name__ == '__main__':
    results = run_sorting_experiments()
    
    # 保存结果
    output_dir = r'C:\Users\41529\WorkBuddy\2026-06-10-16-03-30\experiment_data'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'sorting_results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_dir}/sorting_results.json")
    
    # 打印汇总表
    print("\n" + "=" * 80)
    print("排序算法比较操作次数汇总")
    print("=" * 80)
    print(f"{'规模':>10} {'冒泡比较次数':>15} {'合并比较次数':>15} {'快速比较次数':>15}")
    print("-" * 60)
    for size, r in results['all_results'].items():
        print(f"{int(size):>10} {r['bubble']['comparisons']:>15} "
              f"{r['merge']['comparisons']:>15} {r['quick']['comparisons']:>15}")
