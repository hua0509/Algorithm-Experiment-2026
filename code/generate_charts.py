# -*- coding: utf-8 -*-
"""
生成实验图表
- 排序算法比较次数对比折线图
- 0-1背包执行时间对比折线图
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = r'E:\算法设计与分析实验'
CHARTS_DIR = os.path.join(BASE_DIR, 'charts')
DATA_DIR = r'C:\Users\41529\WorkBuddy\2026-06-10-16-03-30\experiment_data'

os.makedirs(CHARTS_DIR, exist_ok=True)

# ==================== 加载数据 ====================
with open(os.path.join(DATA_DIR, 'sorting_results.json'), 'r', encoding='utf-8') as f:
    sorting_data = json.load(f)

with open(os.path.join(DATA_DIR, 'knapsack_results.json'), 'r', encoding='utf-8') as f:
    knapsack_data = json.load(f)


# ==================== 图1: 排序算法比较次数对比 ====================
def plot_sorting_comparisons():
    all_r = sorting_data['all_results']
    sizes = [10, 100, 1000, 2000, 5000, 10000, 100000]
    
    bubble_cmp = []
    merge_cmp = []
    quick_cmp = []
    
    for s in sizes:
        r = all_r[str(s)]
        bubble_cmp.append(r['bubble']['comparisons'])
        merge_cmp.append(r['merge']['comparisons'])
        quick_cmp.append(r['quick']['comparisons'])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 左图: 线性坐标
    ax1.plot(sizes, bubble_cmp, 'o-', color='#E74C3C', linewidth=2, markersize=6, label='Bubble Sort (O(n^2))')
    ax1.plot(sizes, merge_cmp, 's-', color='#2980B9', linewidth=2, markersize=6, label='Merge Sort (O(n log n))')
    ax1.plot(sizes, quick_cmp, '^--', color='#27AE60', linewidth=2, markersize=6, label='Quick Sort (O(n log n))')
    ax1.set_xlabel('Input Size n', fontsize=12)
    ax1.set_ylabel('Number of Comparisons', fontsize=12)
    ax1.set_title('Sorting Algorithm Comparison Count (Linear Scale)', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
    
    # 右图: 双对数坐标
    ax2.loglog(sizes, bubble_cmp, 'o-', color='#E74C3C', linewidth=2, markersize=6, label='Bubble Sort O(n^2)')
    ax2.loglog(sizes, merge_cmp, 's-', color='#2980B9', linewidth=2, markersize=6, label='Merge Sort O(n log n)')
    ax2.loglog(sizes, quick_cmp, '^--', color='#27AE60', linewidth=2, markersize=6, label='Quick Sort O(n log n)')
    
    # 理论参考线
    ref_x = np.array(sizes)
    # O(n^2) 参考线 (归一化)
    ref_n2 = ref_x ** 2 / ref_x[0] ** 2 * bubble_cmp[0]
    ax2.loglog(ref_x, ref_n2, ':', color='gray', linewidth=1, alpha=0.5, label='Theoretical O(n^2)')
    # O(n log n) 参考线
    ref_nlogn = ref_x * np.log2(ref_x) / (ref_x[0] * np.log2(ref_x[0])) * merge_cmp[0]
    ax2.loglog(ref_x, ref_nlogn, ':', color='gray', linewidth=1, alpha=0.5, label='Theoretical O(n log n)')
    
    ax2.set_xlabel('Input Size n (log scale)', fontsize=12)
    ax2.set_ylabel('Number of Comparisons (log scale)', fontsize=12)
    ax2.set_title('Sorting Algorithm Comparison Count (Log-Log Scale)', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3, which='both')
    
    plt.tight_layout()
    filepath = os.path.join(CHARTS_DIR, 'fig1_sorting_comparisons.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Figure 1 saved: {filepath}')


# ==================== 图2: 排序算法执行时间对比 ====================
def plot_sorting_time():
    all_r = sorting_data['all_results']
    sizes = [10, 100, 1000, 2000, 5000, 10000, 100000]
    
    bubble_time = []
    merge_time = []
    quick_time = []
    
    for s in sizes:
        r = all_r[str(s)]
        bt = r['bubble'].get('time_ms')
        bubble_time.append(bt if bt else None)
        merge_time.append(r['merge']['time_ms'])
        quick_time.append(r['quick']['time_ms'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sizes_plot = [s for s, t in zip(sizes, bubble_time) if t is not None]
    bt_plot = [t for t in bubble_time if t is not None]
    ax.plot(sizes_plot, bt_plot, 'o-', color='#E74C3C', linewidth=2, markersize=6, label='Bubble Sort')
    
    ax.plot(sizes, merge_time, 's-', color='#2980B9', linewidth=2, markersize=6, label='Merge Sort')
    ax.plot(sizes, quick_time, '^--', color='#27AE60', linewidth=2, markersize=6, label='Quick Sort')
    
    ax.set_xlabel('Input Size n', fontsize=12)
    ax.set_ylabel('Execution Time (ms)', fontsize=12)
    ax.set_title('Sorting Algorithm Execution Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filepath = os.path.join(CHARTS_DIR, 'fig2_sorting_time.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Figure 2 saved: {filepath}')


# ==================== 图3: 0-1背包执行时间对比 (C=10000) ====================
def plot_knapsack_time(capacity_str, capacity_label):
    cr = knapsack_data[capacity_str]
    item_counts = [int(n) for n in cr.keys()]
    item_counts.sort()
    
    dp_times = []
    greedy_times = []
    
    for n in item_counts:
        r = cr[str(n)]
        dp = r.get('dp', {})
        gd = r.get('greedy', {})
        
        dp_t = dp.get('execution_time_ms', None)
        if dp.get('note'):
            dp_t = None
        dp_times.append(dp_t)
        
        gd_t = gd.get('execution_time_ms', None)
        greedy_times.append(gd_t)
    
    # 过滤有效数据
    valid_dp = [(n, t) for n, t in zip(item_counts, dp_times) if t is not None]
    valid_gd = [(n, t) for n, t in zip(item_counts, greedy_times) if t is not None]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if valid_dp:
        n_dp, t_dp = zip(*valid_dp)
        ax.plot(n_dp, t_dp, 'o-', color='#2980B9', linewidth=2, markersize=5, label='Dynamic Programming O(n*C)')
    if valid_gd:
        n_gd, t_gd = zip(*valid_gd)
        ax.plot(n_gd, t_gd, 's-', color='#E67E22', linewidth=2, markersize=5, label='Greedy O(n log n)')
    
    ax.set_xlabel('Number of Items n', fontsize=12)
    ax.set_ylabel('Execution Time (ms)', fontsize=12)
    ax.set_title(f'0-1 Knapsack Execution Time (C={capacity_label})', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    
    plt.tight_layout()
    filepath = os.path.join(CHARTS_DIR, f'fig3_knapsack_C{capacity_label}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Figure 3 (C={capacity_label}) saved: {filepath}')


# ==================== 图4: 所有容量下贪心法执行时间 ====================
def plot_greedy_all_capacities():
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#E67E22', '#2980B9', '#27AE60']
    
    for cap_str, color in zip(['10000', '100000', '1000000'], colors):
        cr = knapsack_data[cap_str]
        item_counts = sorted([int(n) for n in cr.keys()])
        times = []
        for n in item_counts:
            gd = cr[str(n)].get('greedy', {})
            t = gd.get('execution_time_ms', 0)
            times.append(t)
        ax.plot(item_counts, times, 'o-', color=color, linewidth=2, markersize=4, 
                label=f'C={int(cap_str):,}', alpha=0.8)
    
    ax.set_xlabel('Number of Items n', fontsize=12)
    ax.set_ylabel('Execution Time (ms)', fontsize=12)
    ax.set_title('Greedy Algorithm Execution Time Across Capacities', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    
    plt.tight_layout()
    filepath = os.path.join(CHARTS_DIR, 'fig4_greedy_all_capacities.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Figure 4 saved: {filepath}')


# ==================== 图5: DP算法各容量执行时间 ====================
def plot_dp_all_capacities():
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['#E67E22', '#2980B9', '#27AE60']
    
    for cap_str, color in zip(['10000', '100000'], colors):
        cr = knapsack_data[cap_str]
        item_counts = sorted([int(n) for n in cr.keys()])
        
        valid_n = []
        valid_t = []
        for n in item_counts:
            dp = cr[str(n)].get('dp', {})
            t = dp.get('execution_time_ms', None)
            if t is not None and dp.get('total_value') is not None and not dp.get('note'):
                valid_n.append(n)
                valid_t.append(t)
        
        if valid_n:
            ax.plot(valid_n, valid_t, 'o-', color=color, linewidth=2, markersize=5, 
                    label=f'DP C={int(cap_str):,}', alpha=0.8)
    
    ax.set_xlabel('Number of Items n', fontsize=12)
    ax.set_ylabel('Execution Time (ms)', fontsize=12)
    ax.set_title('Dynamic Programming Execution Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filepath = os.path.join(CHARTS_DIR, 'fig5_dp_all_capacities.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Figure 5 saved: {filepath}')


# ==================== 图6: DP vs Greedy 最优值对比 (C=10000) ====================
def plot_value_comparison():
    cr = knapsack_data['10000']
    item_counts = sorted([int(n) for n in cr.keys()])
    
    dp_values = []
    greedy_values = []
    valid_n = []
    
    for n in item_counts:
        r = cr[str(n)]
        dp = r.get('dp', {})
        gd = r.get('greedy', {})
        if dp.get('total_value') is not None and gd.get('total_value') is not None:
            valid_n.append(n)
            dp_values.append(dp['total_value'])
            greedy_values.append(gd['total_value'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(valid_n, dp_values, 'o-', color='#2980B9', linewidth=2, markersize=5, label='DP (Optimal)')
    ax.plot(valid_n, greedy_values, 's-', color='#E67E22', linewidth=2, markersize=5, label='Greedy')
    
    ax.set_xlabel('Number of Items n', fontsize=12)
    ax.set_ylabel('Total Value', fontsize=12)
    ax.set_title('DP vs Greedy: Total Value Comparison (C=10,000)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    
    plt.tight_layout()
    filepath = os.path.join(CHARTS_DIR, 'fig6_value_comparison.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Figure 6 saved: {filepath}')


# ==================== 生成所有图表 ====================
if __name__ == '__main__':
    plot_sorting_comparisons()
    plot_sorting_time()
    plot_knapsack_time('10000', '10,000')
    plot_knapsack_time('100000', '100,000')
    plot_greedy_all_capacities()
    plot_dp_all_capacities()
    plot_value_comparison()
    print('\nAll charts generated successfully!')
