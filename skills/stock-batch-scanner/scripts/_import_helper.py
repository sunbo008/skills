"""
安全导入 stock-anomaly-analysis 的 fetch_stock_data 模块。
该模块在顶层重新包装 sys.stdout/stderr，直接导入会破坏调用者的IO。
用 /dev/null 做临时替身，导入完成后恢复。
"""

import sys
import os
from pathlib import Path

ANOMALY_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "stock-anomaly-analysis" / "scripts"


def _safe_import_fetch_stock_data():
    saved_stdout = sys.stdout
    saved_stderr = sys.stderr
    devnull = open(os.devnull, "w")
    sys.stdout = devnull
    sys.stderr = devnull

    sys.path.insert(0, str(ANOMALY_SCRIPTS))
    try:
        import fetch_stock_data as mod
        return mod
    finally:
        sys.stdout = saved_stdout
        sys.stderr = saved_stderr
        devnull.close()


_mod = _safe_import_fetch_stock_data()

fetch_kline_eastmoney = _mod.fetch_kline_eastmoney
get_exchange_prefix = _mod.get_exchange_prefix
fetch_realtime_quote_tencent = _mod.fetch_realtime_quote_tencent
calculate_technical_indicators = _mod.calculate_technical_indicators
