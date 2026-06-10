/*
 * 0-1 背包问题 —— 四种算法实现
 * 学号: 20241120062
 * 姓名: 刘兴华
 * 
 * 算法列表:
 *   1. 蛮力法 (Brute Force)        —— 枚举所有子集，O(2^n)
 *   2. 动态规划法 (Dynamic Programming) —— O(n*C)，一维数组空间优化
 *   3. 贪心法 (Greedy)              —— 按价值/重量比排序，O(n log n)
 *   4. 回溯法 (Backtracking)        —— DFS + 上界剪枝，O(2^n) 最坏
 *
 * 测试用例: 容量=10, 重量=[2,2,6,5,4], 价值=[6,3,5,4,6]
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

/* ========================== 数据结构 ========================== */

/* 用于贪心法和回溯法中排序的物品结构体 */
typedef struct {
    int   index;   /* 原始编号 (1-based) */
    int   weight;
    double value;
    double ratio;  /* value / weight */
} Item;

/* ========================== 辅助函数 ========================== */

/*
 * 按价值/重量比从大到小排序 (供 qsort 使用)
 * 如果比值相等，按价值从大到小排
 */
int cmp_by_ratio(const void *a, const void *b) {
    const Item *ia = (const Item *)a;
    const Item *ib = (const Item *)b;
    if (ia->ratio > ib->ratio) return -1;
    if (ia->ratio < ib->ratio) return 1;
    /* 比值相同，价值高的优先 */
    if (ia->value > ib->value) return -1;
    if (ia->value < ib->value) return 1;
    return 0;
}

/*
 * 打印算法结果
 * name      - 算法名称 (中文)
 * n         - 物品总数
 * selected  - 长度为 n 的数组，selected[i]==1 表示选中
 * total_w   - 选中物品的总重量
 * total_v   - 选中物品的总价值
 * time_ms   - 运行时间 (毫秒)
 */
void print_result(const char *name, int n,
                  const int selected[], int total_w,
                  double total_v, double time_ms) {
    printf("========================================\n");
    printf("【%s】\n", name);
    printf("----------------------------------------\n");
    printf("选中的物品编号: ");
    int first = 1;
    for (int i = 0; i < n; i++) {
        if (selected[i]) {
            if (!first) printf(", ");
            printf("物品%d", i + 1);
            first = 0;
        }
    }
    if (first) printf("(无)");
    printf("\n");
    printf("总重量: %d\n", total_w);
    printf("总价值: %.2f\n", total_v);
    printf("运行时间: %.4f ms\n", time_ms);
    printf("========================================\n\n");
}

/* ========================== 1. 蛮力法 ========================== */

/*
 * 蛮力法 (Brute Force) 求解 0-1 背包问题
 *
 * 原理:
 *   枚举所有 2^n 个物品子集，检查每个子集的总重量是否不超过容量，
 *   在满足约束的子集中选出总价值最大的。
 *
 * 时间复杂度: O(n * 2^n)
 *   - 共 2^n 个子集
 *   - 每个子集需要 O(n) 时间累加重量和价值
 * 空间复杂度: O(n)
 *   - 仅需存储物品数据和最优解标记
 *
 * 仅适用于 n <= 20 左右的小规模问题。
 */
void brute_force(int n, int capacity, const int weights[],
                 const double values[],
                 int *best_selected, double *best_value,
                 int *best_weight) {
    int total       = 1 << n;          /* 子集总数 = 2^n */
    *best_value     = 0.0;
    *best_weight    = 0;
    memset(best_selected, 0, n * sizeof(int));

    for (int mask = 0; mask < total; mask++) {
        int    cur_weight = 0;
        double cur_value  = 0.0;

        /* 遍历每一位，若第 i 位为 1 则选取物品 i */
        for (int i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                cur_weight += weights[i];
                cur_value  += values[i];
                /* 提前剪枝：超重直接跳出 */
                if (cur_weight > capacity) break;
            }
        }

        /* 满足容量约束且价值更优则更新 */
        if (cur_weight <= capacity && cur_value > *best_value) {
            *best_value  = cur_value;
            *best_weight = cur_weight;
            for (int i = 0; i < n; i++) {
                best_selected[i] = (mask >> i) & 1;
            }
        }
    }
}

/* ========================== 2. 动态规划法 ========================== */

/*
 * 动态规划法 (Dynamic Programming) 求解 0-1 背包问题
 *
 * 原理:
 *   定义 dp[j] 表示容量为 j 时能获得的最大价值。
 *   状态转移方程: dp[j] = max(dp[j], dp[j - w[i]] + v[i])
 *   使用一维数组空间优化：内层循环从 capacity 向 w[i] 方向倒序计算，
 *   保证每个物品最多被使用一次。
 *
 * 时间复杂度: O(n * C)  —— C 为背包容量
 * 空间复杂度: O(n * C)  —— 使用 choice[][] 记录选择路径以回溯方案
 *   (纯粹一维 dp 数组本身仅需 O(C) 空间)
 *
 * 适用于容量与物品数量均适中的场景。
 */
void dynamic_programming(int n, int capacity, const int weights[],
                         const double values[],
                         int *selected, double *best_value,
                         int *best_weight) {
    /* dp[j] = 容量 j 的最优价值 */
    double *dp = (double *)calloc(capacity + 1, sizeof(double));

    /*
     * choice[i][j] = 1 表示在处理物品 i 时，容量 j 的最优解包含了物品 i
     * 用于最终回溯具体选择了哪些物品
     */
    int **choice = (int **)malloc(n * sizeof(int *));
    for (int i = 0; i < n; i++) {
        choice[i] = (int *)calloc(capacity + 1, sizeof(int));
    }

    /* 一维 DP 核心循环 (空间优化) */
    for (int i = 0; i < n; i++) {
        int    wi = weights[i];
        double vi = values[i];
        /* 从大到小倒序遍历，确保每个物品只用一次 */
        for (int j = capacity; j >= wi; j--) {
            double new_val = dp[j - wi] + vi;
            if (new_val > dp[j]) {
                dp[j]       = new_val;
                choice[i][j] = 1;
            }
        }
    }

    *best_value = dp[capacity];

    /* 回溯最优方案: 从最后一个物品逆推 */
    memset(selected, 0, n * sizeof(int));
    *best_weight = 0;
    int j = capacity;
    for (int i = n - 1; i >= 0; i--) {
        if (choice[i][j]) {
            selected[i]   = 1;
            *best_weight += weights[i];
            j            -= weights[i];
        }
    }

    /* 释放内存 */
    for (int i = 0; i < n; i++) free(choice[i]);
    free(choice);
    free(dp);
}

/* ========================== 3. 贪心法 ========================== */

/*
 * 贪心法 (Greedy) 求解 0-1 背包问题
 *
 * 原理:
 *   将所有物品按价值/重量比 (单位重量的价值) 从大到小排序，
 *   依次尝试装入每一个物品：如果当前物品不超容量则装入，否则跳过。
 *
 * 时间复杂度: O(n log n)  —— 主要花在排序上
 * 空间复杂度: O(n)
 *
 * 注意:
 *   贪心法在 0-1 背包问题中不一定能得到最优解，仅提供近似解。
 *   但在部分背包问题 (物品可分割) 中是最优的。
 */
void greedy(int n, int capacity, const int weights[],
            const double values[],
            int *selected, double *best_value, int *best_weight) {
    /* 构建物品数组并计算比值 */
    Item *items = (Item *)malloc(n * sizeof(Item));
    for (int i = 0; i < n; i++) {
        items[i].index  = i;
        items[i].weight = weights[i];
        items[i].value  = values[i];
        items[i].ratio  = values[i] / weights[i];
    }

    /* 按价值/重量比降序排序 */
    qsort(items, n, sizeof(Item), cmp_by_ratio);

    /* 贪心选择 */
    memset(selected, 0, n * sizeof(int));
    *best_value  = 0.0;
    *best_weight = 0;
    int remain   = capacity;

    for (int i = 0; i < n; i++) {
        if (items[i].weight <= remain) {
            selected[items[i].index] = 1;   /* 映射回原始编号 */
            *best_value  += items[i].value;
            *best_weight += items[i].weight;
            remain       -= items[i].weight;
        }
    }

    free(items);
}

/* ========================== 4. 回溯法 ========================== */

/* 全局变量: 回溯法中的物品数组 (已按比值排序) */
static Item  *bt_items   = NULL;
static int    bt_n        = 0;
static int    bt_capacity = 0;

/*
 * 计算当前节点的上界 (用于剪枝)
 *
 * 利用部分背包问题 (物品可分割) 的最优解作为上界:
 *   当前价值 + 剩余容量按比值从大到小装入剩余物品的最大可能价值
 *
 * 上界 ≤ 实际可达最优值，因此当上界 ≤ 已有最优值时可以安全剪枝。
 */
static double compute_bound(int step, int cur_weight, double cur_value) {
    double bound     = cur_value;
    int    remaining = bt_capacity - cur_weight;
    for (int i = step; i < bt_n && remaining > 0; i++) {
        if (bt_items[i].weight <= remaining) {
            bound     += bt_items[i].value;
            remaining -= bt_items[i].weight;
        } else {
            /* 最后一个物品只能部分装入 */
            bound     += bt_items[i].value * remaining / bt_items[i].weight;
            remaining  = 0;
        }
    }
    return bound;
}

/*
 * 回溯法 DFS 递归函数
 *
 * step         - 当前考虑的物品索引 (0-based)
 * cur_weight   - 当前已选物品总重量
 * cur_value    - 当前已选物品总价值
 * best_value   - 全局最优价值 (指针，递归过程中更新)
 * cur_selected - 当前路径的选择标记
 * best_selected- 全局最优方案的选择标记
 */
static void backtrack_dfs(int step, int cur_weight, double cur_value,
                          double *best_value,
                          int *cur_selected, int *best_selected) {
    /* 更新最优解 */
    if (cur_value > *best_value) {
        *best_value = cur_value;
        memcpy(best_selected, cur_selected, bt_n * sizeof(int));
    }

    /* 所有物品已考虑完毕 */
    if (step >= bt_n) return;

    /* 计算当前节点的上界 */
    double bound = compute_bound(step, cur_weight, cur_value);
    if (bound <= *best_value) {
        /* 上界不大于当前最优 => 剪枝 */
        return;
    }

    /* 分支1: 尝试装入当前物品 */
    int next_weight = cur_weight + bt_items[step].weight;
    if (next_weight <= bt_capacity) {
        cur_selected[step] = 1;
        backtrack_dfs(step + 1, next_weight,
                      cur_value + bt_items[step].value,
                      best_value, cur_selected, best_selected);
    }

    /* 分支2: 不装入当前物品 */
    cur_selected[step] = 0;
    backtrack_dfs(step + 1, cur_weight, cur_value,
                  best_value, cur_selected, best_selected);
}

/*
 * 回溯法 (Backtracking) 求解 0-1 背包问题
 *
 * 原理:
 *   采用深度优先搜索 (DFS) 遍历解空间树，每个物品有"选"与"不选"两个分支。
 *   核心优化:
 *     1. 先将物品按价值/重量比排序，使高价值物品优先处理，加快找到较优解
 *     2. 在每个节点计算上界 (通过部分背包问题的松弛)，若上界 ≤ 当前最优值则剪枝
 *
 * 时间复杂度: O(2^n) 最坏情况，但实际中剪枝大幅减少搜索空间
 * 空间复杂度: O(n)  —— 递归深度
 *
 * 回溯法能够保证找到最优解 (在剪枝不丢失最优解的前提下)。
 */
void backtracking(int n, int capacity, const int weights[],
                  const double values[],
                  int *selected, double *best_value, int *best_weight) {
    /* 分配并初始化物品数组，按比值排序 */
    bt_items = (Item *)malloc(n * sizeof(Item));
    for (int i = 0; i < n; i++) {
        bt_items[i].index  = i;
        bt_items[i].weight = weights[i];
        bt_items[i].value  = values[i];
        bt_items[i].ratio  = values[i] / weights[i];
    }
    qsort(bt_items, n, sizeof(Item), cmp_by_ratio);

    bt_n        = n;
    bt_capacity = capacity;

    /* 临时数组 */
    int *cur_selected  = (int *)calloc(n, sizeof(int));
    int *best_selected = (int *)calloc(n, sizeof(int));

    *best_value = 0.0;

    /* 启动 DFS */
    backtrack_dfs(0, 0, 0.0, best_value, cur_selected, best_selected);

    /* 将排序后的选择结果映射回原始物品编号 */
    memset(selected, 0, n * sizeof(int));
    *best_weight = 0;
    for (int i = 0; i < n; i++) {
        if (best_selected[i]) {
            int orig = bt_items[i].index;
            selected[orig] = 1;
            *best_weight  += weights[orig];
        }
    }

    /* 释放内存 */
    free(cur_selected);
    free(best_selected);
    free(bt_items);
    bt_items = NULL;
}

/* ========================== 主函数 ========================== */

int main(void) {
    /* ---------- 测试用例 ---------- */
    int    n        = 5;
    int    capacity = 10;
    int    weights[]   = {2, 2, 6, 5, 4};
    double values[]    = {6, 3, 5, 4, 6};

    /* 临时结果变量 */
    int    selected[5];
    double best_value;
    int    best_weight;
    clock_t start, end;
    double  elapsed_ms;

    printf("╔════════════════════════════════════════╗\n");
    printf("║     0-1 背包问题  四种算法对比演示      ║\n");
    printf("║     学号: 20241120062 姓名: 刘兴华       ║\n");
    printf("╠════════════════════════════════════════╣\n");
    printf("║  背包容量: %d                           ║\n", capacity);
    printf("║  物品重量: [2, 2, 6, 5, 4]             ║\n");
    printf("║  物品价值: [6, 3, 5, 4, 6]             ║\n");
    printf("╚════════════════════════════════════════╝\n\n");

    /* ----------------------------------------------------------------
     * 算法一: 蛮力法 (Brute Force)
     * 原理: 枚举 2^n 个子集，逐一验证重量约束，取价值最大者。
     * 复杂度: 时间 O(n·2^n)，空间 O(n)。
     * ---------------------------------------------------------------- */
    printf(">>> 开始执行 蛮力法 ...\n");
    start = clock();
    brute_force(n, capacity, weights, values,
                selected, &best_value, &best_weight);
    end = clock();
    elapsed_ms = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;
    print_result("蛮力法 (Brute Force)", n, selected,
                 best_weight, best_value, elapsed_ms);

    /* ----------------------------------------------------------------
     * 算法二: 动态规划法 (Dynamic Programming)
     * 原理: dp[j]=max(dp[j], dp[j-w[i]]+v[i])，一维数组倒序更新。
     * 复杂度: 时间 O(n·C)，空间 O(n·C)（含路径记录）。
     * ---------------------------------------------------------------- */
    printf(">>> 开始执行 动态规划法 ...\n");
    start = clock();
    dynamic_programming(n, capacity, weights, values,
                        selected, &best_value, &best_weight);
    end = clock();
    elapsed_ms = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;
    print_result("动态规划法 (Dynamic Programming)", n, selected,
                 best_weight, best_value, elapsed_ms);

    /* ----------------------------------------------------------------
     * 算法三: 贪心法 (Greedy)
     * 原理: 按 value/weight 比值降序排序，依次装入不超容量的物品。
     * 复杂度: 时间 O(n log n)，空间 O(n)。
     * 注意: 贪心法在 0-1 背包中不保证最优解。
     * ---------------------------------------------------------------- */
    printf(">>> 开始执行 贪心法 ...\n");
    start = clock();
    greedy(n, capacity, weights, values,
           selected, &best_value, &best_weight);
    end = clock();
    elapsed_ms = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;
    print_result("贪心法 (Greedy)", n, selected,
                 best_weight, best_value, elapsed_ms);

    /* ----------------------------------------------------------------
     * 算法四: 回溯法 (Backtracking)
     * 原理: DFS 遍历解空间树，按比值排序 + 上界剪枝加速搜索。
     * 复杂度: 最坏 O(2^n)，剪枝后实际搜索空间远小于此。
     * ---------------------------------------------------------------- */
    printf(">>> 开始执行 回溯法 ...\n");
    start = clock();
    backtracking(n, capacity, weights, values,
                 selected, &best_value, &best_weight);
    end = clock();
    elapsed_ms = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;
    print_result("回溯法 (Backtracking)", n, selected,
                 best_weight, best_value, elapsed_ms);

    /* ---------- 算法对比总结 ---------- */
    printf("╔════════════════════════════════════════╗\n");
    printf("║            算法对比总结                 ║\n");
    printf("╠══════════════════╦═════════╦═══════════╣\n");
    printf("║ 算法             ║ 最优性  ║ 时间复杂度 ║\n");
    printf("╠══════════════════╬═════════╬═══════════╣\n");
    printf("║ 蛮力法           ║ 最优    ║ O(n·2^n)  ║\n");
    printf("║ 动态规划法       ║ 最优    ║ O(n·C)    ║\n");
    printf("║ 贪心法           ║ 近似    ║ O(nlogn)  ║\n");
    printf("║ 回溯法           ║ 最优    ║ O(2^n)*   ║\n");
    printf("╚══════════════════╩═════════╩═══════════╝\n");
    printf("  * 回溯法最坏 O(2^n)，剪枝后实际远小于此\n");

    return 0;
}
