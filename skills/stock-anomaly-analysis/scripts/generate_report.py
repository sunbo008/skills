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
        "market_environment": {
            "overall_score": 75,
            "overall_status": "偏强",
            "indices": {
                "shanghai": {"name": "上证指数", "price": 3250.5, "change_pct": 1.2},
                "shenzhen": {"name": "深证成指", "price": 10580.3, "change_pct": 1.5},
                "chinext": {"name": "创业板指", "price": 2150.8, "change_pct": 2.1},
                "sz50": {"name": "上证50", "price": 2830.5, "change_pct": 0.8},
                "hs300": {"name": "沪深300", "price": 3920.1, "change_pct": 1.0},
                "csi500": {"name": "中证500", "price": 5680.2, "change_pct": 1.8},
                "csi1000": {"name": "中证1000", "price": 6250.3, "change_pct": 2.5}
            },
            "breadth": {
                "limit_up_count": 65,
                "limit_down_count": 8,
                "advance_count": 3800,
                "decline_count": 1200,
                "advance_decline_ratio": "3.2:1",
                "seal_rate": "72%",
                "total_volume": "1.35万亿"
            },
            "ladder": {
                "max_height": 5,
                "max_height_stock": "XX科技(AI概念)",
                "levels": {
                    "5板": 1, "4板": 2, "3板": 5,
                    "2板": 12, "首板": 45
                },
                "ladder_health": "完整",
                "target_stock_level": "3板(第3梯队, 同梯队5只)"
            },
            "sector": {
                "target_sector": "人形机器人",
                "sector_rank": "3/120",
                "sector_change_pct": 3.8,
                "sector_limit_up": 8,
                "related_sectors": ["AI", "智能驾驶", "传感器"],
                "sector_phase": "主升期"
            },
            "style": {
                "dominant": "小盘成长",
                "sz50_vs_csi1000": "中证1000(+2.5%) > 上证50(+0.8%), 小票活跃",
                "favorable_for_target": True
            },
            "impact_on_stock": "大盘偏强+板块领涨第3+梯队完整有空间+小盘风格有利，市场环境对该股异动形成正向支撑，短期上行阻力较小。"
        },
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
        "participants": {
            "hot_money": {
                "stance": "强烈看多",
                "summary": "[示例] 拉萨系游资大举介入，东方财富拉萨团结路净买入6200万，显示短线资金对连板预期强烈",
                "details": [
                    "东方财富拉萨团结路净买入6200万（知名游资席位）",
                    "买入手法为尾盘扫板，显示强烈接力意愿",
                    "该席位近1个月在机器人板块操作胜率超60%"
                ],
                "source_url": "#demo-需替换为真实链接",
                "verified": False
            },
            "main_force": {
                "stance": "看多",
                "summary": "[示例] 主力连续2日净流入，今日主力净流入2.3亿，超大单净买入1.8亿，量价配合良好",
                "details": [
                    "今日主力净流入2.3亿元，超大单净买入1.8亿",
                    "连续2日主力净流入，累计超4亿",
                    "换手率12.3%放量上涨，量价配合健康"
                ],
                "source_url": "https://data.eastmoney.com/zjlx/002195.html",
                "verified": True
            },
            "institution": {
                "stance": "看多",
                "summary": "[示例] 龙虎榜机构专用席位净买入8500万，近期有券商发布看好研报维持买入评级",
                "details": [
                    "机构专用席位买入8500万，为买方第一大席位",
                    "某券商近期发布研报，维持'买入'评级，目标价15元",
                    "北向资金今日净买入5200万"
                ],
                "source_url": "#demo-需替换为真实链接",
                "verified": False
            },
            "regulatory": {
                "stance": "利好",
                "summary": "[示例] 国家发改委发布人形机器人产业发展支持政策，行业迎来政策催化",
                "details": [
                    "发改委近日发布《人形机器人产业发展行动计划》",
                    "政策明确对核心零部件企业给予税收优惠和研发补贴",
                    "公司未收到任何监管问询函或关注函"
                ],
                "source_url": "#demo-需替换为真实链接",
                "verified": False
            },
            "retail": {
                "stance": "乐观",
                "summary": "[示例] 股吧讨论热度上升300%，看多情绪占主导，但未达到极度狂热阶段",
                "details": [
                    "东方财富股吧今日发帖量较昨日增长300%",
                    "看多帖子占比约70%，讨论焦点为机器人概念和连板预期",
                    "小单（散户）今日净卖出0.3亿，存在部分获利了结"
                ],
                "source_url": "#demo-需替换为真实链接",
                "verified": False
            },
            "battle_summary": {
                "pattern": "多方碾压",
                "bull_count": 4,
                "bear_count": 0,
                "neutral_count": 1,
                "conclusion": "游资+主力+机构+监管四维共振看多，散户情绪乐观但未过热。多方碾压格局下短期强势延续概率大，但需警惕散户情绪升温后的获利回吐。",
                "key_signal": "机构+游资共同买入是最强信号，长短线资金形成合力"
            }
        },
        "technical_pattern": {
            "identified_pattern": "老鸭头",
            "pattern_type": "看涨",
            "reliability": 5,
            "description": "5日线上穿10日线后股价小幅回落，但未跌破10日均线。5日线回踩后再次金叉，MACD在零轴上方金叉放量，符合经典老鸭头形态。主力洗盘完毕，即将展开主升浪。",
            "key_levels": {
                "support": 9.0,
                "resistance": 10.5,
                "stop_loss": 8.5,
                "target": 12.0
            },
            "volume_match": True,
            "trend_context": "上升趋势初期",
            "additional_patterns": ["红三兵", "多方炮"],
            "warning": "若跌破10日均线(约8.8元)则老鸭头形态失败，需及时止损"
        },
        "outlook": {
            "short_term": "短期维持强势。今日放量上涨，突破9.5元平台，上方压力位10.5-11元，下方支撑位9.0元。老鸭头形态确认后大概率展开主升浪。",
            "mid_term": "中期看好。订单持续落地，2026年进入收入确认期。宇树科技若成功IPO，公司作为核心供应商将获估值重估。目标价12-15元。",
            "core_logic": "本次异动核心驱动力是政策催化叠加机构游资共振，技术面老鸭头形态确认主升浪启动。",
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
    
    # 生成大盘环境HTML
    market_env_html = ""
    market_env = data.get("market_environment", {})
    if market_env:
        overall_score = market_env.get("overall_score", 50)
        overall_status = market_env.get("overall_status", "未知")
        
        # 状态颜色
        status_colors = {
            "强势": "#dc2626", "偏强": "#ef4444", "震荡": "#eab308",
            "偏弱": "#22c55e", "弱势": "#16a34a"
        }
        status_color = status_colors.get(overall_status, "#6b7280")
        
        # 指数表格
        indices = market_env.get("indices", {})
        index_names = {
            "shanghai": "上证指数", "shenzhen": "深证成指", "chinext": "创业板指",
            "sz50": "上证50", "hs300": "沪深300", "csi500": "中证500",
            "csi1000": "中证1000", "csi2000": "中证2000"
        }
        indices_html = ""
        for key, name in index_names.items():
            idx = indices.get(key, {})
            if not idx or not isinstance(idx, dict) or "change_pct" not in idx:
                continue
            pct = idx.get("change_pct", 0)
            color = "#ef4444" if pct >= 0 else "#22c55e"
            sign = "+" if pct >= 0 else ""
            price = idx.get("price", 0)
            indices_html += f'''
            <div class="idx-item">
                <div class="idx-name">{name}</div>
                <div class="idx-price">{price:.1f}</div>
                <div class="idx-pct" style="color: {color}">{sign}{pct:.2f}%</div>
            </div>'''
        
        # 市场广度
        breadth = market_env.get("breadth", {})
        breadth_html = ""
        if breadth:
            lu = breadth.get("limit_up_count", "--")
            ld = breadth.get("limit_down_count", "--")
            adv = breadth.get("advance_count", "--")
            dec = breadth.get("decline_count", "--")
            ratio = breadth.get("advance_decline_ratio", "--")
            vol = breadth.get("total_volume", "--")
            seal = breadth.get("seal_rate", "--")
            breadth_html = f'''
            <div class="breadth-grid">
                <div class="breadth-item up"><div class="breadth-label">涨停</div><div class="breadth-val" style="color:#ef4444">{lu}</div></div>
                <div class="breadth-item down"><div class="breadth-label">跌停</div><div class="breadth-val" style="color:#22c55e">{ld}</div></div>
                <div class="breadth-item"><div class="breadth-label">涨跌比</div><div class="breadth-val">{ratio}</div></div>
                <div class="breadth-item"><div class="breadth-label">封板率</div><div class="breadth-val">{seal}</div></div>
                <div class="breadth-item"><div class="breadth-label">上涨</div><div class="breadth-val" style="color:#ef4444">{adv}</div></div>
                <div class="breadth-item"><div class="breadth-label">下跌</div><div class="breadth-val" style="color:#22c55e">{dec}</div></div>
                <div class="breadth-item"><div class="breadth-label">两市成交</div><div class="breadth-val">{vol}</div></div>
            </div>'''
        
        # 连板梯队
        ladder = market_env.get("ladder", {})
        ladder_html = ""
        if ladder:
            max_h = ladder.get("max_height", 0)
            max_stock = ladder.get("max_height_stock", "")
            levels = ladder.get("levels", {})
            target_level = ladder.get("target_stock_level", "")
            health = ladder.get("ladder_health", "")
            
            levels_bars = ""
            for level_name, count in sorted(levels.items(), key=lambda x: x[0], reverse=True):
                bar_width = min(count * 8, 100)
                levels_bars += f'''
                <div class="ladder-row">
                    <span class="ladder-level">{level_name}</span>
                    <div class="ladder-bar-bg"><div class="ladder-bar-fill" style="width:{bar_width}%"></div></div>
                    <span class="ladder-count">{count}只</span>
                </div>'''
            
            ladder_html = f'''
            <div class="ladder-box">
                <div class="ladder-title">连板梯队 <span class="ladder-meta">最高板: {max_h}板 ({max_stock}) | 梯队: {health}</span></div>
                {levels_bars}
                {"<div class='ladder-target'>📍 该股位置: " + target_level + "</div>" if target_level else ""}
            </div>'''
        
        # 板块信息
        sector = market_env.get("sector", {})
        sector_html = ""
        if sector:
            s_name = sector.get("target_sector", "")
            s_rank = sector.get("sector_rank", "")
            s_pct = sector.get("sector_change_pct", 0)
            s_lu = sector.get("sector_limit_up", 0)
            s_phase = sector.get("sector_phase", "")
            related = sector.get("related_sectors", [])
            s_color = "#ef4444" if s_pct >= 0 else "#22c55e"
            
            related_tags = " ".join([f'<span class="related-tag">{r}</span>' for r in related]) if related else ""
            
            sector_html = f'''
            <div class="sector-box">
                <div class="sector-info">
                    <span class="sector-name">{s_name}</span>
                    <span class="sector-rank">排名 {s_rank}</span>
                    <span class="sector-pct" style="color:{s_color}">{"+" if s_pct>=0 else ""}{s_pct:.2f}%</span>
                    <span class="sector-lu">板块涨停 {s_lu}只</span>
                    {"<span class='sector-phase'>" + s_phase + "</span>" if s_phase else ""}
                </div>
                {"<div class='related-sectors'>关联板块: " + related_tags + "</div>" if related_tags else ""}
            </div>'''
        
        # 风格
        style_info = market_env.get("style", {})
        style_html = ""
        if style_info:
            dominant = style_info.get("dominant", "")
            detail = style_info.get("sz50_vs_csi1000", "")
            favorable = style_info.get("favorable_for_target", None)
            fav_text = "✓ 有利" if favorable else ("✗ 不利" if favorable is False else "")
            fav_color = "#4ade80" if favorable else "#ef4444"
            style_html = f'''
            <div class="style-box">
                <span>风格: <strong>{dominant}</strong></span>
                <span>{detail}</span>
                {"<span style='color:" + fav_color + "'>" + fav_text + "</span>" if fav_text else ""}
            </div>'''
        
        # 影响判断
        impact = market_env.get("impact_on_stock", "")
        impact_html = f'<div class="env-impact">💡 {impact}</div>' if impact else ""
        
        market_env_html = f'''
        <div class="env-header-row">
            <span class="env-score-badge" style="background:{status_color}">环境 {overall_score}分 · {overall_status}</span>
        </div>
        <div class="idx-grid">{indices_html}</div>
        {breadth_html}
        {ladder_html}
        {sector_html}
        {style_html}
        {impact_html}
        '''
    
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
    
    # 生成多方博弈分析HTML
    participants_html = ""
    participants = data.get("participants", {})
    if participants:
        # 参与者配置: key -> (名称, 图标, 描述)
        participant_config = {
            "hot_money": ("游资", "🔥", "短线热钱"),
            "main_force": ("主力", "🐋", "控盘大资金"),
            "institution": ("机构", "🏦", "基金/保险/QFII"),
            "regulatory": ("监管层", "🏛️", "政策/合规"),
            "retail": ("散户", "👥", "市场情绪"),
        }
        
        # 态度颜色映射
        stance_colors = {
            "强烈看多": "#dc2626", "看多": "#ef4444", "乐观": "#f97316",
            "强利好": "#dc2626", "利好": "#ef4444",
            "中性": "#6b7280", "分歧": "#eab308", "多空均衡": "#eab308",
            "看空": "#22c55e", "悲观": "#22c55e", "利空": "#22c55e",
            "强烈看空": "#16a34a", "极度恐慌": "#16a34a", "强利空": "#16a34a",
            "极度狂热": "#f97316", "未参与": "#4b5563",
        }
        
        # 态度方向映射 (用于博弈力量条)
        stance_direction = {
            "强烈看多": 2, "看多": 1, "乐观": 1,
            "强利好": 2, "利好": 1,
            "极度狂热": 1,
            "中性": 0, "分歧": 0, "未参与": 0,
            "看空": -1, "悲观": -1, "利空": -1,
            "强烈看空": -2, "极度恐慌": -1, "强利空": -2,
        }
        
        # 生成每个参与者的卡片
        cards_html = ""
        for key, (name, icon, desc) in participant_config.items():
            p = participants.get(key, {})
            if not p:
                continue
            stance = p.get("stance", "中性")
            summary = p.get("summary", "")
            details = p.get("details", [])
            color = stance_colors.get(stance, "#6b7280")
            
            details_html = ""
            for d in details:
                details_html += f'<li>{d}</li>'
            
            cards_html += f'''
            <div class="participant-card">
                <div class="participant-header">
                    <span class="participant-icon">{icon}</span>
                    <div class="participant-name-group">
                        <span class="participant-name">{name}</span>
                        <span class="participant-desc">{desc}</span>
                    </div>
                    <span class="participant-stance" style="background: {color}">{stance}</span>
                </div>
                <div class="participant-summary">{summary}</div>
                <ul class="participant-details">{details_html}</ul>
            </div>
            '''
        
        # 博弈格局总结
        battle = participants.get("battle_summary", {})
        battle_html = ""
        if battle:
            pattern = battle.get("pattern", "")
            bull = battle.get("bull_count", 0)
            bear = battle.get("bear_count", 0)
            neutral = battle.get("neutral_count", 0)
            conclusion = battle.get("conclusion", "")
            key_signal = battle.get("key_signal", "")
            
            # 格局颜色
            pattern_colors = {
                "多方碾压": "#dc2626", "多方占优": "#ef4444",
                "多空均衡": "#eab308",
                "空方占优": "#22c55e", "空方碾压": "#16a34a",
            }
            pattern_color = pattern_colors.get(pattern, "#6b7280")
            
            # 力量条: 总宽度5格
            total = bull + bear + neutral
            bull_pct = (bull / 5 * 100) if total > 0 else 0
            neutral_pct = (neutral / 5 * 100) if total > 0 else 0
            bear_pct = (bear / 5 * 100) if total > 0 else 0
            
            battle_html = f'''
            <div class="battle-summary">
                <div class="battle-header">
                    <span class="battle-icon">⚔️</span>
                    博弈格局
                    <span class="battle-pattern" style="background: {pattern_color}">{pattern}</span>
                </div>
                <div class="battle-bar-container">
                    <div class="battle-bar">
                        <div class="battle-bar-bull" style="width: {bull_pct}%">多 {bull}</div>
                        <div class="battle-bar-neutral" style="width: {neutral_pct}%">{neutral}</div>
                        <div class="battle-bar-bear" style="width: {bear_pct}%">空 {bear}</div>
                    </div>
                    <div class="battle-bar-labels">
                        <span style="color: #ef4444">多方</span>
                        <span style="color: #22c55e">空方</span>
                    </div>
                </div>
                <div class="battle-conclusion">{conclusion}</div>
                {"<div class='battle-signal'>💡 <strong>关键信号:</strong> " + key_signal + "</div>" if key_signal else ""}
            </div>
            '''
        
        participants_html = f'''
        <div class="participants-grid">
            {cards_html}
        </div>
        {battle_html}
        '''
    
    # 生成技术形态分析HTML
    pattern_html = ""
    tech_pattern = data.get("technical_pattern", {})
    if tech_pattern and tech_pattern.get("identified_pattern"):
        pattern_name = tech_pattern.get("identified_pattern", "")
        pattern_type = tech_pattern.get("pattern_type", "")
        reliability = tech_pattern.get("reliability", 0)
        description = tech_pattern.get("description", "")
        key_levels = tech_pattern.get("key_levels", {})
        volume_match = tech_pattern.get("volume_match", False)
        trend_context = tech_pattern.get("trend_context", "")
        additional = tech_pattern.get("additional_patterns", [])
        warning = tech_pattern.get("warning", "")
        
        # 形态类型颜色
        type_colors = {"看涨": "#ef4444", "看跌": "#22c55e", "中继": "#eab308", "整理": "#6b7280"}
        type_color = type_colors.get(pattern_type, "#6b7280")
        
        # 可靠度星星
        stars = "★" * reliability + "☆" * (5 - reliability)
        
        # 关键价位
        levels_html = ""
        if key_levels:
            level_items = []
            level_map = {
                "support": ("支撑位", "#22c55e"),
                "resistance": ("压力位", "#ef4444"),
                "stop_loss": ("止损位", "#f97316"),
                "target": ("目标位", "#8b5cf6"),
            }
            for key, (label, color) in level_map.items():
                val = key_levels.get(key)
                if val:
                    level_items.append(f'''
                    <div class="level-item">
                        <div class="level-label">{label}</div>
                        <div class="level-value" style="color: {color}">¥{val:.2f}</div>
                    </div>''')
            levels_html = f'<div class="levels-grid">{"".join(level_items)}</div>'
        
        # 附加形态
        additional_html = ""
        if additional:
            tags = " ".join([f'<span class="pattern-tag">{p}</span>' for p in additional])
            additional_html = f'<div class="additional-patterns">同时出现: {tags}</div>'
        
        # 警告
        warning_html = ""
        if warning:
            warning_html = f'<div class="pattern-warning">⚠️ {warning}</div>'
        
        pattern_html = f'''
        <div class="pattern-card">
            <div class="pattern-header">
                <span class="pattern-name">{pattern_name}</span>
                <span class="pattern-type" style="background: {type_color}">{pattern_type}</span>
                <span class="pattern-stars">{stars}</span>
            </div>
            <div class="pattern-desc">{description}</div>
            <div class="pattern-meta">
                <span>趋势背景: {trend_context}</span>
                <span>量价配合: {"✓ 是" if volume_match else "✗ 否"}</span>
            </div>
            {levels_html}
            {additional_html}
            {warning_html}
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
        
        /* 大盘环境样式 */
        .env-header-row {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }}
        
        .env-score-badge {{
            color: white;
            padding: 6px 18px;
            border-radius: 16px;
            font-size: 15px;
            font-weight: bold;
        }}
        
        .idx-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
            gap: 8px;
            margin-bottom: 16px;
        }}
        
        .idx-item {{
            background: #1e1e2e;
            border-radius: 8px;
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #3a3a5a;
        }}
        
        .idx-name {{ font-size: 11px; color: #888; margin-bottom: 4px; }}
        .idx-price {{ font-size: 14px; color: #ddd; font-weight: bold; }}
        .idx-pct {{ font-size: 13px; font-weight: bold; }}
        
        .breadth-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
            gap: 8px;
            margin-bottom: 16px;
        }}
        
        .breadth-item {{
            background: #1e1e2e;
            border-radius: 8px;
            padding: 8px;
            text-align: center;
            border: 1px solid #3a3a5a;
        }}
        
        .breadth-label {{ font-size: 11px; color: #888; margin-bottom: 2px; }}
        .breadth-val {{ font-size: 16px; font-weight: bold; color: #ddd; }}
        
        .ladder-box {{
            background: #1e1e2e;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 16px;
            border: 1px solid #3a3a5a;
        }}
        
        .ladder-title {{
            font-size: 14px;
            color: #fff;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        
        .ladder-meta {{ font-size: 12px; color: #888; font-weight: normal; margin-left: 8px; }}
        
        .ladder-row {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
        }}
        
        .ladder-level {{ font-size: 12px; color: #aaa; width: 40px; text-align: right; }}
        
        .ladder-bar-bg {{
            flex: 1;
            height: 14px;
            background: #2a2a40;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .ladder-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            border-radius: 4px;
        }}
        
        .ladder-count {{ font-size: 11px; color: #888; width: 36px; }}
        
        .ladder-target {{
            margin-top: 8px;
            font-size: 13px;
            color: #eab308;
            padding: 6px 10px;
            background: rgba(234, 179, 8, 0.1);
            border-radius: 6px;
        }}
        
        .sector-box {{
            background: #1e1e2e;
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 12px;
            border: 1px solid #3a3a5a;
        }}
        
        .sector-info {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        
        .sector-name {{ font-size: 15px; font-weight: bold; color: #fff; }}
        .sector-rank {{ font-size: 13px; color: #6366f1; background: rgba(99,102,241,0.15); padding: 2px 10px; border-radius: 10px; }}
        .sector-pct {{ font-size: 15px; font-weight: bold; }}
        .sector-lu {{ font-size: 12px; color: #888; }}
        .sector-phase {{ font-size: 12px; color: #fbbf24; background: rgba(251,191,36,0.15); padding: 2px 10px; border-radius: 10px; }}
        
        .related-sectors {{
            margin-top: 8px;
            font-size: 12px;
            color: #888;
        }}
        
        .related-tag {{
            background: #3a3a5a;
            color: #ccc;
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 11px;
            margin-left: 4px;
        }}
        
        .style-box {{
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 13px;
            color: #aaa;
            padding: 10px 14px;
            background: #1e1e2e;
            border-radius: 8px;
            margin-bottom: 12px;
            border: 1px solid #3a3a5a;
        }}
        
        .style-box strong {{ color: #fff; }}
        
        .env-impact {{
            font-size: 14px;
            color: #ddd;
            padding: 12px 14px;
            background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));
            border-radius: 8px;
            border-left: 3px solid #6366f1;
            line-height: 1.5;
        }}
        
        /* 多方博弈分析样式 */
        .participants-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}
        
        .participant-card {{
            background: #1e1e2e;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #3a3a5a;
            transition: transform 0.2s;
        }}
        
        .participant-card:hover {{
            transform: translateY(-2px);
        }}
        
        .participant-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}
        
        .participant-icon {{ font-size: 24px; }}
        
        .participant-name-group {{
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        
        .participant-name {{
            font-size: 15px;
            font-weight: bold;
            color: #fff;
        }}
        
        .participant-desc {{
            font-size: 11px;
            color: #666;
        }}
        
        .participant-stance {{
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            white-space: nowrap;
        }}
        
        .participant-summary {{
            font-size: 13px;
            color: #ccc;
            line-height: 1.5;
            margin-bottom: 10px;
            padding: 10px;
            background: #252540;
            border-radius: 8px;
        }}
        
        .participant-details {{
            list-style: none;
            padding: 0;
        }}
        
        .participant-details li {{
            font-size: 12px;
            color: #999;
            padding: 4px 0 4px 16px;
            position: relative;
            line-height: 1.5;
        }}
        
        .participant-details li::before {{
            content: "•";
            position: absolute;
            left: 4px;
            color: #6366f1;
        }}
        
        .battle-summary {{
            background: linear-gradient(135deg, #1a1a30 0%, #2a2040 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #4a3a6a;
        }}
        
        .battle-header {{
            font-size: 16px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .battle-icon {{ font-size: 20px; }}
        
        .battle-pattern {{
            color: white;
            padding: 4px 14px;
            border-radius: 14px;
            font-size: 13px;
            font-weight: bold;
        }}
        
        .battle-bar-container {{
            margin-bottom: 16px;
        }}
        
        .battle-bar {{
            display: flex;
            height: 32px;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 4px;
        }}
        
        .battle-bar-bull {{
            background: linear-gradient(90deg, #dc2626, #ef4444);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: bold;
            min-width: 40px;
        }}
        
        .battle-bar-neutral {{
            background: #6b7280;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            min-width: 20px;
        }}
        
        .battle-bar-bear {{
            background: linear-gradient(90deg, #22c55e, #16a34a);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            font-weight: bold;
            min-width: 40px;
        }}
        
        .battle-bar-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 11px;
        }}
        
        .battle-conclusion {{
            font-size: 14px;
            color: #ddd;
            line-height: 1.6;
            padding: 12px;
            background: #1e1e30;
            border-radius: 8px;
            margin-bottom: 10px;
        }}
        
        .battle-signal {{
            font-size: 13px;
            color: #eab308;
            padding: 10px 12px;
            background: rgba(234, 179, 8, 0.1);
            border-radius: 8px;
            border-left: 3px solid #eab308;
        }}
        
        .battle-signal strong {{ color: #fbbf24; }}
        
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
        
        /* 技术形态分析样式 */
        .pattern-card {{
            background: linear-gradient(135deg, #1a1a2e 0%, #1e2a3a 100%);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2a4a6a;
        }}
        
        .pattern-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
            flex-wrap: wrap;
        }}
        
        .pattern-name {{
            font-size: 20px;
            font-weight: bold;
            color: #fff;
        }}
        
        .pattern-type {{
            color: white;
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: bold;
        }}
        
        .pattern-stars {{
            font-size: 16px;
            color: #eab308;
            letter-spacing: 2px;
        }}
        
        .pattern-desc {{
            font-size: 14px;
            color: #ccc;
            line-height: 1.6;
            padding: 12px;
            background: #1e1e30;
            border-radius: 8px;
            margin-bottom: 14px;
        }}
        
        .pattern-meta {{
            display: flex;
            gap: 20px;
            font-size: 13px;
            color: #888;
            margin-bottom: 14px;
        }}
        
        .levels-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 12px;
            margin-bottom: 14px;
        }}
        
        .level-item {{
            text-align: center;
            background: #1e1e30;
            border-radius: 8px;
            padding: 10px 8px;
        }}
        
        .level-label {{
            font-size: 11px;
            color: #888;
            margin-bottom: 4px;
        }}
        
        .level-value {{
            font-size: 18px;
            font-weight: bold;
        }}
        
        .additional-patterns {{
            font-size: 13px;
            color: #aaa;
            margin-bottom: 10px;
        }}
        
        .pattern-tag {{
            background: #3a3a5a;
            color: #ccc;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 12px;
            margin-left: 4px;
        }}
        
        .pattern-warning {{
            font-size: 13px;
            color: #f97316;
            padding: 10px 12px;
            background: rgba(249, 115, 22, 0.1);
            border-radius: 8px;
            border-left: 3px solid #f97316;
        }}
        
        .core-logic-box {{
            font-size: 14px;
            color: #fbbf24;
            padding: 14px 16px;
            background: linear-gradient(135deg, rgba(234, 179, 8, 0.1), rgba(245, 158, 11, 0.05));
            border-radius: 10px;
            border-left: 4px solid #eab308;
            margin-bottom: 16px;
            line-height: 1.6;
        }}
        
        .core-logic-box strong {{ color: #fbbf24; }}
        
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
        
        {"<div class='section'><h2>🌍 大盘环境</h2>" + market_env_html + "</div>" if market_env_html else ""}
        
        <div class="section">
            <h2>🔥 近期触发因素</h2>
            {triggers_html if triggers_html else '<p style="color:#888">暂无近期触发因素数据</p>'}
        </div>
        
        {"<div class='section'><h2>⚔️ 多方博弈分析</h2>" + participants_html + "</div>" if participants_html else ""}
        
        {"<div class='section'><h2>📐 技术形态分析</h2>" + pattern_html + "</div>" if pattern_html else ""}
        
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
            {"<div class='core-logic-box'>💡 <strong>核心逻辑:</strong> " + outlook.get("core_logic", "") + "</div>" if outlook.get("core_logic") else ""}
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
