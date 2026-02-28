#!/usr/bin/env python3
"""
本地K线数据抽象层
支持两种数据源: TDX .day 二进制文件 / JSON缓存文件
自动按优先级选择: TDX > JSON缓存 > 无数据
"""

import os
import json
import struct
import glob
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CACHE_DIR = SKILL_DIR / "data"
DEFAULT_CONFIG_PATH = SKILL_DIR / "config.json"


def load_config(config_path=None):
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def read_tdx_day(filepath):
    """解析通达信 .day 二进制文件 (32字节/记录)"""
    records = []
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(32)
            if len(chunk) < 32:
                break
            date_i, open_i, high_i, low_i, close_i, amount_f, volume_i, _ = struct.unpack(
                "<IIIIIfII", chunk
            )
            date_str = str(date_i)
            if len(date_str) != 8:
                continue
            formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            records.append({
                "date": formatted,
                "open": open_i / 100.0,
                "high": high_i / 100.0,
                "low": low_i / 100.0,
                "close": close_i / 100.0,
                "amount": amount_f,
                "volume": volume_i,
                "change_pct": 0.0,
                "turnover": 0.0,
            })
    _fill_change_pct(records)
    return records


def _fill_change_pct(records):
    """为TDX数据补算涨跌幅"""
    for i in range(len(records)):
        if i == 0:
            records[i]["change_pct"] = 0.0
        else:
            prev_close = records[i - 1]["close"]
            if prev_close > 0:
                records[i]["change_pct"] = round(
                    (records[i]["close"] - prev_close) / prev_close * 100, 2
                )


class DataProvider:
    def __init__(self, config_path=None):
        self.config = load_config(config_path)
        self.cache_dir = Path(self.config.get("cache_dir", str(DEFAULT_CACHE_DIR)))
        if not self.cache_dir.is_absolute():
            self.cache_dir = SKILL_DIR / self.cache_dir
        self.klines_dir = self.cache_dir / "klines"
        self.tdx_path = self.config.get("tdx_path", "")
        self._source = self._detect_source()

    def _detect_source(self):
        min_stocks = self.config.get("min_local_stocks", 5)
        if self.tdx_path:
            p = Path(self.tdx_path)
            sh_lday = p / "sh" / "lday"
            sz_lday = p / "sz" / "lday"
            if sh_lday.is_dir() or sz_lday.is_dir():
                day_files = list(sh_lday.glob("*.day")) + list(sz_lday.glob("*.day"))
                if len(day_files) >= min_stocks:
                    return "tdx"
        if self.klines_dir.is_dir():
            json_files = list(self.klines_dir.glob("*.json"))
            if len(json_files) >= min_stocks:
                return "json_cache"
        return None

    def has_local_data(self) -> bool:
        return self._source is not None

    def get_source_info(self) -> str:
        if self._source == "tdx":
            return f"TDX ({self.tdx_path})"
        elif self._source == "json_cache":
            count = len(list(self.klines_dir.glob("*.json")))
            return f"JSON缓存 ({self.klines_dir}, {count}只)"
        return "无本地数据"

    def get_stock_list(self) -> dict:
        """返回 {code: name}"""
        list_file = self.cache_dir / "stock_list.json"
        if list_file.exists():
            with open(list_file, encoding="utf-8") as f:
                return json.load(f)
        if self._source == "tdx":
            return self._tdx_stock_list()
        if self._source == "json_cache":
            return self._cache_stock_list()
        return {}

    def get_klines(self, code: str, days: int = 70) -> list:
        if self._source == "tdx":
            return self._tdx_get_klines(code, days)
        elif self._source == "json_cache":
            return self._cache_get_klines(code, days)
        return []

    def get_all_klines(self, days: int = 70) -> dict:
        """返回 {code: [kline_records]}"""
        result = {}
        if self._source == "tdx":
            result = self._tdx_get_all(days)
        elif self._source == "json_cache":
            result = self._cache_get_all(days)
        return result

    # ---- TDX backend ----

    def _tdx_stock_list(self):
        stocks = {}
        p = Path(self.tdx_path)
        for market_dir in ["sh/lday", "sz/lday"]:
            d = p / market_dir
            if not d.is_dir():
                continue
            for f in d.glob("*.day"):
                code = f.stem.replace("sh", "").replace("sz", "")
                if self._is_valid_stock_code(code):
                    stocks[code] = ""
        return stocks

    def _tdx_get_klines(self, code, days):
        filepath = self._tdx_find_file(code)
        if not filepath:
            return []
        records = read_tdx_day(filepath)
        return records[-days:] if days and len(records) > days else records

    def _tdx_get_all(self, days):
        result = {}
        p = Path(self.tdx_path)
        for prefix, market_dir in [("sz", "sz/lday"), ("sh", "sh/lday")]:
            d = p / market_dir
            if not d.is_dir():
                continue
            for f in d.glob("*.day"):
                code = f.stem.replace("sh", "").replace("sz", "")
                if not self._is_valid_stock_code(code):
                    continue
                records = read_tdx_day(str(f))
                if records:
                    result[code] = records[-days:] if days and len(records) > days else records
        return result

    def _tdx_find_file(self, code):
        p = Path(self.tdx_path)
        exchange = "sh" if code.startswith("6") else "sz"
        f = p / exchange / "lday" / f"{exchange}{code}.day"
        if f.exists():
            return str(f)
        for market in ["sh/lday", "sz/lday"]:
            for candidate in (p / market).glob(f"*{code}.day"):
                return str(candidate)
        return None

    # ---- JSON cache backend ----

    def _cache_stock_list(self):
        stocks = {}
        for f in self.klines_dir.glob("*.json"):
            code = f.stem
            if not self._is_valid_stock_code(code):
                continue
            try:
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                stocks[code] = data.get("name", "")
            except Exception:
                stocks[code] = ""
        return stocks

    def _cache_get_klines(self, code, days):
        f = self.klines_dir / f"{code}.json"
        if not f.exists():
            return []
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            klines = data.get("klines", [])
            return klines[-days:] if days and len(klines) > days else klines
        except Exception:
            return []

    def _cache_get_all(self, days):
        result = {}
        for f in self.klines_dir.glob("*.json"):
            code = f.stem
            if not self._is_valid_stock_code(code):
                continue
            try:
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                klines = data.get("klines", [])
                if klines:
                    result[code] = klines[-days:] if days and len(klines) > days else klines
            except Exception:
                continue
        return result

    # ---- helpers ----

    @staticmethod
    def _is_valid_stock_code(code: str) -> bool:
        if not code or len(code) != 6 or not code.isdigit():
            return False
        if code.startswith("6") or code.startswith("0") or code.startswith("3"):
            return True
        return False

    def save_kline(self, code: str, name: str, klines: list):
        """保存单只股票K线到JSON缓存"""
        self.klines_dir.mkdir(parents=True, exist_ok=True)
        f = self.klines_dir / f"{code}.json"
        data = {"code": code, "name": name, "klines": klines}
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)

    def append_daily(self, code: str, daily_record: dict):
        """追加一条日线记录到缓存"""
        f = self.klines_dir / f"{code}.json"
        if not f.exists():
            return
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            existing_dates = {k["date"] for k in data.get("klines", [])}
            if daily_record["date"] not in existing_dates:
                data["klines"].append(daily_record)
                max_keep = self.config.get("klines_days", 70) + 30
                if len(data["klines"]) > max_keep:
                    data["klines"] = data["klines"][-max_keep:]
                with open(f, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False)
        except Exception:
            pass

    def save_stock_list(self, stock_dict: dict):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_dir / "stock_list.json", "w", encoding="utf-8") as f:
            json.dump(stock_dict, f, ensure_ascii=False, indent=2)

    def update_sync_meta(self, **kwargs):
        meta_file = self.cache_dir / "last_sync.json"
        meta = {}
        if meta_file.exists():
            with open(meta_file, encoding="utf-8") as f:
                meta = json.load(f)
        meta.update(kwargs)
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def get_sync_meta(self) -> dict:
        meta_file = self.cache_dir / "last_sync.json"
        if meta_file.exists():
            with open(meta_file, encoding="utf-8") as f:
                return json.load(f)
        return {}


if __name__ == "__main__":
    provider = DataProvider()
    print(f"数据源: {provider.get_source_info()}")
    print(f"有本地数据: {provider.has_local_data()}")
    if provider.has_local_data():
        stocks = provider.get_stock_list()
        print(f"股票数量: {len(stocks)}")
        if stocks:
            sample_code = list(stocks.keys())[0]
            klines = provider.get_klines(sample_code, 5)
            print(f"示例 {sample_code}: {len(klines)} 条K线")
            if klines:
                print(f"  最新: {klines[-1]}")
