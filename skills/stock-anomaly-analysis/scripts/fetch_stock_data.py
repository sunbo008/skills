#!/usr/bin/env python3
"""
股票数据获取脚本
数据来源：腾讯财经、东方财富
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import json
import re
from datetime import datetime
import argparse


def get_exchange_prefix(stock_code: str) -> tuple[str, str]:
    """根据股票代码判断交易所前缀"""
    code = stock_code.replace('.SZ', '').replace('.SH', '').replace('.sz', '').replace('.sh', '')
    
    if code.startswith('6'):
        return 'sh', code  # 上交所
    elif code.startswith(('0', '3')):
        return 'sz', code  # 深交所
    elif code.startswith('8') or code.startswith('4'):
        return 'bj', code  # 北交所
    else:
        return 'sz', code  # 默认深交所


def fetch_realtime_quote_tencent(stock_code: str) -> dict:
    """
    从腾讯财经获取实时行情
    接口: https://qt.gtimg.cn/q=sz002195
    """
    exchange, code = get_exchange_prefix(stock_code)
    url = f"https://qt.gtimg.cn/q={exchange}{code}"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = 'gbk'
        text = resp.text
        
        # 解析返回数据: v_sz002195="..."
        match = re.search(r'"([^"]+)"', text)
        if not match:
            return {"error": "无法解析数据", "raw": text}
        
        fields = match.group(1).split('~')
        if len(fields) < 50:
            return {"error": "数据字段不完整", "raw": text}
        
        # 字段含义参考: https://blog.csdn.net/lgddb00000/article/details/78688420
        return {
            "source": "腾讯财经",
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": fields[1],
            "code": fields[2],
            "price": float(fields[3]) if fields[3] else 0,
            "prev_close": float(fields[4]) if fields[4] else 0,
            "open": float(fields[5]) if fields[5] else 0,
            "volume": int(fields[6]) if fields[6] else 0,  # 成交量(手)
            "buy_volume": int(fields[7]) if fields[7] else 0,  # 外盘
            "sell_volume": int(fields[8]) if fields[8] else 0,  # 内盘
            "bid1_price": float(fields[9]) if fields[9] else 0,
            "bid1_volume": int(fields[10]) if fields[10] else 0,
            "change": float(fields[31]) if fields[31] else 0,  # 涨跌额
            "change_pct": float(fields[32]) if fields[32] else 0,  # 涨跌幅%
            "high": float(fields[33]) if fields[33] else 0,
            "low": float(fields[34]) if fields[34] else 0,
            "amount": float(fields[37]) if fields[37] else 0,  # 成交额(万)
            "turnover": float(fields[38]) if fields[38] else 0,  # 换手率%
            "pe": float(fields[39]) if fields[39] else 0,  # 市盈率
            "amplitude": float(fields[43]) if fields[43] else 0,  # 振幅%
            "circulating_market_cap": float(fields[44]) if fields[44] else 0,  # 流通市值(亿)
            "total_market_cap": float(fields[45]) if fields[45] else 0,  # 总市值(亿)
            "pb": float(fields[46]) if fields[46] else 0,  # 市净率
            "limit_up": float(fields[47]) if fields[47] else 0,  # 涨停价
            "limit_down": float(fields[48]) if fields[48] else 0,  # 跌停价
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_fund_flow_eastmoney(stock_code: str) -> dict:
    """
    从东方财富获取资金流向
    接口: https://push2.eastmoney.com/api/qt/stock/fflow/kline/get
    """
    exchange, code = get_exchange_prefix(stock_code)
    secid = f"0.{code}" if exchange == 'sz' else f"1.{code}"
    
    url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "klt": 1,  # 日级别
        "lmt": 1,  # 最近1条
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('data') and data['data'].get('klines'):
            kline = data['data']['klines'][-1].split(',')
            return {
                "source": "东方财富",
                "date": kline[0],
                "main_net": float(kline[1]) / 10000 if kline[1] else 0,  # 主力净流入(万->亿)
                "small_net": float(kline[2]) / 10000 if kline[2] else 0,  # 小单净流入
                "mid_net": float(kline[3]) / 10000 if kline[3] else 0,  # 中单净流入
                "big_net": float(kline[4]) / 10000 if kline[4] else 0,  # 大单净流入
                "super_big_net": float(kline[5]) / 10000 if kline[5] else 0,  # 超大单净流入
            }
        return {"error": "无数据"}
    except Exception as e:
        return {"error": str(e)}


def fetch_dragon_tiger_eastmoney(stock_code: str, date: str = None) -> dict:
    """
    从东方财富获取龙虎榜数据
    接口: https://datacenter-web.eastmoney.com/api/data/v1/get
    """
    exchange, code = get_exchange_prefix(stock_code)
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
        "columns": "ALL",
        "filter": f"(SECURITY_CODE=\"{code}\")(TRADE_DATE='{date}')",
        "pageNumber": 1,
        "pageSize": 50,
        "sortTypes": -1,
        "sortColumns": "BUY",
        "source": "WEB",
        "client": "WEB",
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('result') and data['result'].get('data'):
            records = data['result']['data']
            buy_seats = []
            sell_seats = []
            
            for r in records:
                seat_info = {
                    "name": r.get('OPERATEDEPT_NAME', ''),
                    "buy": r.get('BUY', 0),
                    "sell": r.get('SELL', 0),
                    "net": r.get('NET', 0),
                }
                if seat_info['buy'] > 0:
                    buy_seats.append(seat_info)
                if seat_info['sell'] > 0:
                    sell_seats.append(seat_info)
            
            # 取第一条记录的原因
            reason = records[0].get('EXPLANATION', '') if records else ''
            
            return {
                "source": "东方财富",
                "date": date,
                "reason": reason,
                "buy_seats": sorted(buy_seats, key=lambda x: x['buy'], reverse=True)[:5],
                "sell_seats": sorted(sell_seats, key=lambda x: x['sell'], reverse=True)[:5],
            }
        return {"error": "该日期无龙虎榜数据", "date": date}
    except Exception as e:
        return {"error": str(e)}


def fetch_kline_eastmoney(stock_code: str, period: str = "daily", limit: int = 30) -> dict:
    """
    从东方财富获取K线数据
    period: daily/weekly/monthly
    """
    exchange, code = get_exchange_prefix(stock_code)
    secid = f"0.{code}" if exchange == 'sz' else f"1.{code}"
    
    klt_map = {"daily": 101, "weekly": 102, "monthly": 103}
    klt = klt_map.get(period, 101)
    
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": klt,
        "fqt": 1,  # 前复权
        "end": "20500101",
        "lmt": limit,
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('data') and data['data'].get('klines'):
            klines = []
            for k in data['data']['klines']:
                fields = k.split(',')
                klines.append({
                    "date": fields[0],
                    "open": float(fields[1]),
                    "close": float(fields[2]),
                    "high": float(fields[3]),
                    "low": float(fields[4]),
                    "volume": int(fields[5]),
                    "amount": float(fields[6]),
                    "amplitude": float(fields[7]),  # 振幅%
                    "change_pct": float(fields[8]),  # 涨跌幅%
                    "change": float(fields[9]),  # 涨跌额
                    "turnover": float(fields[10]),  # 换手率%
                })
            
            return {
                "source": "东方财富",
                "code": code,
                "name": data['data'].get('name', ''),
                "period": period,
                "klines": klines,
            }
        return {"error": "无数据"}
    except Exception as e:
        return {"error": str(e)}


def fetch_market_indices() -> dict:
    """
    获取大盘核心指数数据
    通过腾讯财经接口批量获取
    """
    # 指数代码映射
    index_map = {
        "shanghai":  ("sh000001", "上证指数"),
        "shenzhen":  ("sz399001", "深证成指"),
        "chinext":   ("sz399006", "创业板指"),
        "sz50":      ("sh000016", "上证50"),
        "hs300":     ("sh000300", "沪深300"),
        "csi500":    ("sh000905", "中证500"),
        "csi1000":   ("sh000852", "中证1000"),
    }
    
    # 批量请求
    codes = ",".join([v[0] for v in index_map.values()])
    url = f"https://qt.gtimg.cn/q={codes}"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.encoding = 'gbk'
        text = resp.text
        
        result = {
            "source": "腾讯财经",
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "indices": {},
        }
        
        # 按行解析每个指数
        lines = [line.strip() for line in text.split(';') if line.strip()]
        
        idx = 0
        for key, (code, name) in index_map.items():
            if idx >= len(lines):
                break
            line = lines[idx]
            idx += 1
            
            match = re.search(r'"([^"]+)"', line)
            if not match:
                result["indices"][key] = {"name": name, "error": "解析失败"}
                continue
            
            fields = match.group(1).split('~')
            if len(fields) < 45:
                result["indices"][key] = {"name": name, "error": "数据不完整"}
                continue
            
            result["indices"][key] = {
                "name": fields[1] if fields[1] else name,
                "price": float(fields[3]) if fields[3] else 0,
                "prev_close": float(fields[4]) if fields[4] else 0,
                "change": float(fields[31]) if fields[31] else 0,
                "change_pct": float(fields[32]) if fields[32] else 0,
                "high": float(fields[33]) if fields[33] else 0,
                "low": float(fields[34]) if fields[34] else 0,
                "volume": int(fields[6]) if fields[6] else 0,
                "amount": float(fields[37]) if fields[37] else 0,
            }
        
        # 市场风格判断
        sz50_pct = result["indices"].get("sz50", {}).get("change_pct", 0)
        csi1000_pct = result["indices"].get("csi1000", {}).get("change_pct", 0)
        shanghai_pct = result["indices"].get("shanghai", {}).get("change_pct", 0)
        chinext_pct = result["indices"].get("chinext", {}).get("change_pct", 0)
        
        if sz50_pct > csi1000_pct + 0.5:
            style = "大盘价值"
        elif csi1000_pct > sz50_pct + 0.5:
            style = "小盘成长"
        else:
            style = "均衡"
        
        # 简单环境评估
        all_pcts = [v.get("change_pct", 0) for v in result["indices"].values() if isinstance(v, dict) and "change_pct" in v]
        avg_pct = sum(all_pcts) / len(all_pcts) if all_pcts else 0
        up_count = sum(1 for p in all_pcts if p > 0)
        
        if avg_pct > 1.5 and up_count >= 6:
            status = "强势"
        elif avg_pct > 0.5 and up_count >= 4:
            status = "偏强"
        elif avg_pct > -0.5:
            status = "震荡"
        elif avg_pct > -1.5:
            status = "偏弱"
        else:
            status = "弱势"
        
        result["style"] = style
        result["overall_status"] = status
        result["avg_change_pct"] = round(avg_pct, 2)
        
        return result
    except Exception as e:
        return {"error": str(e)}


def calculate_temperature_history(stock_klines: list, index_klines: list) -> dict:
    """
    基于真实K线数据程序化计算每日市场温度
    
    算法: 5维度加权
      ① 个股涨跌幅 (30%): score = clamp(50 + change_pct * 5, 0, 100)
      ② 换手率活跃度 (20%): score = clamp(30 + (turnover/avg_turnover) * 25, 0, 100)
      ③ 大盘联动 (20%): score = clamp(50 + index_change_pct * 15, 0, 100)
      ④ 3日动量均值 (15%): score = clamp(50 + avg_3d_change * 5, 0, 100)
      ⑤ 波幅方向 (15%): 涨时 clamp(50 + amplitude * 3), 跌时 clamp(50 - amplitude * 3)
    
    返回:
      {
        "source": "程序化计算(fetch_stock_data.py)",
        "algorithm": "5维度加权: 涨跌幅30%+换手率20%+大盘联动20%+3日动量15%+波幅方向15%",
        "data_basis": "东方财富K线API(个股+上证指数)",
        "trading_days_count": N,
        "history": [{"date": "MM-DD", "value": int, "label": str, "detail": str}, ...]
      }
    """
    if not stock_klines or not index_klines:
        return {"error": "K线数据不可用，无法计算温度历史"}
    
    # 构建大盘指数日期→数据映射
    idx_map = {}
    for k in index_klines:
        idx_map[k["date"]] = k
    
    # 计算平均换手率(用于归一化)
    turnovers = [k.get("turnover", 0) for k in stock_klines]
    avg_turnover = sum(turnovers) / len(turnovers) if turnovers else 1
    
    def clamp(val, lo=0, hi=100):
        return max(lo, min(hi, val))
    
    history = []
    for i, s in enumerate(stock_klines):
        date_str = s["date"]  # 真实交易日，来自API
        chg = s.get("change_pct", 0)
        turnover = s.get("turnover", 0)
        amplitude = s.get("amplitude", 0)
        
        # 大盘当日数据
        idx = idx_map.get(date_str, {})
        idx_chg = idx.get("change_pct", 0)
        
        # ① 个股涨跌幅 (30%)
        f1 = clamp(50 + chg * 5)
        
        # ② 换手率活跃度 (20%)
        vol_ratio = turnover / avg_turnover if avg_turnover > 0 else 1
        f2 = clamp(30 + vol_ratio * 25)
        
        # ③ 大盘联动 (20%)
        f3 = clamp(50 + idx_chg * 15)
        
        # ④ 3日动量均值 (15%)
        if i >= 2:
            mom3 = sum(stock_klines[j].get("change_pct", 0) for j in range(max(0, i-2), i+1)) / 3
        else:
            mom3 = chg
        f4 = clamp(50 + mom3 * 5)
        
        # ⑤ 波幅方向 (15%)
        if chg >= 0:
            f5 = clamp(50 + amplitude * 3)
        else:
            f5 = clamp(50 - amplitude * 3)
        
        # 加权合成
        temp = f1 * 0.30 + f2 * 0.20 + f3 * 0.20 + f4 * 0.15 + f5 * 0.15
        temp = round(max(5, min(95, temp)))
        
        # 自动生成事件标签(仅基于可观察的K线特征)
        label = ""
        if chg >= 9.9:
            label = "涨停"
        elif chg <= -9.9:
            label = "跌停"
        elif turnover > avg_turnover * 3:
            label = f"天量{turnover:.0f}%"
        elif turnover < avg_turnover * 0.4 and chg < -1:
            label = "缩量下跌"
        elif idx_chg < -1.5:
            label = "大盘暴跌"
        elif idx_chg > 1.2 and chg > 3:
            label = "大盘反弹"
        
        # 连板检测
        if chg >= 9.9 and i > 0 and stock_klines[i-1].get("change_pct", 0) >= 9.9:
            prev_count = 1
            for j in range(i-1, -1, -1):
                if stock_klines[j].get("change_pct", 0) >= 9.9:
                    prev_count += 1
                else:
                    break
            if prev_count >= 2:
                label = f"{prev_count}连板"
        
        # 格式化日期为 MM-DD
        date_short = date_str[5:] if len(date_str) >= 10 else date_str
        
        # 详情字段(用于数据溯源)
        detail = f"涨跌:{chg:+.2f}% 换手:{turnover:.1f}% 振幅:{amplitude:.1f}% 大盘:{idx_chg:+.2f}%"
        
        history.append({
            "date": date_short,
            "value": temp,
            "label": label,
            "detail": detail,
        })
    
    return {
        "source": "程序化计算(fetch_stock_data.py)",
        "algorithm": "5维度加权: 涨跌幅30%+换手率20%+大盘联动20%+3日动量15%+波幅方向15%",
        "data_basis": "东方财富K线API(个股+上证指数)",
        "trading_days_count": len(history),
        "avg_turnover_pct": round(avg_turnover, 2),
        "history": history,
    }


def fetch_all_data(stock_code: str) -> dict:
    """获取股票全部数据"""
    print(f"📊 正在获取 {stock_code} 的数据...")
    
    result = {
        "stock_code": stock_code,
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # 1. 实时行情
    print("  → 获取实时行情 (腾讯财经)...")
    result["realtime"] = fetch_realtime_quote_tencent(stock_code)
    
    # 2. 资金流向
    print("  → 获取资金流向 (东方财富)...")
    result["fund_flow"] = fetch_fund_flow_eastmoney(stock_code)
    
    # 3. 龙虎榜
    print("  → 获取龙虎榜数据 (东方财富)...")
    result["dragon_tiger"] = fetch_dragon_tiger_eastmoney(stock_code)
    
    # 4. 近期K线(30个交易日,用于温度历史计算)
    print("  → 获取近期K线 (东方财富, 30日)...")
    result["klines"] = fetch_kline_eastmoney(stock_code, "daily", 30)
    
    # 5. 大盘指数K线(同期, 用于温度历史计算)
    print("  → 获取上证指数K线 (东方财富, 30日)...")
    result["index_klines"] = fetch_kline_eastmoney("sh000001", "daily", 30)
    
    # 6. 程序化计算温度历史(基于真实K线数据)
    stock_k = result["klines"].get("klines", []) if isinstance(result["klines"], dict) else []
    index_k = result["index_klines"].get("klines", []) if isinstance(result["index_klines"], dict) else []
    if stock_k and index_k:
        print("  → 程序化计算温度历史 (基于K线数据)...")
        result["temperature_history"] = calculate_temperature_history(stock_k, index_k)
        print(f"    ✓ 计算完成: {result['temperature_history']['trading_days_count']}个交易日温度数据")
    else:
        print("  ⚠ K线数据不可用，跳过温度历史计算")
        result["temperature_history"] = {"error": "K线数据不可用"}
    
    return result


def main():
    parser = argparse.ArgumentParser(description='获取股票实时数据')
    parser.add_argument('stock_code', nargs='?', default=None, help='股票代码，如 002195 或 sz002195')
    parser.add_argument('--output', '-o', help='输出JSON文件路径')
    parser.add_argument('--realtime', action='store_true', help='仅获取实时行情')
    parser.add_argument('--fund', action='store_true', help='仅获取资金流向')
    parser.add_argument('--lhb', action='store_true', help='仅获取龙虎榜')
    parser.add_argument('--kline', action='store_true', help='仅获取K线')
    parser.add_argument('--temperature', action='store_true', help='计算并输出温度历史(基于K线数据)')
    parser.add_argument('--market', action='store_true', help='获取大盘指数数据(无需股票代码)')
    
    args = parser.parse_args()
    
    # 大盘指数模式
    if args.market:
        print("📈 正在获取大盘指数数据...")
        data = fetch_market_indices()
    elif not args.stock_code:
        parser.error("请提供股票代码，或使用 --market 获取大盘数据")
        return
    else:
        stock_code = args.stock_code
        
        # 单独获取某类数据
        if args.realtime:
            data = fetch_realtime_quote_tencent(stock_code)
        elif args.fund:
            data = fetch_fund_flow_eastmoney(stock_code)
        elif args.lhb:
            data = fetch_dragon_tiger_eastmoney(stock_code)
        elif args.kline:
            data = fetch_kline_eastmoney(stock_code)
        elif args.temperature:
            print(f"🌡️ 计算 {stock_code} 温度历史...")
            print("  → 获取个股K线 (30日)...")
            sk = fetch_kline_eastmoney(stock_code, "daily", 30)
            print("  → 获取上证指数K线 (30日)...")
            ik = fetch_kline_eastmoney("sh000001", "daily", 30)
            stock_k = sk.get("klines", []) if isinstance(sk, dict) else []
            index_k = ik.get("klines", []) if isinstance(ik, dict) else []
            if stock_k and index_k:
                data = calculate_temperature_history(stock_k, index_k)
            else:
                data = {"error": "K线数据获取失败，无法计算温度"}
        else:
            data = fetch_all_data(stock_code)
    
    # 输出
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_str)
        print(f"✅ 数据已保存至: {args.output}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()
