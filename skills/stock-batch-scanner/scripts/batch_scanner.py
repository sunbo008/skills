#!/usr/bin/env python3
"""
全A股批量扫描主入口
三重筛选: 近2月涨停 + 多头排列 + 右侧买点
自动选择数据路径: 有本地数据→零API / 无本地数据→涨停池预过滤+API
"""

import sys
import io
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from data_provider import DataProvider, load_config
from fetch_limit_up_pool import fetch_limit_up_pool
from _import_helper import fetch_kline_eastmoney


# ============================================================
# 技术指标计算
# ============================================================

def compute_ma(closes: list, period: int):
    if len(closes) < period:
        return None
    return sum(closes[-period:]) / period


def compute_ma_series(closes: list, period: int) -> list:
    """计算MA序列 (长度 = len(closes) - period + 1)"""
    if len(closes) < period:
        return []
    series = []
    for i in range(period - 1, len(closes)):
        series.append(sum(closes[i - period + 1 : i + 1]) / period)
    return series


# ============================================================
# 三重筛选
# ============================================================

def has_limit_up(klines: list, lookback_days: int = 40) -> dict:
    """
    检查近N日是否有涨停。
    返回: {"passed": bool, "dates": [str], "count": int}
    主板涨跌幅限制10%, 创业板/科创板20%
    """
    recent = klines[-lookback_days:] if len(klines) > lookback_days else klines
    limit_dates = []
    for k in recent:
        code = ""
        threshold = 9.8
        pct = k.get("change_pct", 0)
        if pct >= 19.5:
            limit_dates.append(k["date"])
        elif pct >= threshold:
            limit_dates.append(k["date"])
    return {
        "passed": len(limit_dates) > 0,
        "dates": limit_dates,
        "count": len(limit_dates),
    }


def is_multi_head(klines: list) -> dict:
    """
    检查多头排列: MA5 > MA10 > MA20 > MA60
    返回: {"passed": bool, "ma5": float, "ma10": float, "ma20": float, "ma60": float}
    """
    closes = [k["close"] for k in klines]
    ma5 = compute_ma(closes, 5)
    ma10 = compute_ma(closes, 10)
    ma20 = compute_ma(closes, 20)
    ma60 = compute_ma(closes, 60)

    passed = False
    if ma5 and ma10 and ma20 and ma60:
        passed = ma5 > ma10 > ma20 > ma60
    elif ma5 and ma10 and ma20:
        passed = ma5 > ma10 > ma20

    return {
        "passed": passed,
        "ma5": round(ma5, 3) if ma5 else None,
        "ma10": round(ma10, 3) if ma10 else None,
        "ma20": round(ma20, 3) if ma20 else None,
        "ma60": round(ma60, 3) if ma60 else None,
    }


def is_right_side_buy(klines: list) -> dict:
    """
    右侧买点判定:
    1. MA20上升 (当前MA20 > 5日前MA20)
    2. 收盘价 > MA10 且 > MA20
    3. 近5日低点曾触及MA10/MA20附近(±3%)
    4. 最新K线阳线确认
    """
    closes = [k["close"] for k in klines]
    if len(closes) < 25:
        return {"passed": False, "reason": "数据不足"}

    ma20_series = compute_ma_series(closes, 20)
    if len(ma20_series) < 6:
        return {"passed": False, "reason": "MA20序列不足"}

    ma20_now = ma20_series[-1]
    ma20_5d_ago = ma20_series[-6]
    ma10 = compute_ma(closes, 10)
    current_close = closes[-1]

    if ma20_now <= ma20_5d_ago:
        return {"passed": False, "reason": "MA20未上升"}

    if current_close < ma10 or current_close < ma20_now:
        return {"passed": False, "reason": "价格未站上均线"}

    recent_lows = [k["low"] for k in klines[-5:]]
    touched_ma20 = any(abs(low - ma20_now) / ma20_now < 0.03 for low in recent_lows)
    touched_ma10 = any(abs(low - ma10) / ma10 < 0.03 for low in recent_lows) if ma10 else False
    if not (touched_ma20 or touched_ma10):
        return {"passed": False, "reason": "近5日未回踩均线"}

    if klines[-1]["close"] <= klines[-1]["open"]:
        return {"passed": False, "reason": "最新K线非阳线"}

    return {
        "passed": True,
        "ma20_slope": round((ma20_now - ma20_5d_ago) / ma20_5d_ago * 100, 2),
        "distance_to_ma20": round((current_close - ma20_now) / ma20_now * 100, 2),
    }


def compute_score(klines: list, limit_up_info: dict, multi_head: dict, right_side: dict) -> float:
    """综合评分 0-100"""
    score = 0
    score += min(limit_up_info["count"] * 15, 30)

    if multi_head["passed"]:
        score += 25
        if multi_head.get("ma60"):
            score += 5

    if right_side["passed"]:
        score += 25
        slope = right_side.get("ma20_slope", 0)
        if slope > 1:
            score += min(slope * 2, 10)

    closes = [k["close"] for k in klines]
    if len(closes) >= 6:
        change_5d = (closes[-1] / closes[-6] - 1) * 100
        if 5 < change_5d < 25:
            score += 5

    return round(min(score, 100), 1)


def scan_stock(code, klines, lookback_days=40):
    """对单只股票执行三重筛选，返回结果或None(未通过)"""
    if not klines or len(klines) < 20:
        return None

    limit_up = has_limit_up(klines, lookback_days)
    if not limit_up["passed"]:
        return None

    multi_head = is_multi_head(klines)
    if not multi_head["passed"]:
        return None

    right_side = is_right_side_buy(klines)
    if not right_side["passed"]:
        return None

    score = compute_score(klines, limit_up, multi_head, right_side)
    closes = [k["close"] for k in klines]
    latest = klines[-1]

    def period_change(n):
        if len(closes) >= n + 1:
            return round((closes[-1] / closes[-(n + 1)] - 1) * 100, 2)
        return 0

    return {
        "code": code,
        "price": latest["close"],
        "change_pct": latest.get("change_pct", 0),
        "turnover": latest.get("turnover", 0),
        "change_5d": period_change(5),
        "change_10d": period_change(10),
        "change_20d": period_change(20),
        "limit_up_dates": limit_up["dates"],
        "limit_up_count": limit_up["count"],
        "ma5": multi_head["ma5"],
        "ma10": multi_head["ma10"],
        "ma20": multi_head["ma20"],
        "ma60": multi_head["ma60"],
        "ma20_slope": right_side.get("ma20_slope", 0),
        "score": score,
        "date": latest["date"],
    }


# ============================================================
# 主流程
# ============================================================

def scan_from_local(provider, config):
    """路径A: 从本地数据扫描"""
    lookback = config.get("scan_lookback_days", 40)
    klines_days = config.get("klines_days", 70)

    print(f"📂 数据源: {provider.get_source_info()}")
    print(f"📊 加载本地K线数据...")
    start = time.time()
    all_klines = provider.get_all_klines(days=klines_days)
    print(f"  ✅ 加载 {len(all_klines)} 只股票, 耗时 {time.time()-start:.1f}秒")

    stock_list = provider.get_stock_list()
    return _do_scan(all_klines, stock_list, lookback)


def scan_from_api(config):
    """路径B: 无本地数据，从API涨停池预过滤"""
    lookback = config.get("scan_lookback_days", 40)
    klines_days = config.get("klines_days", 70)
    threads = config.get("api_threads", 5)
    delay = config.get("api_delay", 0.5)

    print("🌐 无本地数据，走API回退路径")
    pool = fetch_limit_up_pool(days=lookback)
    if not pool:
        print("⚠ 涨停池为空，且无本地数据")
        print("💡 建议先运行 sync_klines.py --init 建立本地数据库")
        return []

    print(f"\n📈 批量获取 {len(pool)} 只候选股K线 ({threads}线程)...")
    codes = list(pool.keys())
    all_klines = {}
    stock_list = {}
    done = 0
    total = len(codes)
    start = time.time()

    for code, info in pool.items():
        if "klines" in info and info["klines"]:
            all_klines[code] = info["klines"]
            stock_list[code] = info.get("name", "")
            done += 1

    remaining = [c for c in codes if c not in all_klines]
    if remaining:
        def fetch_one(code):
            result = fetch_kline_eastmoney(code, "daily", klines_days)
            if delay > 0:
                time.sleep(delay)
            return code, result

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(fetch_one, c): c for c in remaining}
            for future in as_completed(futures):
                done += 1
                try:
                    code, result = future.result()
                    if result and "klines" in result and result["klines"]:
                        all_klines[code] = result["klines"]
                        name = result.get("name", pool.get(code, {}).get("name", ""))
                        stock_list[code] = name
                except Exception:
                    pass
                if done % 50 == 0 or done == total:
                    print(f"  [{done}/{total}] {done*100//total}%")

    provider = DataProvider()
    for code, kl in all_klines.items():
        provider.save_kline(code, stock_list.get(code, ""), kl)
    provider.save_stock_list(stock_list)
    provider.update_sync_meta(
        last_api_scan=datetime.now().isoformat(),
        api_scan_count=len(all_klines),
    )
    print(f"  ✅ 获取 {len(all_klines)} 只K线, 耗时 {(time.time()-start)/60:.1f}分钟")
    return _do_scan(all_klines, stock_list, lookback)


def _do_scan(all_klines: dict, stock_list: dict, lookback: int) -> list:
    """执行三重筛选"""
    print(f"\n🔍 执行三重筛选 (回溯{lookback}日)...")
    results = []
    stats = {"total": 0, "limit_up": 0, "multi_head": 0, "right_side": 0}

    for code, klines in all_klines.items():
        stats["total"] += 1
        if not klines or len(klines) < 20:
            continue

        limit_up = has_limit_up(klines, lookback)
        if not limit_up["passed"]:
            continue
        stats["limit_up"] += 1

        multi_head = is_multi_head(klines)
        if not multi_head["passed"]:
            continue
        stats["multi_head"] += 1

        right_side = is_right_side_buy(klines)
        if not right_side["passed"]:
            continue
        stats["right_side"] += 1

        result = scan_stock(code, klines, lookback)
        if result:
            result["name"] = stock_list.get(code, "")
            results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n📊 筛选统计:")
    print(f"  扫描总数:   {stats['total']}")
    print(f"  近{lookback}日涨停: {stats['limit_up']}")
    print(f"  多头排列:   {stats['multi_head']}")
    print(f"  右侧买点:   {stats['right_side']} ← 最终结果")
    return results


def main():
    parser = argparse.ArgumentParser(description="全A股批量扫描选股")
    parser.add_argument("-o", "--output", default="screened.json", help="输出文件路径")
    parser.add_argument("--days", type=int, default=None, help="涨停回溯天数 (默认从config读取)")
    parser.add_argument("--config", default=None, help="配置文件路径")
    parser.add_argument("--top", type=int, default=None, help="只输出TOP N")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.days:
        config["scan_lookback_days"] = args.days
    provider = DataProvider(args.config)

    start = time.time()
    if provider.has_local_data():
        results = scan_from_local(provider, config)
    else:
        results = scan_from_api(config)

    if args.top and len(results) > args.top:
        results = results[: args.top]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_data = {
        "scan_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "scan_mode": "local" if provider.has_local_data() else "api",
        "total_scanned": len(provider.get_all_klines()) if provider.has_local_data() else 0,
        "result_count": len(results),
        "results": results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start
    print(f"\n✅ 扫描完成: {len(results)} 只通过筛选, 耗时 {elapsed:.1f}秒")
    print(f"💾 结果保存至 {output_path}")

    if results:
        print(f"\n🏆 TOP 10:")
        for i, r in enumerate(results[:10], 1):
            print(f"  {i:2d}. {r['code']} {r['name']:8s} "
                  f"¥{r['price']:.2f} ({r['change_pct']:+.2f}%) "
                  f"评分{r['score']} "
                  f"涨停{r['limit_up_count']}次 "
                  f"5日{r['change_5d']:+.1f}%")


if __name__ == "__main__":
    main()
