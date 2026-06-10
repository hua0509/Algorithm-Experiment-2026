# 算法设计与分析 课程实验作业

**云南大学信息学院 · 2026年春季学期**

- **姓名**：刘兴华
- **学号**：20241120062
- **专业**：计算机科学与技术（2024级一班）
- **指导教师**：岳昆 / 吴鑫然

---

## 实验内容

### 实验一：排序算法
实现并对比 **冒泡排序、合并排序、快速排序** 在多种数据规模下的性能，分析输入等价类对比较次数的影响及子问题规模变化规律。

### 实验二：0-1背包问题
用 **蛮力法、动态规划法、贪心法、回溯法** 求解0-1背包问题，测试多容量（C=10,000 / 100,000 / 1,000,000）及大规模 n 下的表现。

---

## 项目结构

```
├── code/                           # 源代码
│   ├── 20241120062-刘兴华-代码.c      # C语言实现（排序+背包）
│   ├── generate_charts.py           # 图表生成脚本
│   ├── generate_excel.py            # 数据导出脚本
│   ├── generate_report.py           # 报告生成脚本
│   ├── knapsack_experiment.py       # 背包实验（Python版）
│   └── sorting_experiment.py        # 排序实验（Python版）
├── data/                           # 实验数据
│   └── 20241120062-刘兴华-数据.xlsx   # 完整实验数据表
├── charts/                         # 实验图表
│   ├── fig1_sorting_comparisons.png
│   ├── fig2_sorting_time.png
│   ├── fig3_knapsack_C10,000.png
│   ├── fig3_knapsack_C100,000.png
│   ├── fig4_greedy_all_capacities.png
│   ├── fig5_dp_all_capacities.png
│   └── fig6_value_comparison.png
└── report/                         # 实验报告
    └── 20241120062-刘兴华-实验报告.docx
```

## 运行环境

- 操作系统：Windows 11
- 编译器：GCC (MinGW-w64)
- Python：3.x（图表/数据处理）
- Excel：实验数据查看

## 编译与运行

```bash
# C语言版本（核心算法）
gcc -O2 code/20241120062-刘兴华-代码.c -o knapsack_sort
./knapsack_sort

# Python版本（实验数据采集）
python code/sorting_experiment.py
python code/knapsack_experiment.py
```

---

*提交日期：2026年6月10日*
