#!/usr/bin/env python3
"""
个股异动分析报告生成器
区分近期触发因素和历史背景信息
"""

import argparse
import json
import os
from datetime import datetime


def get_sample_data():
    """返回示例数据"""
    return {
        "stock": {
            "code": "002195",
            "name": "岩山科技",
            "sector": "AI+机器人+智能驾驶",
            "price": 9.93,
            "price_time": "2026-02-05 15:00",
            "change_pct": 5.67,
            "volume": "8.5亿",
            "turnover": "12.3%",
            "high": 10.15,
            "low": 9.20,
            "anomaly_type": "放量大涨"
        },
        "analysis_date": "2026-02-05",
        "triggers": [
            {
                "type": "消息面",
                "title": "[示例] 公司公告获得新能源车企智驾订单",
                "detail": "【此为演示数据】公司公告子公司纽劢科技与某头部新能源车企签订智能驾驶供货协议，预计2026年贡献收入1.2亿元。",
                "date": "2026-02-05",
                "source": "巨潮资讯",
                "url": "#demo-url-需替换为真实公告链接",
                "impact": "positive",
                "freshness": "today",
                "weight": 40
            },
            {
                "type": "板块联动",
                "title": "[示例] 人形机器人板块集体走强",
                "detail": "【此为演示数据】受海外机器人利好消息刺激，人形机器人板块今日大涨3.8%，多只个股涨停。",
                "date": "2026-02-05",
                "source": "东方财富",
                "url": "#demo-url-需替换为真实新闻链接",
                "impact": "positive",
                "freshness": "today",
                "weight": 35
            },
            {
                "type": "资金面",
                "title": "[示例] 主力资金大幅流入",
                "detail": "【此为演示数据】今日主力净流入2.3亿元，北向资金净买入5200万元，连续3日获主力加仓。",
                "date": "2026-02-05",
                "source": "同花顺",
                "url": "https://data.10jqka.com.cn/funds/ggzjl/board/002195/",
                "impact": "positive",
                "freshness": "today",
                "weight": 25
            }
        ],
        "background": [
            {
                "title": "宇树科技2亿元AI大脑订单",
                "detail": "2025年9月，子公司岩芯数智获得宇树科技2亿元订单，为人形机器人G1、R1提供Yan1.3多模态大模型。公司被列为宇树IPO核心供应商。",
                "date": "2025-09-01",
                "source": "东方财富",
                "url": "https://caifuhao.eastmoney.com/news/20250918123725099612100"
            },
            {
                "title": "国际汽配商3.39亿五年大单",
                "detail": "2025年10月，子公司纽劢科技与国际头部汽配商签署协议，2026-2030年预计收入3.39亿元，提供纯视觉L4级智驾方案。",
                "date": "2025-10-15",
                "source": "界面新闻",
                "url": "https://www.jiemian.com/article/13408972.html"
            },
            {
                "title": "AI业务首次规模变现",
                "detail": "2024年年报显示，AI板块收入7340万元，研发投入2.39亿元同比增168%。自研Yan大模型以3B参数达到Llama3 8B水平。",
                "date": "2025-04-22",
                "source": "中证网",
                "url": "https://www.cs.com.cn/ssgs/gsxw/202504/t20250422_6487135.html"
            }
        ],
        "fund_flow": {
            "main_net": "+2.3亿",
            "north_net": "+0.52亿",
            "big_order": "+1.8亿",
            "retail_net": "-0.3亿",
            "date": "2026-02-05"
        },
        "dragon_tiger": {
            "date": "2026-02-04",
            "reason": "涨幅偏离值达7%",
            "buy_seats": [
                {"name": "机构专用", "amount": "8500万"},
                {"name": "东方财富拉萨团结路", "amount": "6200万"},
                {"name": "华泰证券深圳益田路", "amount": "4100万"}
            ],
            "sell_seats": [
                {"name": "中信证券上海分公司", "amount": "5200万"},
                {"name": "机构专用", "amount": "3800万"}
            ]
        },
        "outlook": {
            "short_term": "短期维持强势。今日放量上涨，突破9.5元平台，上方压力位10.5-11元，下方支撑位9.0元。若明日能继续放量，有望挑战前高。",
            "mid_term": "中期看好。订单持续落地，2026年进入收入确认期。宇树科技若成功IPO，公司作为核心供应商将获估值重估。目标价12-15元。",
            "risks": [
                "AI/机器人概念退潮风险",
                "订单交付不及预期",
                "短期涨幅大，获利盘回吐",
                "大盘系统性回调"
            ]
        },
        "sources": [
            {"title": "[示例] 公司公告-智驾订单", "url": "#demo-需替换为真实链接", "date": "2026-02-05", "source": "巨潮资讯"},
            {"title": "今日资金流向", "url": "https://data.10jqka.com.cn/funds/ggzjl/board/002195/", "date": "2026-02-05", "source": "同花顺"},
            {"title": "宇树科技订单详情", "url": "https://caifuhao.eastmoney.com/news/20250918123725099612100", "date": "2025-09-18", "source": "东方财富"},
            {"title": "国际汽配商大单", "url": "https://www.jiemian.com/article/13408972.html", "date": "2025-10-15", "source": "界面新闻"}
        ]
    }


def validate_and_fix_urls(data):
    """校验并修复报告中的URL，确保都是用户可浏览的网页"""
    
    # API接口URL → 可浏览网页URL 的映射规则
    api_url_patterns = {
        "qt.gtimg.cn/q=": None,  # 腾讯财经API，需要根据股票代码替换
        "push2.eastmoney.com/api/": None,
        "push2his.eastmoney.com/api/": None,
        "datacenter-web.eastmoney.com/api/": None,
    }
    
    stock_code = data.get("stock", {}).get("code", "")
    warnings = []
    
    def fix_url(url, context=""):
        """修复单个URL"""
        if not url or url.startswith("#"):
            return url
        
        for pattern in api_url_patterns:
            if pattern in url:
                # 根据pattern类型替换为可浏览URL
                if "qt.gtimg.cn" in url:
                    new_url = f"https://stockpage.10jqka.com.cn/{stock_code}/"
                elif "push2.eastmoney.com" in url and "fflow" in url:
                    new_url = f"https://data.eastmoney.com/zjlx/{stock_code}.html"
                elif "push2his.eastmoney.com" in url:
                    new_url = f"https://quote.eastmoney.com/sz{stock_code}.html"
                elif "datacenter-web.eastmoney.com" in url:
                    new_url = f"https://data.eastmoney.com/stock/lhb/{stock_code}.html"
                else:
                    new_url = f"https://quote.eastmoney.com/sz{stock_code}.html"
                
                warnings.append(f"  ⚠️ [{context}] API接口URL已替换为可浏览网页:")
                warnings.append(f"     旧: {url}")
                warnings.append(f"     新: {new_url}")
                return new_url
        return url
    
    # 修复triggers中的URL
    for t in data.get("triggers", []):
        t["url"] = fix_url(t.get("url", ""), f"触发因素: {t.get('title', '')}")
    
    # 修复background中的URL
    for b in data.get("background", []):
        b["url"] = fix_url(b.get("url", ""), f"背景: {b.get('title', '')}")
    
    # 修复fund_flow中的URL
    fund_flow = data.get("fund_flow", {})
    if fund_flow.get("source_url"):
        fund_flow["source_url"] = fix_url(fund_flow["source_url"], "资金流向")
    
    # 修复dragon_tiger中的URL
    dragon_tiger = data.get("dragon_tiger", {})
    if dragon_tiger.get("source_url"):
        dragon_tiger["source_url"] = fix_url(dragon_tiger["source_url"], "龙虎榜")
    
    # 修复sources中的URL
    for s in data.get("sources", []):
        s["url"] = fix_url(s.get("url", ""), f"来源: {s.get('title', '')}")
    
    if warnings:
        print("\n🔗 URL校验结果:")
        for w in warnings:
            print(w)
        print()
    else:
        print("🔗 URL校验通过: 所有URL均为可浏览网页\n")
    
    return data


def generate_html(data):
    """生成HTML报告"""
    
    # 先校验并修复URL
    data = validate_and_fix_urls(data)
    
    stock = data["stock"]
    triggers = sorted(data.get("triggers", []), key=lambda x: x.get("weight", 0), reverse=True)
    background = data.get("background", [])
    fund_flow = data.get("fund_flow", {})
    dragon_tiger = data.get("dragon_tiger", {})
    outlook = data.get("outlook", {})
    sources = data.get("sources", [])
    analysis_date = data.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))
    
    # 涨跌颜色
    change_color = "#ef4444" if stock["change_pct"] >= 0 else "#22c55e"
    change_sign = "+" if stock["change_pct"] >= 0 else ""
    
    # 异动类型样式
    anomaly_colors = {
        "涨停": "#dc2626", "大涨": "#ef4444", "放量大涨": "#f97316",
        "持续走强": "#f97316", "跌停": "#16a34a", "大跌": "#22c55e",
        "放量下跌": "#15803d", "异常波动": "#eab308", "概念热炒": "#8b5cf6"
    }
    anomaly_color = anomaly_colors.get(stock.get("anomaly_type", "异常波动"), "#6b7280")
    
    # 行情数据
    price_time = stock.get("price_time", analysis_date)
    volume = stock.get("volume", "")
    turnover = stock.get("turnover", "")
    high = stock.get("high", 0)
    low = stock.get("low", 0)
    
    market_data_html = ""
    if volume or turnover or high:
        parts = []
        if volume:
            parts.append(f"成交额: {volume}")
        if turnover:
            parts.append(f"换手率: {turnover}")
        if high and low:
            parts.append(f"振幅: {high:.2f}-{low:.2f}")
        market_data_html = f'<div class="market-data">{" | ".join(parts)}</div>'
    
    # 生成触发因素HTML
    triggers_html = ""
    for t in triggers:
        impact_color = "#22c55e" if t["impact"] == "positive" else "#ef4444"
        impact_text = "利好" if t["impact"] == "positive" else "利空"
        freshness = t.get("freshness", "")
        
        # 时效性标签
        freshness_html = ""
        if freshness == "today":
            freshness_html = '<span class="freshness-badge today">今日</span>'
        elif freshness == "recent":
            freshness_html = '<span class="freshness-badge recent">近3日</span>'
        elif freshness == "week":
            freshness_html = '<span class="freshness-badge week">本周</span>'
        
        source_html = ""
        if t.get("date") or t.get("source"):
            parts = []
            if t.get("date"):
                parts.append(f'<span class="info-date">📅 {t["date"]}</span>')
            if t.get("source") and t.get("url"):
                parts.append(f'<a href="{t["url"]}" target="_blank" class="info-source">🔗 {t["source"]}</a>')
            source_html = f'<div class="trigger-source">{" ".join(parts)}</div>'
        
        triggers_html += f'''
        <div class="trigger-card">
            <div class="trigger-header">
                <span class="trigger-type">{t["type"]}</span>
                {freshness_html}
                <span class="trigger-impact" style="background: {impact_color}">{impact_text}</span>
                <span class="trigger-weight">权重 {t.get("weight", 0)}%</span>
            </div>
            <h4 class="trigger-title">{t["title"]}</h4>
            <p class="trigger-detail">{t["detail"]}</p>
            {source_html}
        </div>
        '''
    
    # 生成资金流向HTML
    fund_html = ""
    if fund_flow:
        fund_date = fund_flow.get("date", "")
        main_net = fund_flow.get("main_net", "")
        super_big_net = fund_flow.get("super_big_net", "")
        big_net = fund_flow.get("big_net", "")
        mid_net = fund_flow.get("mid_net", "")
        small_net = fund_flow.get("small_net", "")
        north_net = fund_flow.get("north_net", "")
        
        def get_color(val):
            if not val:
                return "#888"
            val_str = str(val)
            return "#ef4444" if val_str.startswith("+") else "#22c55e" if val_str.startswith("-") else "#888"
        
        # 如果有详细资金流向数据
        if super_big_net or small_net:
            fund_html = f'''
            <div class="fund-flow">
                <div class="fund-header">今日资金流向 <span class="fund-date">📅 {fund_date}</span></div>
                <div class="fund-grid" style="grid-template-columns: repeat(5, 1fr);">
                    <div class="fund-item">
                        <div class="fund-label">主力净额</div>
                        <div class="fund-value" style="color: {get_color(main_net)}">{main_net or "--"}</div>
                    </div>
                    <div class="fund-item">
                        <div class="fund-label">超大单</div>
                        <div class="fund-value" style="color: {get_color(super_big_net)}">{super_big_net or "--"}</div>
                    </div>
                    <div class="fund-item">
                        <div class="fund-label">大单</div>
                        <div class="fund-value" style="color: {get_color(big_net)}">{big_net or "--"}</div>
                    </div>
                    <div class="fund-item">
                        <div class="fund-label">中单</div>
                        <div class="fund-value" style="color: {get_color(mid_net)}">{mid_net or "--"}</div>
                    </div>
                    <div class="fund-item">
                        <div class="fund-label">小单(散户)</div>
                        <div class="fund-value" style="color: {get_color(small_net)}">{small_net or "--"}</div>
                    </div>
                </div>
            </div>
            '''
        else:
            big_order = fund_flow.get("big_order", "")
            fund_html = f'''
            <div class="fund-flow">
                <div class="fund-header">今日资金流向 <span class="fund-date">📅 {fund_date}</span></div>
                <div class="fund-grid">
                    <div class="fund-item">
                        <div class="fund-label">主力净流入</div>
                        <div class="fund-value" style="color: {get_color(main_net)}">{main_net or "--"}</div>
                    </div>
                    <div class="fund-item">
                        <div class="fund-label">北向资金</div>
                        <div class="fund-value" style="color: {get_color(north_net)}">{north_net or "--"}</div>
                    </div>
                    <div class="fund-item">
                        <div class="fund-label">大单净额</div>
                        <div class="fund-value" style="color: {get_color(big_order)}">{big_order or "--"}</div>
                    </div>
                </div>
            </div>
            '''
    
    # 生成主力吸筹分析HTML
    chip_html = ""
    chip_analysis = data.get("chip_analysis", {})
    if chip_analysis:
        conclusion = chip_analysis.get("conclusion", "")
        features = chip_analysis.get("features", [])
        pattern = chip_analysis.get("recent_pattern", "")
        
        features_html = ""
        for f in features:
            features_html += f'<li>{f}</li>'
        
        chip_html = f'''
        <div class="chip-analysis">
            <div class="chip-header">
                <span class="chip-icon">🔍</span>
                主力吸筹分析
            </div>
            <div class="chip-conclusion">结论: <strong>{conclusion}</strong></div>
            <div class="chip-features">
                <div class="chip-subtitle">吸筹特征:</div>
                <ul>{features_html}</ul>
            </div>
            <div class="chip-pattern">
                <div class="chip-subtitle">近期走势形态:</div>
                <p>{pattern}</p>
            </div>
        </div>
        '''
    
    # 生成龙虎榜HTML
    dragon_html = ""
    if dragon_tiger and dragon_tiger.get("date"):
        buy_html = ""
        for seat in dragon_tiger.get("buy_seats", []):
            if isinstance(seat, dict):
                buy_html += f'<div class="seat-item buy"><span class="seat-name">{seat["name"]}</span><span class="seat-amount">{seat["amount"]}</span></div>'
            else:
                buy_html += f'<div class="seat-item buy"><span class="seat-name">{seat}</span></div>'
        
        sell_html = ""
        for seat in dragon_tiger.get("sell_seats", []):
            if isinstance(seat, dict):
                sell_html += f'<div class="seat-item sell"><span class="seat-name">{seat["name"]}</span><span class="seat-amount">{seat["amount"]}</span></div>'
            else:
                sell_html += f'<div class="seat-item sell"><span class="seat-name">{seat}</span></div>'
        
        dragon_html = f'''
        <div class="dragon-tiger">
            <div class="dragon-header">
                龙虎榜 <span class="dragon-date">📅 {dragon_tiger["date"]}</span>
                <span class="dragon-reason">{dragon_tiger.get("reason", "")}</span>
            </div>
            <div class="dragon-grid">
                <div class="dragon-col">
                    <div class="dragon-title buy">买入前三</div>
                    {buy_html}
                </div>
                <div class="dragon-col">
                    <div class="dragon-title sell">卖出前三</div>
                    {sell_html}
                </div>
            </div>
        </div>
        '''
    
    # 生成背景信息HTML
    background_html = ""
    for b in background:
        background_html += f'''
        <div class="bg-item">
            <div class="bg-date">{b.get("date", "")}</div>
            <div class="bg-content">
                <div class="bg-title">{b["title"]}</div>
                <div class="bg-detail">{b["detail"]}</div>
                <a href="{b.get("url", "#")}" target="_blank" class="bg-source">🔗 {b.get("source", "来源")}</a>
            </div>
        </div>
        '''
    
    # 生成风险HTML
    risks_html = ""
    for risk in outlook.get("risks", []):
        risks_html += f'<li>{risk}</li>'
    
    # 生成来源HTML
    sources_html = ""
    for s in sources:
        date_str = f'[{s.get("date", "")}]' if s.get("date") else ""
        source_str = f'- {s.get("source", "")}' if s.get("source") else ""
        sources_html += f'''
        <li>
            <a href="{s["url"]}" target="_blank">{s["title"]}</a>
            <span class="source-meta">{date_str} {source_str}</span>
        </li>
        '''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{stock["name"]}({stock["code"]}) 异动分析报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            min-height: 100vh;
            color: #e0e0e0;
            padding: 20px;
        }}
        
        .container {{ max-width: 1000px; margin: 0 auto; }}
        
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ font-size: 28px; color: #fff; margin-bottom: 10px; }}
        .header .date {{ color: #888; font-size: 14px; }}
        
        .stock-card {{
            background: linear-gradient(135deg, #2a2a40 0%, #1a1a2e 100%);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #3a3a5a;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}
        
        .stock-info {{ display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
        .stock-name {{ font-size: 24px; font-weight: bold; color: #fff; }}
        .stock-code {{ font-size: 14px; color: #888; background: #3a3a5a; padding: 4px 12px; border-radius: 20px; }}
        .stock-sector {{ font-size: 14px; color: #888; }}
        
        .stock-price-container {{ text-align: right; }}
        .stock-price {{ font-size: 32px; font-weight: bold; color: {change_color}; }}
        .stock-change {{ font-size: 18px; color: {change_color}; }}
        .price-time {{ font-size: 12px; color: #666; margin-top: 4px; }}
        .market-data {{ font-size: 12px; color: #888; margin-top: 4px; }}
        
        .anomaly-badge {{
            background: {anomaly_color};
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}
        
        .section {{
            background: #2a2a40;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #3a3a5a;
        }}
        
        .section h2 {{
            font-size: 18px;
            color: #fff;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #4a4a6a;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .section h2::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 20px;
            background: linear-gradient(to bottom, #6366f1, #8b5cf6);
            border-radius: 2px;
        }}
        
        /* 触发因素样式 */
        .trigger-card {{
            background: #1e1e2e;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            border: 1px solid #3a3a5a;
        }}
        
        .trigger-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .trigger-type {{
            background: #4a4a6a;
            color: #fff;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
        }}
        
        .freshness-badge {{
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }}
        
        .freshness-badge.today {{
            background: linear-gradient(135deg, #f97316, #ea580c);
            color: white;
            animation: pulse 2s infinite;
        }}
        
        .freshness-badge.recent {{
            background: #6366f1;
            color: white;
        }}
        
        .freshness-badge.week {{
            background: #4a4a6a;
            color: #ccc;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .trigger-impact {{
            color: #fff;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
        }}
        
        .trigger-weight {{
            color: #888;
            font-size: 12px;
            margin-left: auto;
        }}
        
        .trigger-title {{ font-size: 16px; color: #fff; margin-bottom: 8px; }}
        .trigger-detail {{ font-size: 14px; color: #aaa; line-height: 1.6; }}
        
        .trigger-source {{
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px dashed #3a3a5a;
            font-size: 12px;
            display: flex;
            gap: 16px;
        }}
        
        .info-date {{ color: #888; }}
        .info-source {{ color: #6366f1; text-decoration: none; }}
        .info-source:hover {{ text-decoration: underline; }}
        
        /* 资金流向样式 */
        .fund-flow {{
            background: #1e1e2e;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid #3a3a5a;
        }}
        
        .fund-header {{
            font-size: 14px;
            color: #fff;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .fund-date {{ font-size: 12px; color: #888; }}
        
        .fund-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}
        
        .fund-item {{ text-align: center; }}
        .fund-label {{ font-size: 12px; color: #888; margin-bottom: 4px; }}
        .fund-value {{ font-size: 18px; font-weight: bold; }}
        
        /* 主力吸筹分析样式 */
        .chip-analysis {{
            background: linear-gradient(135deg, #1a2a1a 0%, #1e2e1e 100%);
            border-radius: 12px;
            padding: 16px;
            margin-top: 16px;
            border: 1px solid #2a4a2a;
        }}
        
        .chip-header {{
            font-size: 16px;
            font-weight: bold;
            color: #4ade80;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .chip-icon {{ font-size: 20px; }}
        
        .chip-conclusion {{
            background: #2a3a2a;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 12px;
            color: #fff;
        }}
        
        .chip-conclusion strong {{
            color: #4ade80;
        }}
        
        .chip-features {{
            margin-bottom: 12px;
        }}
        
        .chip-subtitle {{
            font-size: 13px;
            color: #888;
            margin-bottom: 8px;
        }}
        
        .chip-features ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .chip-features li {{
            padding: 6px 0;
            padding-left: 20px;
            position: relative;
            font-size: 13px;
            color: #d0d0d0;
        }}
        
        .chip-features li::before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #4ade80;
        }}
        
        .chip-pattern {{
            background: #1e2e1e;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 13px;
        }}
        
        .chip-pattern p {{
            color: #a0a0a0;
            line-height: 1.6;
        }}
        
        /* 龙虎榜样式 */
        .dragon-tiger {{
            background: #1e1e2e;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #3a3a5a;
        }}
        
        .dragon-header {{
            font-size: 14px;
            color: #fff;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .dragon-date {{ font-size: 12px; color: #888; }}
        .dragon-reason {{ font-size: 12px; color: #666; }}
        
        .dragon-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }}
        
        .dragon-title {{
            font-size: 13px;
            padding: 6px;
            border-radius: 6px;
            text-align: center;
            margin-bottom: 8px;
        }}
        
        .dragon-title.buy {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; }}
        .dragon-title.sell {{ background: rgba(34, 197, 94, 0.2); color: #22c55e; }}
        
        .seat-item {{
            display: flex;
            justify-content: space-between;
            padding: 6px 8px;
            border-radius: 6px;
            margin-bottom: 4px;
            font-size: 12px;
        }}
        
        .seat-item.buy {{ background: rgba(239, 68, 68, 0.1); }}
        .seat-item.sell {{ background: rgba(34, 197, 94, 0.1); }}
        .seat-name {{ color: #ccc; }}
        .seat-amount {{ color: #888; }}
        
        /* 背景信息样式 */
        .bg-timeline {{
            position: relative;
            padding-left: 20px;
        }}
        
        .bg-timeline::before {{
            content: "";
            position: absolute;
            left: 6px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #3a3a5a;
        }}
        
        .bg-item {{
            position: relative;
            padding: 12px 0 12px 20px;
            border-bottom: 1px dashed #3a3a5a;
        }}
        
        .bg-item:last-child {{ border-bottom: none; }}
        
        .bg-item::before {{
            content: "";
            position: absolute;
            left: -17px;
            top: 18px;
            width: 10px;
            height: 10px;
            background: #6366f1;
            border-radius: 50%;
        }}
        
        .bg-date {{
            font-size: 12px;
            color: #888;
            margin-bottom: 4px;
        }}
        
        .bg-title {{
            font-size: 14px;
            color: #fff;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        
        .bg-detail {{
            font-size: 13px;
            color: #aaa;
            line-height: 1.5;
            margin-bottom: 6px;
        }}
        
        .bg-source {{
            font-size: 12px;
            color: #6366f1;
            text-decoration: none;
        }}
        
        /* 展望样式 */
        .outlook-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }}
        
        .outlook-card {{
            background: #1e1e2e;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #3a3a5a;
        }}
        
        .outlook-card h3 {{
            font-size: 14px;
            color: #6366f1;
            margin-bottom: 10px;
        }}
        
        .outlook-card p {{
            font-size: 14px;
            color: #ccc;
            line-height: 1.6;
        }}
        
        .risks-card {{
            background: linear-gradient(135deg, #2a1a1a 0%, #1e1e2e 100%);
            border: 1px solid #5a3a3a;
        }}
        
        .risks-card h3 {{ color: #ef4444; }}
        .risks-card ul {{ list-style: none; }}
        .risks-card li {{
            font-size: 14px;
            color: #ccc;
            padding: 6px 0 6px 20px;
            position: relative;
        }}
        .risks-card li::before {{
            content: "⚠️";
            position: absolute;
            left: 0;
            font-size: 12px;
        }}
        
        /* 来源样式 */
        .sources {{
            margin-top: 20px;
            background: #1e1e2e;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #3a3a5a;
        }}
        
        .sources h3 {{
            font-size: 14px;
            color: #fff;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid #3a3a5a;
        }}
        
        .sources ul {{ list-style: none; }}
        .sources li {{
            padding: 8px 0;
            border-bottom: 1px dashed #2a2a40;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .sources li:last-child {{ border-bottom: none; }}
        .sources a {{ color: #6366f1; text-decoration: none; font-size: 14px; }}
        .sources a:hover {{ text-decoration: underline; }}
        .source-meta {{ font-size: 12px; color: #666; }}
        
        .disclaimer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
            padding: 20px;
            border-top: 1px solid #3a3a5a;
        }}
        
        @media (max-width: 600px) {{
            .stock-card {{ flex-direction: column; text-align: center; }}
            .stock-price-container {{ text-align: center; }}
            .fund-grid {{ grid-template-columns: 1fr; }}
            .dragon-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 个股异动分析报告</h1>
            <div class="date">分析日期: {analysis_date}</div>
        </div>
        
        <div class="stock-card">
            <div class="stock-info">
                <span class="stock-name">{stock["name"]}</span>
                <span class="stock-code">{stock["code"]}</span>
                <span class="stock-sector">{stock["sector"]}</span>
            </div>
            <div class="stock-price-container">
                <div class="stock-price">¥{stock["price"]:.2f}</div>
                <div class="stock-change">{change_sign}{stock["change_pct"]:.2f}%</div>
                <div class="price-time">📅 {price_time}</div>
                {market_data_html}
            </div>
            <span class="anomaly-badge">{stock.get("anomaly_type", "异常波动")}</span>
        </div>
        
        <div class="section">
            <h2>🔥 近期触发因素</h2>
            {triggers_html if triggers_html else '<p style="color:#888">暂无近期触发因素数据</p>'}
        </div>
        
        <div class="section">
            <h2>💰 资金动向</h2>
            {fund_html if fund_html else ''}
            {chip_html if chip_html else ''}
            {dragon_html if dragon_html else ''}
            {'' if fund_html or dragon_html or chip_html else '<p style="color:#888">暂无资金数据</p>'}
        </div>
        
        <div class="section">
            <h2>📜 历史背景</h2>
            <div class="bg-timeline">
                {background_html if background_html else '<p style="color:#888">暂无背景信息</p>'}
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 走势预判</h2>
            <div class="outlook-grid">
                <div class="outlook-card">
                    <h3>📈 短期展望</h3>
                    <p>{outlook.get("short_term", "暂无")}</p>
                </div>
                <div class="outlook-card">
                    <h3>📊 中期展望</h3>
                    <p>{outlook.get("mid_term", "暂无")}</p>
                </div>
                <div class="outlook-card risks-card">
                    <h3>风险提示</h3>
                    <ul>{risks_html}</ul>
                </div>
            </div>
        </div>
        
        <div class="sources">
            <h3>📚 信息来源</h3>
            <ul>{sources_html}</ul>
        </div>
        
        <div class="disclaimer">
            ⚠️ 免责声明：本报告仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。<br>
            数据来源于公开信息，请以官方公告为准。
        </div>
    </div>
</body>
</html>'''
    
    return html


def main():
    parser = argparse.ArgumentParser(description="生成个股异动分析报告")
    parser.add_argument("--data", type=str, help="JSON数据文件路径 (必须是真实数据)")
    parser.add_argument("--output", type=str, default="stock_analysis_report.html", help="输出HTML文件路径")
    parser.add_argument("--sample", action="store_true", help="显示JSON格式说明 (不生成报告)")
    parser.add_argument("--format", action="store_true", help="显示JSON格式说明")
    
    args = parser.parse_args()
    
    if args.sample or args.format:
        print("=" * 60)
        print("📋 JSON数据格式说明 (仅供参考格式，禁止直接使用)")
        print("=" * 60)
        print("""
⚠️  警告: 以下为格式示例，所有数据必须从WebSearch获取真实值!

{
  "stock": {
    "code": "股票代码",
    "name": "股票名称", 
    "price": 从搜索获取的真实价格,
    "price_time": "价格获取时间",
    "change_pct": 真实涨跌幅,
    ...
  },
  "triggers": [
    {
      "title": "从搜索结果复制的真实标题",
      "detail": "从搜索结果复制的真实内容",
      "date": "搜索结果中的真实日期",
      "url": "WebSearch返回的真实URL (禁止编造!)",
      ...
    }
  ],
  ...
}

使用方法:
1. 先用 WebSearch 搜索股票相关信息
2. 从搜索结果中提取真实数据和URL
3. 创建 JSON 文件
4. 运行: python generate_report.py --data 你的数据.json --output 报告.html
""")
        return 0
    
    if not args.data:
        print("❌ 错误: 请提供 --data 参数指定真实数据文件")
        print("   用法: python generate_report.py --data analysis.json --output 报告.html")
        print("   查看格式: python generate_report.py --format")
        return 1
    
    if not os.path.exists(args.data):
        print(f"❌ 错误: 找不到数据文件 {args.data}")
        return 1
    
    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 验证数据真实性
    warnings = []
    for trigger in data.get("triggers", []):
        url = trigger.get("url", "")
        if not url or url.startswith("#") or "demo" in url.lower() or "示例" in url or "需替换" in url:
            warnings.append(f"  - '{trigger.get('title', '未知')}' 的URL无效: {url}")
    
    if warnings:
        print("⚠️  警告: 检测到可能的无效URL:")
        for w in warnings:
            print(w)
        print("   请确保所有URL都是从WebSearch获取的真实链接!")
        print()
    
    print(f"📊 从 {args.data} 加载数据...")
    
    html = generate_html(data)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {os.path.abspath(args.output)}")
    return 0


if __name__ == "__main__":
    exit(main())
