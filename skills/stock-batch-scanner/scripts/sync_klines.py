#!/usr/bin/env python3
"""
K线数据同步脚本
--init:   首次全量下载全A股K线到本地缓存 (~50分钟, 一次性)
--update: 每日增量更新，追加当日收盘数据 (~30秒)
"""

import sys
import io
import json
import time
import argparse
import requests
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from data_provider import DataProvider, load_config
from _import_helper import fetch_kline_eastmoney


def fetch_all_stock_list():
    """
    获取全A股票列表 (沪深主板+创业板+科创板)
    优先用push2 clist API，失败时回退到腾讯财经批量报价
    """
    stocks = _fetch_stock_list_eastmoney()
    if len(stocks) > 100:
        return stocks
    print("  ⚠ push2 API不可用，回退到腾讯财经接口获取股票列表...")
    return _fetch_stock_list_tencent()


def _fetch_stock_list_eastmoney():
    stocks = {}
    for market_id in [0, 1]:
        page = 1
        while True:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": page,
                "pz": 5000,
                "po": 1,
                "np": 1,
                "fltt": 2,
                "invt": 2,
                "fs": f"m:{market_id}+t:6,m:{market_id}+t:13,m:{market_id}+t:80" if market_id == 0 else f"m:{market_id}+t:2,m:{market_id}+t:23",
                "fields": "f12,f14",
            }
            try:
                resp = requests.get(url, params=params, timeout=15)
                data = resp.json()
                diff = data.get("data", {}).get("diff", [])
                if not diff:
                    break
                for item in diff:
                    code = str(item.get("f12", ""))
                    name = str(item.get("f14", ""))
                    if _is_valid_a_share(code, name):
                        stocks[code] = name
                if len(diff) < 5000:
                    break
                page += 1
            except Exception as e:
                print(f"  ⚠ 获取股票列表失败 (market={market_id}, page={page}): {e}")
                break
    return stocks


def _fetch_stock_list_tencent():
    """
    通过腾讯财经批量报价接口探测有效股票代码。
    生成所有可能的A股代码范围，批量查询。
    """
    stocks = {}
    code_ranges = []
    for prefix in range(0, 4):
        for i in range(0, 10000):
            code = f"{prefix:01d}{i:05d}"
            if code.startswith("0") or code.startswith("3"):
                code_ranges.append(f"sz{code}")
    for i in range(600000, 690000):
        code_ranges.append(f"sh{i:06d}")

    batch_size = 50
    for batch_start in range(0, len(code_ranges), batch_size):
        batch = code_ranges[batch_start : batch_start + batch_size]
        url = "https://qt.gtimg.cn/q=" + ",".join(batch)
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            for line in resp.text.strip().split(";"):
                line = line.strip()
                if not line or "~" not in line:
                    continue
                parts = line.split("~")
                if len(parts) < 5:
                    continue
                name = parts[1].strip()
                code = parts[2].strip()
                price = parts[3].strip()
                if not name or not code or price == "0.00" or not price:
                    continue
                if _is_valid_a_share(code, name):
                    stocks[code] = name
        except Exception:
            continue

        if batch_start % 5000 == 0 and batch_start > 0:
            print(f"  已扫描 {batch_start}/{len(code_ranges)} 代码, 发现 {len(stocks)} 只股票")
            time.sleep(0.1)

    return stocks


def fetch_all_realtime_batch():
    """
    批量获取全A股今日收盘数据 (用于增量更新)
    优先用push2 clist API，失败时回退到腾讯批量报价
    """
    results = _fetch_realtime_eastmoney()
    if len(results) > 100:
        return results
    print("  ⚠ push2 API不可用，回退到腾讯财经批量报价...")
    return _fetch_realtime_tencent()


def _fetch_realtime_eastmoney():
    results = []
    for fs_str in [
        "m:0+t:6,m:0+t:13,m:0+t:80",
        "m:1+t:2,m:1+t:23",
    ]:
        page = 1
        while True:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": page,
                "pz": 5000,
                "po": 1,
                "np": 1,
                "fltt": 2,
                "invt": 2,
                "fs": fs_str,
                "fields": "f12,f14,f2,f15,f16,f17,f3,f5,f6,f7,f8",
            }
            try:
                resp = requests.get(url, params=params, timeout=15)
                data = resp.json()
                diff = data.get("data", {}).get("diff", [])
                if not diff:
                    break
                today = datetime.now().strftime("%Y-%m-%d")
                for item in diff:
                    code = str(item.get("f12", ""))
                    name = str(item.get("f14", ""))
                    if not _is_valid_a_share(code, name):
                        continue
                    close = item.get("f2")
                    if close is None or close == "-":
                        continue
                    results.append({
                        "code": code,
                        "name": name,
                        "date": today,
                        "open": _safe_float(item.get("f17")),
                        "close": _safe_float(close),
                        "high": _safe_float(item.get("f15")),
                        "low": _safe_float(item.get("f16")),
                        "volume": int(item.get("f5", 0) or 0),
                        "amount": _safe_float(item.get("f6")),
                        "change_pct": _safe_float(item.get("f3")),
                        "amplitude": _safe_float(item.get("f7")),
                        "turnover": _safe_float(item.get("f8")),
                    })
                if len(diff) < 5000:
                    break
                page += 1
            except Exception as e:
                print(f"  ⚠ 批量获取失败 (page={page}): {e}")
                break
    return results


def _fetch_realtime_tencent():
    """从腾讯财经批量获取今日行情, 基于已有的stock_list.json"""
    provider = DataProvider()
    stock_list = provider.get_stock_list()
    if not stock_list:
        print("  ⚠ 无stock_list.json，无法执行腾讯回退")
        return []

    results = []
    codes = list(stock_list.keys())
    today = datetime.now().strftime("%Y-%m-%d")
    batch_size = 50

    for batch_start in range(0, len(codes), batch_size):
        batch = codes[batch_start: batch_start + batch_size]
        prefixed = []
        for c in batch:
            prefix = "sh" if c.startswith("6") else "sz"
            prefixed.append(f"{prefix}{c}")
        url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
        try:
            resp = requests.get(url, timeout=10)
            for line in resp.text.strip().split(";"):
                line = line.strip()
                if not line or "~" not in line:
                    continue
                parts = line.split("~")
                if len(parts) < 45:
                    continue
                code = parts[2].strip()
                name = parts[1].strip()
                close = _safe_float(parts[3])
                if close == 0:
                    continue
                results.append({
                    "code": code,
                    "name": name,
                    "date": today,
                    "open": _safe_float(parts[5]),
                    "close": close,
                    "high": _safe_float(parts[33]),
                    "low": _safe_float(parts[34]),
                    "volume": int(_safe_float(parts[6]) * 100),
                    "amount": _safe_float(parts[37]),
                    "change_pct": _safe_float(parts[32]),
                    "amplitude": _safe_float(parts[43]),
                    "turnover": _safe_float(parts[38]),
                })
        except Exception:
            continue

    return results


def _safe_float(val):
    try:
        if val is None or val == "-" or val == "":
            return 0.0
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _is_valid_a_share(code: str, name: str) -> bool:
    if not code or len(code) != 6 or not code.isdigit():
        return False
    if code.startswith("4") or code.startswith("8"):
        return False
    if "ST" in name or "退" in name:
        return False
    return True


def init_full_download(provider: DataProvider, config: dict):
    """首次全量下载"""
    threads = config.get("api_threads", 5)
    delay = config.get("api_delay", 0.5)
    klines_days = config.get("klines_days", 70)

    print("📋 Step 1: 获取全A股票列表...")
    stocks = fetch_all_stock_list()
    print(f"  ✅ 获取到 {len(stocks)} 只股票")
    provider.save_stock_list(stocks)

    print(f"\n📈 Step 2: 下载K线数据 ({len(stocks)}只, {threads}线程)...")
    codes = list(stocks.keys())
    done = 0
    failed = 0
    total = len(codes)
    start_time = time.time()

    def download_one(code):
        nonlocal delay
        result = fetch_kline_eastmoney(code, "daily", klines_days)
        if delay > 0:
            time.sleep(delay)
        return code, result

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(download_one, c): c for c in codes}
        for future in as_completed(futures):
            code = futures[future]
            done += 1
            try:
                code, result = future.result()
                if result and "klines" in result and result["klines"]:
                    name = result.get("name", stocks.get(code, ""))
                    provider.save_kline(code, name, result["klines"])
                else:
                    failed += 1
            except Exception:
                failed += 1

            if done % 100 == 0 or done == total:
                elapsed = time.time() - start_time
                speed = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / speed if speed > 0 else 0
                print(f"  [{done}/{total}] {done*100//total}% | "
                      f"失败{failed} | {speed:.1f}只/秒 | ETA {eta/60:.1f}分钟")

    elapsed = time.time() - start_time
    provider.update_sync_meta(
        last_full_sync=datetime.now().isoformat(),
        stock_count=total,
        failed_count=failed,
        elapsed_seconds=round(elapsed),
    )
    print(f"\n✅ 全量下载完成: {total - failed}/{total} 成功, 耗时 {elapsed/60:.1f} 分钟")


def update_daily(provider: DataProvider):
    """每日增量更新"""
    print("📊 获取今日全A股收盘数据...")
    records = fetch_all_realtime_batch()
    print(f"  ✅ 获取到 {len(records)} 只股票数据")

    if not records:
        print("  ⚠ 无数据，可能非交易日或未收盘")
        return

    updated = 0
    new_stocks = 0
    for rec in records:
        code = rec["code"]
        daily = {
            "date": rec["date"],
            "open": rec["open"],
            "close": rec["close"],
            "high": rec["high"],
            "low": rec["low"],
            "volume": rec["volume"],
            "amount": rec["amount"],
            "change_pct": rec["change_pct"],
            "amplitude": rec.get("amplitude", 0),
            "turnover": rec.get("turnover", 0),
            "change": round(rec["close"] - rec["open"], 2) if rec["close"] and rec["open"] else 0,
        }
        cache_file = provider.klines_dir / f"{code}.json"
        if cache_file.exists():
            provider.append_daily(code, daily)
            updated += 1
        else:
            provider.save_kline(code, rec["name"], [daily])
            new_stocks += 1

    stock_list = provider.get_stock_list()
    for rec in records:
        if rec["code"] not in stock_list:
            stock_list[rec["code"]] = rec["name"]
    provider.save_stock_list(stock_list)

    provider.update_sync_meta(
        last_update=datetime.now().isoformat(),
        last_update_count=updated,
        new_stocks=new_stocks,
    )
    print(f"✅ 增量更新完成: 更新{updated}只, 新增{new_stocks}只")


def main():
    parser = argparse.ArgumentParser(description="K线数据同步")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true", help="首次全量下载 (~50分钟)")
    group.add_argument("--update", action="store_true", help="每日增量更新 (~30秒)")
    parser.add_argument("--config", default=None, help="配置文件路径")
    args = parser.parse_args()

    config = load_config(args.config)
    provider = DataProvider(args.config)

    if args.init:
        init_full_download(provider, config)
    elif args.update:
        update_daily(provider)


if __name__ == "__main__":
    main()
