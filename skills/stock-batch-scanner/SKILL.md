---
name: stock-batch-scanner
description: 全A股批量扫描选股。从本地K线数据或API批量筛选"近2月涨停+多头排列+右侧买点"的股票，生成交互式看板，并衔接stock-anomaly-analysis做深度分析。当用户提到"全市场扫描"、"批量选股"、"筛选股票"、"今日选股"、"扫描全A"或需要从全市场中筛选符合条件的股票时使用此技能。
---

# 全A股批量扫描选股

从沪深5000+只股票中，自动筛选出 **近2月有涨停 + 多头排列 + 右侧买点** 的标的。

## 两层架构

- **Tier 1 (脚本筛选)**: 纯Python脚本执行，零LLM Token消耗
- **Tier 2 (深度分析)**: 对筛选结果中用户选定的股票，调用 `stock-anomaly-analysis` 技能做深度分析

## 数据路径自动选择

| 条件 | 路径 | API调用 | 耗时 |
|------|------|---------|------|
| 有本地K线数据 (TDX .day 或 JSON缓存) | 本地扫描 | **0次** | <30秒 |
| 无本地数据 | API回退: 涨停池预过滤 + 候选K线获取 | ~1040次 | ~15-20分钟 |

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/data_provider.py` | 本地数据抽象层，支持TDX .day和JSON缓存 |
| `scripts/fetch_limit_up_pool.py` | API回退路径: 获取近N日涨停股池 |
| `scripts/sync_klines.py` | 数据同步: 首次全量下载 + 每日增量更新 |
| `scripts/batch_scanner.py` | 扫描主入口: 自动选路径 + 三重筛选 |
| `scripts/generate_dashboard.py` | 生成交互式HTML看板 |

## 工作流

### 首次使用 (建立本地数据库, 可选)

```bash
# 全量下载全A股K线数据到本地 (~50分钟, 一次性)
python3 scripts/sync_klines.py --init
```

### 每日使用

```bash
# Step 1: 增量更新今日数据 (有本地数据时, ~30秒)
python3 scripts/sync_klines.py --update

# Step 2: 执行扫描 (有本地数据<30秒 / 无本地数据~15分钟)
python3 scripts/batch_scanner.py -o screened.json

# Step 3: 生成看板
python3 scripts/generate_dashboard.py --data screened.json --output docs/scanner/全市场扫描--$(date +%Y-%m-%d).html
```

### Agent执行流程

1. 检查是否有本地数据 → 运行 `data_provider.py` 查看
2. 若有本地数据 → 先 `sync_klines.py --update` 增量更新
3. 若无本地数据 → 直接运行 `batch_scanner.py` (自动走API回退)
4. 运行 `batch_scanner.py -o screened.json`
5. 运行 `generate_dashboard.py` 生成看板
6. 向用户展示筛选结果摘要 (TOP 10 + 统计漏斗)
7. 用户选择感兴趣的股票
8. 对选中股票调用 `stock-anomaly-analysis` 技能做深度分析

## 筛选条件

### 1. 近2月涨停 (回溯40个交易日)
- 主板: `change_pct >= 9.8%`
- 创业板/科创板: `change_pct >= 19.5%`

### 2. 多头排列
- `MA5 > MA10 > MA20 > MA60`
- 若MA60数据不足，放宽为 `MA5 > MA10 > MA20`

### 3. 右侧买点
以下条件需同时满足:
- MA20上升: 当前MA20 > 5日前MA20
- 价格站上均线: 收盘价 > MA10 且 > MA20
- 回踩确认: 近5日低点曾触及MA10或MA20附近(±3%)
- 阳线反弹: 最新K线收盘 > 开盘

## 配置文件 (config.json)

```json
{
  "data_source": "json_cache",
  "tdx_path": "",
  "cache_dir": "data",
  "klines_days": 70,
  "scan_lookback_days": 40,
  "api_threads": 5,
  "api_delay": 0.5
}
```

- `tdx_path`: 通达信 vipdoc 目录路径 (如 `/path/to/new_tdx/vipdoc`)
- `cache_dir`: JSON缓存目录 (默认 `data/`)
- `scan_lookback_days`: 涨停回溯天数
- `api_threads`: API并发线程数
- `api_delay`: API请求间隔(秒)

## 输出

- 筛选结果: `screened.json`
- HTML看板: `docs/scanner/全市场扫描--YYYY-MM-DD.html`
- 看板功能: 搜索、排序(点击表头)、评分筛选、多次涨停筛选
