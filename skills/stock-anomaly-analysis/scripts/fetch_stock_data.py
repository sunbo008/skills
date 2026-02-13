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


# ============================================================
# 板块联动分析 (新增)
# ============================================================

def get_eastmoney_secid(stock_code: str) -> str:
    """获取东方财富格式的secid"""
    exchange, code = get_exchange_prefix(stock_code)
    return f"0.{code}" if exchange == 'sz' else f"1.{code}"


def fetch_stock_sectors_eastmoney(stock_code: str) -> dict:
    """
    从东方财富获取个股所属概念板块和行业板块
    接口: https://datacenter-web.eastmoney.com/api/data/v1/get
    """
    exchange, code = get_exchange_prefix(stock_code)
    
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    params = {
        "reportName": "RPT_F10_CORETHEME_BJHANGYE",
        "columns": "ALL",
        "filter": f'(SECURITY_CODE="{code}")',
        "pageNumber": 1,
        "pageSize": 50,
        "source": "HSF10",
        "client": "WEB",
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('result') and data['result'].get('data'):
            sectors = []
            for item in data['result']['data']:
                sectors.append({
                    "name": item.get('BOARD_NAME', ''),
                    "code": item.get('BOARD_CODE', ''),
                    "rank": item.get('BOARD_RANK', 0),
                    "is_precise": item.get('IS_PRECISE', 0),
                    "board_type": item.get('BOARD_TYPE', ''),
                })
            return {
                "source": "东方财富",
                "stock_code": code,
                "sectors": sectors,
            }
        return {"error": "无板块数据", "sectors": []}
    except Exception as e:
        return {"error": str(e), "sectors": []}


def fetch_sector_stocks_eastmoney(sector_code: str, limit: int = 50) -> dict:
    """
    获取板块成分股，按今日涨跌幅降序排列
    接口: https://push2.eastmoney.com/api/qt/clist/get
    """
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": limit,
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f21",
        "fs": f"b:{sector_code}",
        "fid": "f3",
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('data') and data['data'].get('diff'):
            stocks = []
            for item in data['data']['diff']:
                stocks.append({
                    "code": str(item.get('f12', '')),
                    "name": item.get('f14', ''),
                    "price": item.get('f2', 0),
                    "change_pct": item.get('f3', 0),
                    "change": item.get('f4', 0),
                    "turnover": item.get('f8', 0),
                    "pe": item.get('f9', 0),
                    "market_cap": item.get('f20', 0),
                })
            total = data['data'].get('total', len(stocks))
            return {
                "source": "东方财富",
                "sector_code": sector_code,
                "total_stocks": total,
                "stocks": stocks,
            }
        return {"error": "无成分股数据", "stocks": []}
    except Exception as e:
        return {"error": str(e), "stocks": []}


def fetch_hot_sectors_eastmoney(sector_type: str = "concept", limit: int = 20) -> dict:
    """
    获取今日热门板块排行
    sector_type: "concept" 概念板块, "industry" 行业板块
    """
    fs_map = {
        "concept": "m:90+t:3",
        "industry": "m:90+t:2",
    }
    
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": 1,
        "pz": limit,
        "po": 1,
        "np": 1,
        "fltt": 2,
        "invt": 2,
        "fields": "f2,f3,f4,f12,f14,f104,f105,f128,f136,f140,f141",
        "fs": fs_map.get(sector_type, fs_map["concept"]),
        "fid": "f3",
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('data') and data['data'].get('diff'):
            sectors = []
            for item in data['data']['diff']:
                sectors.append({
                    "code": item.get('f12', ''),
                    "name": item.get('f14', ''),
                    "change_pct": item.get('f3', 0),
                    "up_count": item.get('f104', 0),
                    "down_count": item.get('f105', 0),
                    "leading_stock_name": item.get('f140', ''),
                    "leading_stock_code": item.get('f141', ''),
                })
            return {
                "source": "东方财富",
                "type": sector_type,
                "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sectors": sectors,
            }
        return {"error": "无板块数据", "sectors": []}
    except Exception as e:
        return {"error": str(e), "sectors": []}


def analyze_sector_position(stock_code: str, sector_name: str, sector_stocks: dict) -> dict:
    """
    分析个股在板块中的身位 (龙头/前排/中军/后排/掉队)
    """
    exchange, code = get_exchange_prefix(stock_code)
    stocks = sector_stocks.get("stocks", [])
    total = len(stocks)
    
    if total == 0:
        return {"error": "无成分股数据"}
    
    rank = None
    target_data = None
    for i, s in enumerate(stocks):
        if str(s["code"]) == code:
            rank = i + 1
            target_data = s
            break
    
    if rank is None:
        return {"error": "未在板块成分股中找到该股票", "sector_name": sector_name}
    
    ratio = rank / total
    if ratio <= 0.05:
        position, position_emoji = "龙头", "🏆"
        position_detail = f"板块涨幅第{rank}/{total}名，处于绝对领涨位置"
    elif ratio <= 0.2:
        position, position_emoji = "前排", "🔴"
        position_detail = f"板块涨幅第{rank}/{total}名，属于板块领涨梯队"
    elif ratio <= 0.5:
        position, position_emoji = "中军", "🟡"
        position_detail = f"板块涨幅第{rank}/{total}名，与板块整体走势基本同步"
    elif ratio <= 0.8:
        position, position_emoji = "后排", "🔵"
        position_detail = f"板块涨幅第{rank}/{total}名，弱于板块整体表现"
    else:
        position, position_emoji = "掉队", "⚪"
        position_detail = f"板块涨幅第{rank}/{total}名，明显落后于板块大部分个股"
    
    leading = stocks[:5]
    mid_start = max(0, total // 2 - 2)
    mid_stocks = stocks[mid_start:mid_start + 5]
    lagging = list(reversed(stocks[-5:])) if total > 5 else []
    
    valid_changes = [s["change_pct"] for s in stocks
                     if isinstance(s.get("change_pct"), (int, float)) and s["change_pct"] != 0]
    sector_avg = round(sum(valid_changes) / len(valid_changes), 2) if valid_changes else 0
    
    limit_up_count = sum(1 for s in stocks if isinstance(s.get("change_pct"), (int, float)) and s["change_pct"] >= 9.9)
    limit_down_count = sum(1 for s in stocks if isinstance(s.get("change_pct"), (int, float)) and s["change_pct"] <= -9.9)
    up_count = sum(1 for s in stocks if isinstance(s.get("change_pct"), (int, float)) and s["change_pct"] > 0)
    down_count = sum(1 for s in stocks if isinstance(s.get("change_pct"), (int, float)) and s["change_pct"] < 0)
    
    stock_change = target_data["change_pct"] if target_data else 0
    diff = stock_change - sector_avg
    
    if abs(diff) < 1:
        independence = "弱"
        independence_conclusion = f"与板块走势高度同步 (板块均涨{sector_avg}%, 个股涨{stock_change}%)"
    elif diff > 5:
        independence = "极强-正向"
        independence_conclusion = f"远超板块表现 (板块均涨{sector_avg}%, 个股涨{stock_change}%), 走出独立强势行情"
    elif diff > 2:
        independence = "强-正向"
        independence_conclusion = f"明显强于板块 (板块均涨{sector_avg}%, 个股涨{stock_change}%)"
    elif diff > 1:
        independence = "中-正向"
        independence_conclusion = f"略强于板块 (板块均涨{sector_avg}%, 个股涨{stock_change}%)"
    elif diff < -5:
        independence = "极强-负向"
        independence_conclusion = f"远逊板块表现 (板块均涨{sector_avg}%, 个股涨{stock_change}%), 需警惕个股风险"
    elif diff < -2:
        independence = "强-负向"
        independence_conclusion = f"明显弱于板块 (板块均涨{sector_avg}%, 个股涨{stock_change}%)"
    else:
        independence = "中-负向"
        independence_conclusion = f"略弱于板块 (板块均涨{sector_avg}%, 个股涨{stock_change}%)"
    
    def simplify(s):
        return {"code": s["code"], "name": s["name"], "change_pct": s["change_pct"]}
    
    return {
        "sector_name": sector_name,
        "rank": rank,
        "total": total,
        "position": position,
        "position_emoji": position_emoji,
        "position_detail": position_detail,
        "sector_avg_change": sector_avg,
        "stock_change": stock_change,
        "up_count": up_count,
        "down_count": down_count,
        "limit_up_count": limit_up_count,
        "limit_down_count": limit_down_count,
        "independence": independence,
        "independence_conclusion": independence_conclusion,
        "leading_stocks": [simplify(s) for s in leading],
        "mid_stocks": [simplify(s) for s in mid_stocks],
        "lagging_stocks": [simplify(s) for s in lagging],
    }


def calculate_technical_indicators(klines_data: dict) -> dict:
    """从K线数据计算技术指标(均线、趋势、量价关系、支撑压力)"""
    klines = klines_data.get("klines", [])
    if not klines or len(klines) < 5:
        return {"error": "K线数据不足"}
    
    closes = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]
    current = closes[-1]
    
    def ma(data, period):
        if len(data) < period:
            return None
        return round(sum(data[-period:]) / period, 3)
    
    ma5, ma10, ma20, ma60 = ma(closes, 5), ma(closes, 10), ma(closes, 20), ma(closes, 60)
    
    valid_mas = [(n, v) for n, v in [("MA5", ma5), ("MA10", ma10), ("MA20", ma20), ("MA60", ma60)] if v is not None]
    if len(valid_mas) >= 3:
        values = [v for _, v in valid_mas]
        if all(values[i] >= values[i+1] for i in range(len(values)-1)):
            ma_alignment = "多头排列"
        elif all(values[i] <= values[i+1] for i in range(len(values)-1)):
            ma_alignment = "空头排列"
        else:
            ma_alignment = "均线交叉缠绕"
    else:
        ma_alignment = "数据不足"
    
    avg_vol_5 = sum(volumes[-5:]) / 5
    today_vol_ratio = round(volumes[-1] / avg_vol_5, 2) if avg_vol_5 > 0 else 1.0
    
    recent_change = klines[-1]["change_pct"]
    if recent_change > 0 and today_vol_ratio > 1.3:
        volume_price = "放量上涨，量价配合良好"
    elif recent_change > 0 and today_vol_ratio < 0.7:
        volume_price = "缩量上涨，上攻动力不足"
    elif recent_change < 0 and today_vol_ratio > 1.3:
        volume_price = "放量下跌，抛压较重"
    elif recent_change < 0 and today_vol_ratio < 0.7:
        volume_price = "缩量下跌，恐慌消退"
    else:
        volume_price = "量价关系中性"
    
    recent_klines = klines[-min(20, len(klines)):]
    resistance = sorted(set(round(k["high"], 2) for k in recent_klines if k["high"] > current * 1.005), reverse=True)[:3]
    support = sorted(set(round(k["low"], 2) for k in recent_klines if k["low"] < current * 0.995))[:3]
    resistance.sort()
    support.sort(reverse=True)
    
    short_t = closes[-1] - closes[-5] if len(closes) >= 5 else 0
    mid_t = closes[-1] - closes[-20] if len(closes) >= 20 else short_t
    if short_t > 0 and mid_t > 0:
        trend = "上升趋势"
    elif short_t < 0 and mid_t < 0:
        trend = "下降趋势"
    elif short_t > 0:
        trend = "反弹修复"
    elif short_t <= 0 and mid_t > 0:
        trend = "高位回调"
    else:
        trend = "震荡整理"
    
    consecutive = 0
    direction = None
    for k in reversed(klines):
        if direction is None:
            direction = "up" if k["change_pct"] >= 0 else "down"
        if (direction == "up" and k["change_pct"] >= 0) or (direction == "down" and k["change_pct"] < 0):
            consecutive += 1
        else:
            break
    
    def period_change(n):
        if len(closes) >= n + 1:
            return round((closes[-1] / closes[-(n+1)] - 1) * 100, 2)
        return None
    
    return {
        "current_price": current,
        "ma5": ma5, "ma10": ma10, "ma20": ma20, "ma60": ma60,
        "ma_alignment": ma_alignment,
        "volume_price": volume_price,
        "today_vol_ratio": today_vol_ratio,
        "support_levels": support,
        "resistance_levels": resistance,
        "trend": trend,
        "consecutive_days": consecutive,
        "consecutive_direction": "涨" if direction == "up" else "跌",
        "change_5d": period_change(5),
        "change_10d": period_change(10),
        "change_20d": period_change(20),
    }


def fetch_all_data(stock_code: str) -> dict:
    """获取股票全部数据 (含板块联动和技术指标)"""
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
    
    # 4. 近期K线(70个交易日,用于温度历史和技术指标计算)
    print("  → 获取近期K线 (东方财富, 70日)...")
    result["klines"] = fetch_kline_eastmoney(stock_code, "daily", 70)
    
    # 5. 大盘指数K线(同期, 用于温度历史计算)
    print("  → 获取上证指数K线 (东方财富, 70日)...")
    result["index_klines"] = fetch_kline_eastmoney("sh000001", "daily", 70)
    
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
    
    # 7. 技术指标计算 (基于K线)
    print("  → 计算技术指标...")
    if not result["klines"].get("error"):
        result["technical"] = calculate_technical_indicators(result["klines"])
    else:
        result["technical"] = {"error": "无K线数据，无法计算技术指标"}
    
    # 8. 大盘指数
    print("  → 获取大盘指数 (腾讯财经)...")
    result["market_indices"] = fetch_market_indices()
    
    # 9. 个股所属板块
    print("  → 获取所属板块 (东方财富)...")
    result["stock_sectors"] = fetch_stock_sectors_eastmoney(stock_code)
    
    # 10. 今日热门概念板块TOP10
    print("  → 获取今日热门概念板块 (东方财富)...")
    result["hot_concept_sectors"] = fetch_hot_sectors_eastmoney("concept", 10)
    
    # 11. 板块联动分析 (取前3个最相关板块)
    sectors = result["stock_sectors"].get("sectors", [])
    if sectors:
        print(f"  → 分析板块联动 (发现{len(sectors)}个相关板块)...")
        sector_analysis = []
        for sector_info in sectors[:3]:
            sector_code = sector_info.get("code", "")
            sector_name = sector_info.get("name", "")
            if sector_code:
                print(f"    → 分析板块: {sector_name} ({sector_code})...")
                sector_stocks = fetch_sector_stocks_eastmoney(sector_code, 80)
                if not sector_stocks.get("error"):
                    position = analyze_sector_position(stock_code, sector_name, sector_stocks)
                    sector_analysis.append({
                        "sector_info": sector_info,
                        "position_analysis": position,
                    })
        result["sector_analysis"] = sector_analysis
    else:
        result["sector_analysis"] = []
        print("  ⚠️ 未获取到板块数据，建议通过WebSearch查询所属板块")
    
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
    parser.add_argument('--sectors', action='store_true', help='仅获取所属板块')
    parser.add_argument('--sector-stocks', type=str, help='获取板块成分股(传入板块代码如BK1050)')
    parser.add_argument('--hot-sectors', action='store_true', help='获取今日热门板块')
    parser.add_argument('--technical', action='store_true', help='获取技术指标(需要K线数据)')
    
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
            data = fetch_kline_eastmoney(stock_code, limit=70)
        elif args.sectors:
            data = fetch_stock_sectors_eastmoney(stock_code)
        elif args.sector_stocks:
            data = fetch_sector_stocks_eastmoney(args.sector_stocks)
        elif args.hot_sectors:
            data = {
                "concept": fetch_hot_sectors_eastmoney("concept", 10),
                "industry": fetch_hot_sectors_eastmoney("industry", 10),
            }
        elif args.technical:
            klines = fetch_kline_eastmoney(stock_code, limit=70)
            data = calculate_technical_indicators(klines)
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
