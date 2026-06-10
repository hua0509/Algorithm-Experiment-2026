# -*- coding: utf-8 -*-
"""
算法设计与分析实验 - 0-1背包问题
蛮力法、动态规划法、贪心法、回溯法
"""
import random
import time
import json
import sys
import os
from itertools import combinations

sys.setrecursionlimit(1000000)

# ===================== 蛮力法 =====================
def knapsack_bruteforce(weights, values, capacity):
    """蛮力法：枚举所有子集"""
    n = len(weights)
    best_value = 0.0
    best_subset = []
    
    # 对于较大的n，蛮力法不可行
    if n > 30:
        return None, None, "N/A (n > 30, brute force infeasible)"
    
    # 使用位运算枚举所有子集
    for mask in range(1, 1 << n):
        total_weight = 0
        total_value = 0.0
        subset = []
        for i in range(n):
            if mask & (1 << i):
                total_weight += weights[i]
                total_value += values[i]
                subset.append(i)
                if total_weight > capacity:
                    break
        if total_weight <= capacity and total_value > best_value:
            best_value = total_value
            best_subset = subset.copy()
    
    return best_subset, best_value, len(best_subset)

# ===================== 动态规划法 =====================
def knapsack_dp(weights, values, capacity):
    """动态规划法：O(n*C)时间，O(C)空间"""
    n = len(weights)
    # 使用一维DP数组优化空间
    dp = [0.0] * (capacity + 1)
    # 记录选择情况
    choice = [[False] * (capacity + 1) for _ in range(n)]
    
    for i in range(n):
        w = weights[i]
        v = values[i]
        for j in range(capacity, w - 1, -1):
            if dp[j - w] + v > dp[j]:
                dp[j] = dp[j - w] + v
                choice[i][j] = True
    
    # 回溯找出选择的物品
    best_value = dp[capacity]
    selected = []
    j = capacity
    for i in range(n - 1, -1, -1):
        if choice[i][j]:
            selected.append(i)
            j -= weights[i]
    selected.reverse()
    
    return selected, best_value, len(selected)

# ===================== 贪心法 =====================
def knapsack_greedy(weights, values, capacity):
    """贪心法：按价值/重量比排序选择"""
    n = len(weights)
    items = [(i, weights[i], values[i], values[i] / weights[i]) for i in range(n)]
    # 按单位价值降序排序
    items.sort(key=lambda x: x[3], reverse=True)
    
    selected = []
    total_weight = 0
    total_value = 0.0
    
    for idx, w, v, ratio in items:
        if total_weight + w <= capacity:
            selected.append(idx)
            total_weight += w
            total_value += v
    
    selected.sort()
    return selected, total_value, len(selected)

# ===================== 回溯法 =====================
def knapsack_backtracking(weights, values, capacity):
    """回溯法：深度优先搜索 + 剪枝"""
    n = len(weights)
    
    # 按单位价值排序，便于剪枝
    items = [(weights[i], values[i], i) for i in range(n)]
    items.sort(key=lambda x: x[1] / x[0], reverse=True)
    sorted_w = [x[0] for x in items]
    sorted_v = [x[1] for x in items]
    
    best_value = 0.0
    best_subset = []
    current_subset = []
    current_weight = 0
    current_value = 0.0
    
    # 预处理：计算从i到n-1的累积价值上界（用于剪枝）
    max_remaining = [0.0] * (n + 1)
    # 用分数背包的上界
    for i in range(n - 1, -1, -1):
        max_remaining[i] = max_remaining[i + 1] + sorted_v[i]
    
    def backtrack(i):
        nonlocal best_value, best_subset
        if i == n:
            if current_value > best_value:
                best_value = current_value
                best_subset = current_subset.copy()
            return
        
        # 剪枝：即使把剩余所有物品都装入也不超过当前最优
        if current_value + max_remaining[i] <= best_value:
            return
        
        w, v, orig_idx = items[i]
        
        # 选择当前物品
        if current_weight + w <= capacity:
            current_subset.append(orig_idx)
            current_weight += w
            current_value += v
            backtrack(i + 1)
            current_subset.pop()
            current_weight -= w
            current_value -= v
        
        # 不选当前物品
        backtrack(i + 1)
    
    # 如果物品数量过大，回溯法不可行
    if n > 100:
        return None, None, f"N/A (n={n} too large for backtracking)"
    
    backtrack(0)
    best_subset.sort()
    return best_subset, best_value, len(best_subset)


# ===================== 生成测试数据 =====================
def generate_knapsack_data(n, seed=42):
    """生成0-1背包测试数据"""
    random.seed(seed + n)  # 不同n使用不同seed保证数据独立性
    weights = [random.randint(1, 100) for _ in range(n)]
    values = [round(random.uniform(100, 1000), 2) for _ in range(n)]
    return weights, values


# ===================== 主实验函数 =====================
def run_knapsack_experiments():
    # 物品数量（修正40000->4000，保留40000作为大规模测试）
    item_counts = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 
                   10000, 20000, 40000, 80000, 160000, 320000]
    capacities = [10000, 100000, 1000000]
    
    algorithms = {
        'bruteforce': ('蛮力法', knapsack_bruteforce),
        'dp': ('动态规划法', knapsack_dp),
        'greedy': ('贪心法', knapsack_greedy),
        'backtracking': ('回溯法', knapsack_backtracking)
    }
    
    # 为每种算法设置合理的时间上限
    MAX_TIME_SECONDS = 300  # 5分钟
    
    all_results = {}
    
    # 先生成所有数据（确保可复现）
    all_data = {}
    for n in item_counts:
        w, v = generate_knapsack_data(n)
        all_data[n] = (w, v)
    
    for cap in capacities:
        print(f"\n{'=' * 80}")
        print(f"背包容量 C = {cap}")
        print(f"{'=' * 80}")
        cap_results = {}
        
        for n in item_counts:
            print(f"\n  物品数量 n = {n}:")
            weights, values = all_data[n]
            n_results = {}
            
            for algo_name, (algo_cn, algo_func) in algorithms.items():
                # 合理的时间限制判断
                skip = False
                reason = ""
                
                if algo_name == 'bruteforce' and n > 25:
                    reason = f"蛮力法O(2^n)对n={n}不可行"
                    skip = True
                elif algo_name == 'backtracking' and n > 100:
                    reason = f"回溯法对n={n}过大"
                    skip = True
                elif algo_name == 'dp' and n * cap > 500000000:
                    # DP: n*C > 5亿次操作可能太慢
                    # 但尝试看看
                    pass
                
                t0 = time.time()
                
                if skip:
                    selected, total_value, count = None, None, reason
                    elapsed_ms = 0
                else:
                    try:
                        selected, total_value, count = algo_func(weights, values, cap)
                        elapsed_ms = round((time.time() - t0) * 1000, 2)
                        
                        if elapsed_ms > MAX_TIME_SECONDS * 1000:
                            selected, total_value, count = None, None, f"超时(>{MAX_TIME_SECONDS}s)"
                            elapsed_ms = MAX_TIME_SECONDS * 1000
                    except Exception as e:
                        selected, total_value, count = None, None, f"错误: {str(e)}"
                        elapsed_ms = round((time.time() - t0) * 1000, 2)
                
                n_results[algo_name] = {
                    'algorithm': algo_cn,
                    'execution_time_ms': elapsed_ms,
                    'total_value': total_value,
                    'selected_count': count if isinstance(count, int) else 0,
                    'selected_items': selected[:20] if isinstance(selected, list) and len(selected) > 20 else selected,
                    'note': count if isinstance(count, str) else ''
                }
                
                status = f"耗时={elapsed_ms}ms, 总价值={total_value}, 物品数={count}" if not skip else reason
                print(f"    {algo_cn}: {status}")
            
            cap_results[str(n)] = n_results
        
        all_results[str(cap)] = cap_results
    
    return all_results


def print_summary_table(all_results):
    """打印0-1背包实验结果汇总表"""
    capacities = [10000, 100000, 1000000]
    item_counts = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 
                   10000, 20000, 40000, 80000, 160000, 320000]
    
    print("\n\n" + "=" * 100)
    print("0-1背包实验结果汇总 - 执行时间(ms)")
    print("=" * 100)
    
    for cap in capacities:
        print(f"\n--- 背包容量 C = {cap} ---")
        header = f"{'n':>8}"
        for algo in ['dp', 'greedy', 'backtracking', 'bruteforce']:
            header += f" {'DP':>12} {'贪心':>12} {'回溯':>12} {'蛮力':>12}"
        print(header)
        print("-" * 70)
        
        for n in item_counts:
            row = f"{n:>8}"
            for algo in ['dp', 'greedy', 'backtracking', 'bruteforce']:
                if str(cap) in all_results and str(n) in all_results[str(cap)]:
                    r = all_results[str(cap)][str(n)].get(algo, {})
                    t = r.get('execution_time_ms', 0)
                    note = r.get('note', '')
                    if note:
                        row += f" {str(note)[:12]:>12}"
                    else:
                        row += f" {t:>12.1f}"
                else:
                    row += f" {'N/A':>12}"
            print(row)


if __name__ == '__main__':
    results = run_knapsack_experiments()
    
    # 保存结果
    output_dir = r'C:\Users\41529\WorkBuddy\2026-06-10-16-03-30\experiment_data'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'knapsack_results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_dir}/knapsack_results.json")
    print_summary_table(results)
