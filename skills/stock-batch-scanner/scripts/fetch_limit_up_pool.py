#!/usr/bin/env python3
"""
涨停股池获取 — API回退路径
方法1: 东方财富涨停板复盘API (push2ex)
方法2: 从push2his K线API逐股获取候选股的K线并判断涨停 (当方法1不可用时)
"""

import sys
import io
import requests
import json
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def get_recent_trading_days(n_days):
    dates = []
    today = datetime.now()
    i = 0
    while len(dates) < n_days + 10:
        d = today - timedelta(days=i)
        if d.weekday() < 5:
            dates.append(d.strftime("%Y%m%d"))
        i += 1
        if i > n_days * 3:
            break
    return dates[:n_days + 5]


def fetch_zt_pool_eastmoney(date_str):
    """通过东方财富涨停板复盘API获取指定日期涨停股"""
    url = "https://push2ex.eastmoney.com/getTopicZTPool"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dession": "",
        "Ession": "",
        "date": date_str,
        "fields": "f1,f2,f3,f4,f6,f8,f12,f13,f14,f15,f16,f17,f221,f222,f223,f224,f225",
        "_": str(int(time.time() * 1000)),
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        pool = data.get("data", {})
        if not pool or not pool.get("pool"):
            return []
        results = []
        for item in pool["pool"]:
            code = str(item.get("f12", "")).zfill(6)
            name = item.get("f14", "")
            change_pct = item.get("f3", 0)
            if not _is_a_share(code, name):
                continue
            results.append({
                "code": code,
                "name": name,
                "change_pct": change_pct,
            })
        return results
    except Exception:
        return []


def fetch_limit_up_via_kline(codes, days=40, delay=0.3, threads=5):
    """
    通过K线API判断候选股中哪些近N日有涨停。
    codes: 待查的股票代码列表
    """
    from _import_helper import fetch_kline_eastmoney
    from concurrent.futures import ThreadPoolExecutor, as_completed

    pool = {}
    done = 0
    total = len(codes)

    def check_one(code):
        result = fetch_kline_eastmoney(code, "daily", days + 10)
        if delay > 0:
            time.sleep(delay)
        return code, result

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_one, c): c for c in codes}
        for future in as_completed(futures):
            done += 1
            try:
                code, result = future.result()
                if result and "klines" in result and result["klines"]:
                    zt_dates = []
                    for k in result["klines"]:
                        pct = k.get("change_pct", 0)
                        if pct >= 9.8:
                            zt_dates.append(k["date"])
                    if zt_dates:
                        pool[code] = {
                            "name": result.get("name", ""),
                            "limit_up_dates": zt_dates,
                            "limit_up_count": len(zt_dates),
                            "latest_change_pct": result["klines"][-1].get("change_pct", 0),
                            "klines": result["klines"],
                        }
            except Exception:
                pass

            if done % 100 == 0 or done == total:
                print(f"  [{done}/{total}] 已发现 {len(pool)} 只涨停股")

    return pool


def _is_a_share(code, name):
    if not code or len(code) != 6 or not code.isdigit():
        return False
    if code.startswith("4") or code.startswith("8"):
        return False
    if "ST" in str(name) or "退" in str(name) or "B" in str(name):
        return False
    return True


def fetch_limit_up_pool(days=40, delay=0.3):
    """
    获取近N个交易日的涨停股票汇总。
    先尝试涨停板复盘API，不可用时回退到K线逐日判断。
    """
    trading_days = get_recent_trading_days(days)
    pool = {}
    fetched = 0
    empty_streak = 0

    print(f"📊 获取近{days}个交易日涨停股池...")

    # 方法1: push2ex涨停板API
    for date_str in trading_days[:5]:
        stocks = fetch_zt_pool_eastmoney(date_str)
        if stocks:
            empty_streak = 0
            fetched += 1
            break
        empty_streak += 1

    if fetched > 0:
        print("  使用涨停板复盘API...")
        for date_str in trading_days:
            if empty_streak > 5:
                break
            stocks = fetch_zt_pool_eastmoney(date_str)
            if not stocks:
                empty_streak += 1
                continue
            empty_streak = 0
            fetched += 1
            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            for s in stocks:
                code = s["code"]
                if code not in pool:
                    pool[code] = {
                        "name": s["name"],
                        "limit_up_dates": [],
                        "latest_change_pct": s["change_pct"],
                    }
                pool[code]["limit_up_dates"].append(formatted_date)
            if delay > 0:
                time.sleep(delay)

        for v in pool.values():
            v["limit_up_dates"].sort()
            v["limit_up_count"] = len(v["limit_up_dates"])
        print(f"✅ 扫描{fetched}个交易日，发现{len(pool)}只涨停股")
    else:
        print("  ⚠ 涨停板API不可用，回退到K线判断模式")
        print("  将在batch_scanner中通过K线数据直接判断涨停")

    return pool


def main():
    parser = argparse.ArgumentParser(description="获取近N日涨停股池")
    parser.add_argument("--days", type=int, default=40, help="回溯交易日数 (默认40)")
    parser.add_argument("-o", "--output", default="limit_up_pool.json", help="输出文件路径")
    parser.add_argument("--delay", type=float, default=0.3, help="请求间隔秒数")
    args = parser.parse_args()

    pool = fetch_limit_up_pool(days=args.days, delay=args.delay)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存至 {output_path}")


if __name__ == "__main__":
    main()
