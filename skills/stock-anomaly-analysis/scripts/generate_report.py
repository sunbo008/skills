#!/usr/bin/env python3
"""
个股异动分析报告生成器
区分近期触发因素和历史背景信息
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import json
import os
from datetime import datetime


def _get_trading_day(offset=0):
    """获取最近的交易日 (跳过周末)，offset=0为今天/最近交易日，offset=-1为上一个交易日"""
    from datetime import timedelta
    dt = datetime.now()
    # 先找到今天或最近的交易日
    while dt.weekday() >= 5:  # 5=Sat, 6=Sun
        dt -= timedelta(days=1)
    # 再往前偏移offset个交易日
    for _ in range(abs(offset)):
        dt -= timedelta(days=1)
        while dt.weekday() >= 5:
            dt -= timedelta(days=1)
    return dt


def _get_trading_days_before(anchor_dt, count):
    """从anchor_dt往前获取count个交易日列表 (不含anchor_dt本身)"""
    from datetime import timedelta
    days = []
    dt = anchor_dt
    for _ in range(count):
        dt -= timedelta(days=1)
        while dt.weekday() >= 5:
            dt -= timedelta(days=1)
        days.append(dt)
    return list(reversed(days))  # 从早到晚


def get_sample_data():
    """返回示例数据 (日期动态生成，始终基于最近交易日)"""
    today = _get_trading_day(0)       # 今天/最近交易日
    yesterday = _get_trading_day(-1)  # 上一个交易日
    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    
    # 生成温度历史: 最近15个交易日 + 今天
    temp_history_days = _get_trading_days_before(today, 15)
    temp_values = [30, 28, 25, 22, 18, 20, 23, 26, 28, 25, 27, 30, 33, 35, 32]
    temp_labels = ["缩量调整", "", "放量下跌", "", "缩量新低", "", "止跌企稳", "", "", "回踩确认", "", "温和放量", "", "突破平台", ""]
    temp_history = []
    for i, d in enumerate(temp_history_days):
        temp_history.append({"date": d.strftime("%m-%d"), "value": temp_values[i], "label": temp_labels[i]})
    temp_history.append({"date": today.strftime("%m-%d"), "value": 42, "label": "放量大涨"})
    
    # 威科夫事件: Spring在前2个交易日，SOS在今天
    spring_day = _get_trading_day(-2)
    spring_str = spring_day.strftime("%Y-%m-%d")
    
    return {
        "stock": {
            "code": "002195",
            "name": "岩山科技",
            "sector": "AI+机器人+智能驾驶",
            "price": 9.93,
            "price_time": f"{today_str} 15:00",
            "change_pct": 5.67,
            "volume": "8.5亿",
            "turnover": "12.3%",
            "high": 10.15,
            "low": 9.20,
            "anomaly_type": "放量大涨"
        },
        "analysis_date": today_str,
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
                "date": today_str,
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
                "date": today_str,
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
                "date": today_str,
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
            "date": today_str
        },
        "dragon_tiger": {
            "date": yesterday_str,
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
        "market_temperature": {
            "temperature_value": 42,
            "phase": "升温期",
            "phase_code": 3,
            "trend": "持续升温",
            "trend_arrow": "↑",
            "yesterday_temperature": 35,
            "temperature_change": "+7",
            "history_source": "基于东方财富K线数据(个股+上证指数)加权计算: 涨跌幅30%+换手率20%+大盘联动20%+3日动量15%+波幅方向15%",
            "history": temp_history,
            "dimensions": {
                "profit_effect": {"score": 55, "weight": 0.25, "detail": "涨停45家，跌停12家"},
                "board_height": {"score": 50, "weight": 0.20, "detail": "最高板4板，梯队较完整"},
                "market_breadth": {"score": 48, "weight": 0.15, "detail": "涨跌比1.8:1，封板率55%"},
                "volume_level": {"score": 40, "weight": 0.10, "detail": "成交额1.1万亿，较昨日微增"},
                "sentiment_extreme": {"score": 35, "weight": 0.10, "detail": "股吧情绪偏中性，多空分歧"},
                "leader_status": {"score": 45, "weight": 0.10, "detail": "龙头封板但有分歧"},
                "fund_trend": {"score": 30, "weight": 0.10, "detail": "北向小幅流入，融资持平"}
            },
            "entry_suggestion": {
                "market_level": "★★★ 精选介入",
                "combined_assessment": "市场处于升温期(42°)，赚钱效应开始扩散但尚未过热，配合个股自身强势表现，可以积极精选介入",
                "position_advice": "建议5-7成仓位",
                "key_warning": "关注温度是否继续升温确认趋势，若连续2日降温需减仓"
            },
            "cycle_position": {
                "description": "当前处于情绪周期的升温阶段，赚钱效应正在从少数龙头向更多个股扩散",
                "distance_from_peak": "距离高潮期约13-33°空间",
                "distance_from_bottom": "距离冰点约27-42°",
                "phase_duration_days": 3,
                "estimated_phase_progress": "40%"
            }
        },
        "supply_demand": {
            "wyckoff_phase": "吸筹末期→上涨初期",
            "wyckoff_phase_code": 1,
            "phase_evidence": [
                "股价在8.5-10.5区间横盘整理超过15个交易日",
                "下跌时成交量萎缩(平均换手率2.1%)，反弹时放量(平均换手率4.8%)",
                "出现Spring信号: 2月3日假跌破8.5支撑后迅速收回至9.0以上"
            ],
            "supply_demand_score": 65,
            "supply_demand_balance": "需求占优",
            "volume_price_analysis": {
                "pattern": "放量上涨",
                "up_day_avg_volume": "6.8亿",
                "down_day_avg_volume": "3.2亿",
                "volume_ratio": 2.13,
                "interpretation": "上涨日平均成交量是下跌日的2.13倍，需求力量明显强于供应，买方积极抢筹"
            },
            "divergence": {
                "type": "无背离",
                "detail": "近期量价配合良好，未出现明显背离信号"
            },
            "wyckoff_events": [
                {"event": "Spring(弹簧)", "date": spring_str, "detail": "股价假跌破8.5元支撑位后迅速反弹至9.0以上，典型的最后一次供应测试", "significance": "高"},
                {"event": "SOS(强势信号)", "date": today_str, "detail": "放量突破9.5元阻力位，成交量较前5日均值放大180%，需求正式超过供应", "significance": "高"}
            ],
            "supply_zones": [10.5, 11.0],
            "demand_zones": [9.0, 8.5],
            "supply_exhaustion_signs": [
                "连续3日下跌时成交量递减，卖盘逐步枯竭",
                "最近一次回调幅度仅3.2%，远小于前次回调7.8%"
            ],
            "demand_strength_signs": [
                "今日主力净流入2.3亿，大额需求持续进入",
                "涨停时封单量大于成交量的30%，买方积极"
            ],
            "conclusion": "当前处于威科夫吸筹末期→上涨初期过渡阶段。Spring已确认底部供应被充分吸收，SOS信号确认需求正式占优。供需格局明确有利于多方，上方10.5元为首个供应密集区。",
            "supply_demand_forecast": {
                "short_term": "需求持续占优，短期上方10.5元附近可能遇到供应释放",
                "mid_term": "若能放量突破10.5供应区，则进入上涨期(Markup)，下一供应区在12-13元",
                "key_observation": "关注9.5元是否能从阻力转为支撑(供需转换确认)"
            }
        },
        "outlook": {
            "short_term": "短期维持强势。今日放量上涨，突破9.5元平台，上方供应密集区10.5-11元，下方需求支撑区9.0元。老鸭头形态确认后大概率展开主升浪。",
            "mid_term": "中期看好。威科夫吸筹完成进入上涨期，订单持续落地，2026年进入收入确认期。若放量突破10.5供应区则打开12-15元空间。",
            "core_logic": "本次异动核心驱动力是政策催化叠加机构游资共振+供需格局转换(Spring+SOS确认需求占优)，技术面老鸭头形态确认主升浪启动。",
            "supply_demand_logic": "威科夫视角: 长期横盘吸筹已完成供应吸收，Spring确认底部卖盘枯竭，SOS确认需求突破供应防线。当前处于需求>供应的有利格局，上方10.5元为前期套牢盘供应区。",
            "risks": [
                "AI/机器人概念退潮风险",
                "订单交付不及预期",
                "短期涨幅大，获利盘回吐(供应释放)",
                "大盘系统性回调",
                "若出现天量滞涨则供应可能涌出(供需反转预警)"
            ]
        },
        "sources": [
            {"title": "[示例] 公司公告-智驾订单", "url": "#demo-需替换为真实链接", "date": today_str, "source": "巨潮资讯"},
            {"title": "今日资金流向", "url": "https://data.10jqka.com.cn/funds/ggzjl/board/002195/", "date": today_str, "source": "同花顺"},
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


def validate_temperature_history(data):
    """
    校验温度历史数据的日期准确性
    - 检查是否包含周末日期
    - 检查日期是否与K线数据一致
    - 检查是否有程序化计算来源标注
    """
    temp_data = data.get("market_temperature", {})
    history = temp_data.get("history", [])
    
    if not history:
        return data
    
    warnings = []
    errors = []
    
    # 1. 检查是否有数据来源标注
    source = temp_data.get("history_source", "")
    if not source:
        warnings.append("⚠️ 温度历史缺少 history_source 字段，无法追溯数据来源")
    
    # 2. 获取当前年份用于日期解析
    current_year = datetime.now().year
    
    # 3. 逐条检查日期是否是周末
    weekend_dates = []
    for item in history:
        date_str = item.get("date", "")
        if not date_str or len(date_str) < 5:
            continue
        try:
            month = int(date_str[:2])
            day = int(date_str[3:5])
            dt = datetime(current_year, month, day)
            weekday = dt.weekday()  # 0=Mon, 5=Sat, 6=Sun
            if weekday >= 5:
                day_name = "周六" if weekday == 5 else "周日"
                weekend_dates.append(f"{date_str}({day_name})")
                errors.append(f"❌ 日期 {date_str} 是{day_name}，不是交易日!")
        except (ValueError, IndexError):
            warnings.append(f"⚠️ 无法解析日期: {date_str}")
    
    # 4. 检查日期是否连续合理(不应有周六/周日)
    if weekend_dates:
        print(f"\n🚨 温度历史日期校验失败!")
        print(f"   发现 {len(weekend_dates)} 个非交易日: {', '.join(weekend_dates)}")
        print(f"   ❌ 温度历史日期必须来自真实K线数据，禁止包含周末/假日!")
        # 自动过滤掉周末日期
        valid_history = []
        for item in history:
            date_str = item.get("date", "")
            try:
                month = int(date_str[:2])
                day = int(date_str[3:5])
                dt = datetime(current_year, month, day)
                if dt.weekday() < 5:
                    valid_history.append(item)
            except (ValueError, IndexError):
                valid_history.append(item)
        
        removed_count = len(history) - len(valid_history)
        print(f"   🔧 已自动移除 {removed_count} 个非交易日数据点")
        temp_data["history"] = valid_history
        history = valid_history
    
    # 5. 检查温度值范围
    out_of_range = []
    for item in history:
        v = item.get("value", 0)
        if v < 0 or v > 100:
            out_of_range.append(f"{item.get('date','')}={v}")
    if out_of_range:
        warnings.append(f"⚠️ 温度值超出0-100范围: {', '.join(out_of_range)}")
    
    # 输出校验结果
    if not errors and not warnings:
        print(f"🌡️ 温度历史校验通过: {len(history)}个数据点，全部为有效交易日\n")
    else:
        for w in warnings:
            print(f"   {w}")
        print()
    
    return data


def validate_dates(data):
    """
    校验报告中的日期时效性
    - analysis_date 应为最近交易日 (不超过3天)
    - price_time 应与 analysis_date 一致
    - 标记为 today 的 triggers 日期应与 analysis_date 一致
    - fund_flow 日期应与 analysis_date 一致
    """
    from datetime import timedelta
    
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    warnings = []
    errors = []
    
    # 1. 校验 analysis_date
    analysis_date_str = data.get("analysis_date", "")
    if not analysis_date_str:
        errors.append("❌ 缺少 analysis_date 字段!")
    else:
        try:
            analysis_dt = datetime.strptime(analysis_date_str, "%Y-%m-%d")
            days_diff = (now - analysis_dt).days
            
            if days_diff < 0:
                errors.append(f"❌ analysis_date={analysis_date_str} 是未来日期!")
            elif days_diff > 5:
                errors.append(f"❌ analysis_date={analysis_date_str} 距今已{days_diff}天，数据严重过期! (今天={today_str})")
            elif days_diff > 3:
                warnings.append(f"⚠️ analysis_date={analysis_date_str} 距今{days_diff}天，数据可能过期 (今天={today_str})")
            elif days_diff > 0:
                # 1-3天可能是周末，检查是否合理
                if analysis_dt.weekday() < 5:  # 工作日
                    if days_diff == 1 and now.weekday() in [0, 6]:  # 周一或周日看周五的数据
                        pass  # 合理
                    elif days_diff <= 2 and now.weekday() == 0:  # 周一看周四/周五
                        pass
                    else:
                        warnings.append(f"⚠️ analysis_date={analysis_date_str} 非今日({today_str})，请确认是否为最近交易日")
        except ValueError:
            errors.append(f"❌ analysis_date 格式错误: {analysis_date_str} (应为YYYY-MM-DD)")
    
    # 2. 校验 price_time 与 analysis_date 一致
    stock = data.get("stock", {})
    price_time = stock.get("price_time", "")
    if price_time and analysis_date_str:
        if not price_time.startswith(analysis_date_str):
            errors.append(f"❌ price_time={price_time} 与 analysis_date={analysis_date_str} 不一致!")
    
    # 3. 校验 today 标记的 triggers 日期
    triggers = data.get("triggers", [])
    for t in triggers:
        if t.get("freshness") == "today" and t.get("date"):
            if t["date"] != analysis_date_str:
                errors.append(f"❌ trigger '{t.get('title', '')[:20]}...' 标记为today但日期={t['date']}，应为{analysis_date_str}")
    
    # 4. 校验 fund_flow 日期
    fund_flow = data.get("fund_flow", {})
    ff_date = fund_flow.get("date", "")
    if ff_date and analysis_date_str:
        if ff_date != analysis_date_str:
            warnings.append(f"⚠️ fund_flow日期={ff_date} 与 analysis_date={analysis_date_str} 不一致")
    
    # 5. 校验年份一致性 (所有触发因素的年份)
    if analysis_date_str:
        analysis_year = analysis_date_str[:4]
        for t in triggers:
            t_date = t.get("date", "")
            if t_date and t.get("freshness") == "today":
                if not t_date.startswith(analysis_year):
                    errors.append(f"❌ trigger '{t.get('title', '')[:20]}...' 年份={t_date[:4]}，与分析年份{analysis_year}不一致!")
    
    # 输出校验结果
    if errors or warnings:
        print(f"\n{'🚨' if errors else '⚠️'} 日期时效性校验{'失败' if errors else '警告'}!")
        for e in errors:
            print(f"   {e}")
        for w in warnings:
            print(f"   {w}")
        if not errors:
            print(f"   ℹ️  以上为警告，不影响报告生成")
        print()
    else:
        print(f"📅 日期校验通过: analysis_date={analysis_date_str}, price_time={price_time}\n")
    
    return data


def validate_supply_demand(data):
    """
    校验威科夫供需分析数据的完整性和一致性
    - 供需得分范围: -100 ~ +100
    - 威科夫阶段代码: 1-4
    - 量比合理性: > 0
    - 事件日期: 非周末
    - 供需区间逻辑: supply_zones > demand_zones
    - 得分与结论一致性
    """
    sd = data.get("supply_demand", {})
    
    if not sd:
        return data
    
    warnings = []
    errors = []
    
    # 1. 供需得分范围校验
    score = sd.get("supply_demand_score", 0)
    if not isinstance(score, (int, float)):
        errors.append(f"❌ supply_demand_score 类型错误: {type(score).__name__}，应为数字")
    elif score < -100 or score > 100:
        errors.append(f"❌ supply_demand_score={score} 超出范围 [-100, +100]")
    
    # 2. 威科夫阶段代码校验
    phase_code = sd.get("wyckoff_phase_code", 0)
    valid_codes = {1: "吸筹", 2: "上涨", 3: "派发", 4: "下跌"}
    if phase_code not in valid_codes:
        errors.append(f"❌ wyckoff_phase_code={phase_code} 无效，必须为 1(吸筹)/2(上涨)/3(派发)/4(下跌)")
    
    # 3. 量比合理性校验
    vpa = sd.get("volume_price_analysis", {})
    volume_ratio = vpa.get("volume_ratio", 0)
    if volume_ratio is not None and isinstance(volume_ratio, (int, float)):
        if volume_ratio <= 0:
            errors.append(f"❌ volume_ratio={volume_ratio} 无效，必须 > 0")
        elif volume_ratio > 10:
            warnings.append(f"⚠️ volume_ratio={volume_ratio} 异常偏高(>10)，请确认数据来源")
    
    # 4. 威科夫事件日期校验
    events = sd.get("wyckoff_events", [])
    current_year = datetime.now().year
    weekend_events = []
    for evt in events:
        date_str = evt.get("date", "")
        if not date_str or len(date_str) < 10:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            if dt.weekday() >= 5:
                day_name = "周六" if dt.weekday() == 5 else "周日"
                weekend_events.append(f"{date_str}({day_name}): {evt.get('event', '')}")
        except ValueError:
            warnings.append(f"⚠️ 威科夫事件日期格式错误: {date_str} (应为YYYY-MM-DD)")
    
    if weekend_events:
        for we in weekend_events:
            errors.append(f"❌ 威科夫事件日期为非交易日: {we}")
    
    # 5. 供需区间逻辑校验: supply_zones 应高于 demand_zones
    supply_zones = sd.get("supply_zones", [])
    demand_zones = sd.get("demand_zones", [])
    if supply_zones and demand_zones:
        min_supply = min(supply_zones) if supply_zones else float('inf')
        max_demand = max(demand_zones) if demand_zones else 0
        if min_supply <= max_demand:
            warnings.append(f"⚠️ 供应区最低价({min_supply}) ≤ 需求区最高价({max_demand})，供需区间可能交叉，请确认")
    
    # 6. 得分与结论一致性校验
    balance = sd.get("supply_demand_balance", "")
    if isinstance(score, (int, float)):
        if score > 20 and "供应占优" in balance:
            errors.append(f"❌ 供需得分={score}(需求占优)但结论为'{balance}'，得分与结论矛盾!")
        elif score < -20 and "需求占优" in balance:
            errors.append(f"❌ 供需得分={score}(供应占优)但结论为'{balance}'，得分与结论矛盾!")
    
    # 7. 必要字段完整性检查
    required_fields = ["wyckoff_phase", "wyckoff_phase_code", "supply_demand_score", 
                       "supply_demand_balance", "volume_price_analysis", "conclusion"]
    missing = [f for f in required_fields if not sd.get(f)]
    if missing:
        warnings.append(f"⚠️ 供需分析缺少字段: {', '.join(missing)}")
    
    # 8. phase_evidence 不能为空
    evidence = sd.get("phase_evidence", [])
    if not evidence:
        warnings.append("⚠️ phase_evidence 为空，威科夫阶段判断缺少依据")
    
    # 输出校验结果
    if errors or warnings:
        print(f"\n{'🚨' if errors else '⚠️'} 威科夫供需分析校验{'失败' if errors else '警告'}!")
        for e in errors:
            print(f"   {e}")
        for w in warnings:
            print(f"   {w}")
        if not errors:
            print(f"   ℹ️  以上为警告，不影响报告生成")
        print()
    else:
        phase_name = sd.get("wyckoff_phase", "未知")
        print(f"⚖️ 供需分析校验通过: 阶段={phase_name}, 得分={score}, 余额={balance}\n")
    
    return data


def generate_html(data):
    """生成HTML报告"""
    
    # 先校验并修复URL
    data = validate_and_fix_urls(data)
    
    # 校验日期时效性
    data = validate_dates(data)
    
    # 校验温度历史数据
    data = validate_temperature_history(data)
    
    # 校验供需分析数据
    data = validate_supply_demand(data)
    
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
    
    # 生成威科夫供需分析HTML
    supply_demand_html = ""
    sd_data = data.get("supply_demand", {})
    if sd_data and sd_data.get("wyckoff_phase"):
        sd_phase = sd_data.get("wyckoff_phase", "")
        sd_phase_code = sd_data.get("wyckoff_phase_code", 0)
        sd_score = sd_data.get("supply_demand_score", 0)
        sd_balance = sd_data.get("supply_demand_balance", "")
        sd_evidence = sd_data.get("phase_evidence", [])
        sd_vp = sd_data.get("volume_price_analysis", {})
        sd_divergence = sd_data.get("divergence", {})
        sd_events = sd_data.get("wyckoff_events", [])
        sd_supply_zones = sd_data.get("supply_zones", [])
        sd_demand_zones = sd_data.get("demand_zones", [])
        sd_exhaustion = sd_data.get("supply_exhaustion_signs", [])
        sd_demand_signs = sd_data.get("demand_strength_signs", [])
        sd_conclusion = sd_data.get("conclusion", "")
        sd_forecast = sd_data.get("supply_demand_forecast", {})
        
        # 阶段颜色和图标
        phase_config = {
            1: ("#3b82f6", "🔵", "吸筹期"),
            2: ("#ef4444", "🔴", "上涨期"),
            3: ("#f97316", "🟠", "派发期"),
            4: ("#22c55e", "🟢", "下跌期"),
        }
        sd_color, sd_emoji, sd_phase_label = phase_config.get(sd_phase_code, ("#6b7280", "⚪", "未知"))
        
        # 供需得分仪表盘颜色
        if sd_score >= 60:
            score_color = "#ef4444"
            score_label = "需求强力占优"
        elif sd_score >= 20:
            score_color = "#f97316"
            score_label = "需求略占优"
        elif sd_score >= -19:
            score_color = "#eab308"
            score_label = "供需均衡"
        elif sd_score >= -59:
            score_color = "#06b6d4"
            score_label = "供应略占优"
        else:
            score_color = "#22c55e"
            score_label = "供应强力占优"
        
        # 供需得分条 (范围 -100 ~ +100, 映射到 0% ~ 100%)
        score_pct = (sd_score + 100) / 2  # 映射到 0-100%
        
        # 阶段证据
        evidence_html = ""
        for e in sd_evidence:
            evidence_html += f'<li>{e}</li>'
        
        # 量价分析
        vp_html = ""
        if sd_vp:
            vp_pattern = sd_vp.get("pattern", "")
            vp_ratio = sd_vp.get("volume_ratio", 0)
            vp_up = sd_vp.get("up_day_avg_volume", "")
            vp_down = sd_vp.get("down_day_avg_volume", "")
            vp_interp = sd_vp.get("interpretation", "")
            
            ratio_color = "#ef4444" if vp_ratio > 1.3 else "#22c55e" if vp_ratio < 0.7 else "#eab308"
            ratio_label = "需求>供应" if vp_ratio > 1.3 else "供应>需求" if vp_ratio < 0.7 else "供需均衡"
            
            vp_html = f'''
            <div class="sd-vp-box">
                <div class="sd-vp-title">📊 量价供需分析</div>
                <div class="sd-vp-grid">
                    <div class="sd-vp-item">
                        <div class="sd-vp-label">量价模式</div>
                        <div class="sd-vp-value">{vp_pattern}</div>
                    </div>
                    <div class="sd-vp-item">
                        <div class="sd-vp-label">量比(涨/跌)</div>
                        <div class="sd-vp-value" style="color:{ratio_color}">{vp_ratio:.2f}x</div>
                        <div class="sd-vp-sub">{ratio_label}</div>
                    </div>
                    {"<div class='sd-vp-item'><div class='sd-vp-label'>上涨日均量</div><div class='sd-vp-value' style='color:#ef4444'>" + vp_up + "</div></div>" if vp_up else ""}
                    {"<div class='sd-vp-item'><div class='sd-vp-label'>下跌日均量</div><div class='sd-vp-value' style='color:#22c55e'>" + vp_down + "</div></div>" if vp_down else ""}
                </div>
                <div class="sd-vp-interp">{vp_interp}</div>
            </div>'''
        
        # 量价背离
        divergence_html = ""
        if sd_divergence:
            div_type = sd_divergence.get("type", "")
            div_detail = sd_divergence.get("detail", "")
            div_color = "#ef4444" if "顶背离" in div_type else "#22c55e" if "底背离" in div_type else "#4ade80"
            div_icon = "⚠️" if "背离" in div_type and "无" not in div_type else "✅"
            divergence_html = f'''
            <div class="sd-divergence" style="border-left-color: {div_color};">
                {div_icon} <strong>{div_type}</strong>: {div_detail}
            </div>'''
        
        # 威科夫事件时间线
        events_html = ""
        if sd_events:
            for ev in sd_events:
                ev_name = ev.get("event", "")
                ev_date = ev.get("date", "")
                ev_detail = ev.get("detail", "")
                ev_sig = ev.get("significance", "")
                sig_color = "#ef4444" if ev_sig == "高" else "#eab308" if ev_sig == "中" else "#6b7280"
                events_html += f'''
                <div class="sd-event-item">
                    <div class="sd-event-dot" style="background: {sig_color};"></div>
                    <div class="sd-event-content">
                        <div class="sd-event-header">
                            <span class="sd-event-name">{ev_name}</span>
                            <span class="sd-event-date">{ev_date}</span>
                            <span class="sd-event-sig" style="background: {sig_color};">{ev_sig}</span>
                        </div>
                        <div class="sd-event-detail">{ev_detail}</div>
                    </div>
                </div>'''
            events_html = f'''
            <div class="sd-events-box">
                <div class="sd-events-title">🔑 关键威科夫事件</div>
                <div class="sd-events-timeline">{events_html}</div>
            </div>'''
        
        # 供应区/需求区
        zones_html = ""
        if sd_supply_zones or sd_demand_zones:
            supply_tags = " ".join([f'<span class="sd-zone-tag supply">¥{z:.1f}</span>' for z in sd_supply_zones]) if sd_supply_zones else '<span class="sd-zone-na">暂无数据</span>'
            demand_tags = " ".join([f'<span class="sd-zone-tag demand">¥{z:.1f}</span>' for z in sd_demand_zones]) if sd_demand_zones else '<span class="sd-zone-na">暂无数据</span>'
            zones_html = f'''
            <div class="sd-zones">
                <div class="sd-zone-row">
                    <span class="sd-zone-label" style="color:#ef4444">▲ 供应密集区(压力)</span>
                    <div class="sd-zone-tags">{supply_tags}</div>
                </div>
                <div class="sd-zone-row">
                    <span class="sd-zone-label" style="color:#22c55e">▼ 需求支撑区(支撑)</span>
                    <div class="sd-zone-tags">{demand_tags}</div>
                </div>
            </div>'''
        
        # 供应枯竭/需求增强信号
        signals_html = ""
        if sd_exhaustion or sd_demand_signs:
            exh_items = "".join([f'<li class="sd-signal-item exhaust">{s}</li>' for s in sd_exhaustion])
            dem_items = "".join([f'<li class="sd-signal-item demand">{s}</li>' for s in sd_demand_signs])
            signals_html = f'''
            <div class="sd-signals-grid">
                {"<div class='sd-signals-col'><div class='sd-signals-title' style='color:#22c55e'>📉 供应枯竭信号</div><ul>" + exh_items + "</ul></div>" if exh_items else ""}
                {"<div class='sd-signals-col'><div class='sd-signals-title' style='color:#ef4444'>📈 需求增强信号</div><ul>" + dem_items + "</ul></div>" if dem_items else ""}
            </div>'''
        
        # 供需预判
        forecast_html = ""
        if sd_forecast:
            fc_short = sd_forecast.get("short_term", "")
            fc_mid = sd_forecast.get("mid_term", "")
            fc_key = sd_forecast.get("key_observation", "")
            forecast_html = f'''
            <div class="sd-forecast">
                <div class="sd-forecast-title">🔮 供需趋势预判</div>
                {"<div class='sd-forecast-item'><span class='sd-forecast-label'>短期:</span> " + fc_short + "</div>" if fc_short else ""}
                {"<div class='sd-forecast-item'><span class='sd-forecast-label'>中期:</span> " + fc_mid + "</div>" if fc_mid else ""}
                {"<div class='sd-forecast-key'>💡 <strong>关键观察:</strong> " + fc_key + "</div>" if fc_key else ""}
            </div>'''
        
        # 威科夫阶段指示条
        phase_defs = [
            (1, "吸筹", "#3b82f6"), (2, "上涨", "#ef4444"),
            (3, "派发", "#f97316"), (4, "下跌", "#22c55e"),
        ]
        phase_ruler_html = ""
        for pc, pname, pcolor in phase_defs:
            is_current = pc == sd_phase_code
            opacity = "1" if is_current else "0.3"
            border = f"border: 2px solid {pcolor}; box-shadow: 0 0 8px {pcolor}40;" if is_current else ""
            phase_ruler_html += f'<div class="sd-phase-seg" style="background:{pcolor}; opacity:{opacity}; {border}"><span>{pname}</span></div>'
        
        supply_demand_html = f'''
        <div class="sd-container" style="border: 1px solid {sd_color}30;">
            <!-- 阶段+得分主显示 -->
            <div class="sd-main-row">
                <div class="sd-phase-area">
                    <div class="sd-phase-emoji">{sd_emoji}</div>
                    <div class="sd-phase-name" style="color: {sd_color};">{sd_phase}</div>
                    <div class="sd-balance-badge" style="background: {score_color};">{sd_balance}</div>
                </div>
                <div class="sd-score-area">
                    <div class="sd-score-num" style="color: {score_color};">{sd_score:+d}</div>
                    <div class="sd-score-label">{score_label}</div>
                    <div class="sd-score-bar-bg">
                        <div class="sd-score-bar-center"></div>
                        <div class="sd-score-bar-fill" style="left: {min(score_pct, 50):.1f}%; width: {abs(score_pct - 50):.1f}%; background: {score_color};"></div>
                        <div class="sd-score-pointer" style="left: {score_pct:.1f}%;"></div>
                    </div>
                    <div class="sd-score-bar-labels">
                        <span style="color:#22c55e">供应占优 -100</span>
                        <span style="color:#888">均衡 0</span>
                        <span style="color:#ef4444">需求占优 +100</span>
                    </div>
                </div>
            </div>
            
            <!-- 阶段刻度条 -->
            <div class="sd-phase-ruler">{phase_ruler_html}</div>
            
            <!-- 阶段证据 -->
            <div class="sd-evidence">
                <div class="sd-evidence-title">📋 阶段判断依据</div>
                <ul class="sd-evidence-list">{evidence_html}</ul>
            </div>
            
            <!-- 量价分析 -->
            {vp_html}
            
            <!-- 量价背离 -->
            {divergence_html}
            
            <!-- 威科夫事件 -->
            {events_html}
            
            <!-- 供应区/需求区 -->
            {zones_html}
            
            <!-- 供应枯竭/需求增强信号 -->
            {signals_html}
            
            <!-- 结论 -->
            <div class="sd-conclusion">💡 {sd_conclusion}</div>
            
            <!-- 供需预判 -->
            {forecast_html}
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
    
    # 生成市场温度计HTML
    temperature_html = ""
    temp_data = data.get("market_temperature", {})
    if temp_data and temp_data.get("temperature_value") is not None:
        temp_val = temp_data.get("temperature_value", 50)
        phase = temp_data.get("phase", "未知")
        phase_code = temp_data.get("phase_code", 3)
        trend = temp_data.get("trend", "")
        trend_arrow = temp_data.get("trend_arrow", "")
        yesterday_temp = temp_data.get("yesterday_temperature", "")
        temp_change = temp_data.get("temperature_change", "")
        dimensions = temp_data.get("dimensions", {})
        entry = temp_data.get("entry_suggestion", {})
        cycle = temp_data.get("cycle_position", {})
        
        # 温度颜色渐变
        if temp_val <= 15:
            temp_color = "#3b82f6"  # 冰蓝
            phase_bg = "linear-gradient(135deg, #1e3a5f, #1a2a4a)"
            gauge_gradient = "linear-gradient(90deg, #60a5fa, #3b82f6)"
        elif temp_val <= 35:
            temp_color = "#06b6d4"  # 青色
            phase_bg = "linear-gradient(135deg, #134e5e, #1a3a4a)"
            gauge_gradient = "linear-gradient(90deg, #3b82f6, #06b6d4)"
        elif temp_val <= 55:
            temp_color = "#eab308"  # 黄色
            phase_bg = "linear-gradient(135deg, #4a3a1a, #3a2a10)"
            gauge_gradient = "linear-gradient(90deg, #06b6d4, #eab308)"
        elif temp_val <= 75:
            temp_color = "#f97316"  # 橙色
            phase_bg = "linear-gradient(135deg, #5a2a0a, #4a1a00)"
            gauge_gradient = "linear-gradient(90deg, #eab308, #f97316)"
        elif temp_val <= 90:
            temp_color = "#ef4444"  # 红色
            phase_bg = "linear-gradient(135deg, #5a1a1a, #4a0a0a)"
            gauge_gradient = "linear-gradient(90deg, #f97316, #ef4444)"
        else:
            temp_color = "#dc2626"  # 深红
            phase_bg = "linear-gradient(135deg, #6a0a0a, #5a0000)"
            gauge_gradient = "linear-gradient(90deg, #ef4444, #dc2626)"
        
        # 阶段标签
        phase_labels = {
            1: ("冰点期", "❄️"), 2: ("回暖期", "🌱"), 3: ("升温期", "☀️"),
            4: ("高潮期", "🔥"), 5: ("疯狂期", "🌋"), 6: ("崩溃期", "💀"),
        }
        phase_emoji = phase_labels.get(phase_code, ("", "🌡️"))[1]
        
        # 趋势变化颜色
        change_color_temp = "#ef4444" if str(temp_change).startswith("+") else "#22c55e" if str(temp_change).startswith("-") else "#888"
        
        # 7维度评分条
        dim_config = {
            "profit_effect": ("赚钱效应", "25%"),
            "board_height": ("连板高度", "20%"),
            "market_breadth": ("市场广度", "15%"),
            "volume_level": ("量能水平", "10%"),
            "sentiment_extreme": ("情绪极端度", "10%"),
            "leader_status": ("龙头状态", "10%"),
            "fund_trend": ("资金趋势", "10%"),
        }
        
        dims_html = ""
        for key, (label, weight) in dim_config.items():
            dim = dimensions.get(key, {})
            score = dim.get("score", 0)
            detail = dim.get("detail", "")
            # 分数颜色
            if score >= 70:
                bar_color = "#ef4444"
            elif score >= 50:
                bar_color = "#f97316"
            elif score >= 30:
                bar_color = "#eab308"
            else:
                bar_color = "#3b82f6"
            dims_html += f'''
            <div class="temp-dim-row">
                <div class="temp-dim-label">{label}<span class="temp-dim-weight">{weight}</span></div>
                <div class="temp-dim-bar-bg">
                    <div class="temp-dim-bar-fill" style="width:{score}%; background:{bar_color}"></div>
                </div>
                <div class="temp-dim-score">{score}</div>
                <div class="temp-dim-detail">{detail}</div>
            </div>'''
        
        # 阶段刻度条
        phases_ruler = ""
        phase_defs = [
            (0, 15, "冰点", "#3b82f6"), (15, 35, "回暖", "#06b6d4"),
            (35, 55, "升温", "#eab308"), (55, 75, "高潮", "#f97316"),
            (75, 90, "疯狂", "#ef4444"), (90, 100, "崩溃", "#dc2626"),
        ]
        for start, end, name, color in phase_defs:
            width = end - start
            is_current = start <= temp_val < end or (end == 100 and temp_val >= 90)
            opacity = "1" if is_current else "0.35"
            border_style = f"border: 2px solid {color}; box-shadow: 0 0 8px {color}40;" if is_current else ""
            phases_ruler += f'''<div class="temp-phase-seg" style="width:{width}%; background:{color}; opacity:{opacity}; {border_style}"><span class="temp-phase-seg-label">{name}</span></div>'''
        
        # 入场建议
        entry_html = ""
        if entry:
            market_level = entry.get("market_level", "")
            combined = entry.get("combined_assessment", "")
            position = entry.get("position_advice", "")
            warning = entry.get("key_warning", "")
            entry_html = f'''
            <div class="temp-entry">
                <div class="temp-entry-header">
                    <span class="temp-entry-level">{market_level}</span>
                    {"<span class='temp-entry-position'>" + position + "</span>" if position else ""}
                </div>
                <div class="temp-entry-text">{combined}</div>
                {"<div class='temp-entry-warning'>⚠️ " + warning + "</div>" if warning else ""}
            </div>'''
        
        # 周期位置
        cycle_html = ""
        if cycle:
            desc = cycle.get("description", "")
            from_peak = cycle.get("distance_from_peak", "")
            from_bottom = cycle.get("distance_from_bottom", "")
            progress = cycle.get("estimated_phase_progress", "")
            duration = cycle.get("phase_duration_days", "")
            cycle_html = f'''
            <div class="temp-cycle">
                <div class="temp-cycle-desc">{desc}</div>
                <div class="temp-cycle-metrics">
                    {"<span>距高潮: " + from_peak + "</span>" if from_peak else ""}
                    {"<span>距冰点: " + from_bottom + "</span>" if from_bottom else ""}
                    {"<span>阶段进度: " + progress + "</span>" if progress else ""}
                    {"<span>持续天数: " + str(duration) + "天</span>" if duration else ""}
                </div>
            </div>'''
        
        # 温度趋势折线图
        history = temp_data.get("history", [])
        chart_html = ""
        if len(history) >= 2:
            chart_w, chart_h = 780, 240
            pad_l, pad_r, pad_t, pad_b = 48, 20, 28, 40
            plot_w = chart_w - pad_l - pad_r
            plot_h = chart_h - pad_t - pad_b
            
            vals = [p["value"] for p in history]
            y_min = max(0, (min(vals) // 10) * 10 - 5)
            y_max = min(100, (max(vals) // 10 + 1) * 10 + 5)
            y_range = y_max - y_min if y_max > y_min else 1
            n = len(history)
            
            def px(i, v):
                x = pad_l + (i / max(n - 1, 1)) * plot_w
                y = pad_t + plot_h - ((v - y_min) / y_range) * plot_h
                return x, y
            
            # 阶段背景色带 + 右侧阶段标签
            phase_bands = [
                (0, 15, "#3b82f6", "冰点"), (15, 35, "#06b6d4", "回暖"),
                (35, 55, "#eab308", "升温"), (55, 75, "#f97316", "高潮"),
                (75, 90, "#ef4444", "疯狂"), (90, 100, "#dc2626", "崩溃"),
            ]
            bands_svg = ""
            for lo, hi, color, label_name in phase_bands:
                if hi <= y_min or lo >= y_max:
                    continue
                band_lo = max(lo, y_min)
                band_hi = min(hi, y_max)
                by1 = pad_t + plot_h - ((band_hi - y_min) / y_range) * plot_h
                by2 = pad_t + plot_h - ((band_lo - y_min) / y_range) * plot_h
                band_h = by2 - by1
                bands_svg += f'<rect x="{pad_l}" y="{by1:.1f}" width="{plot_w}" height="{band_h:.1f}" fill="{color}" opacity="0.07"/>'
                # 右侧阶段标签(仅当色带高度足够)
                if band_h > 14:
                    label_cy = by1 + band_h / 2
                    bands_svg += f'<text x="{chart_w - pad_r + 2}" y="{label_cy:.1f}" text-anchor="start" fill="{color}" font-size="9" dominant-baseline="middle" opacity="0.6">{label_name}</text>'
            
            # Y轴刻度线和标签
            y_gridlines = ""
            for tick in range(int(y_min), int(y_max) + 1, 10):
                if tick < y_min or tick > y_max:
                    continue
                _, ty = px(0, tick)
                y_gridlines += f'<line x1="{pad_l}" y1="{ty:.1f}" x2="{chart_w - pad_r}" y2="{ty:.1f}" stroke="#3a3a5a" stroke-width="0.5" stroke-dasharray="4,4"/>'
                y_gridlines += f'<text x="{pad_l - 8}" y="{ty:.1f}" text-anchor="end" fill="#888" font-size="10" dominant-baseline="middle">{tick}°</text>'
            
            # 折线路径坐标 (贝塞尔曲线平滑)
            points = [px(i, v) for i, v in enumerate(vals)]
            # 使用 catmull-rom 转贝塞尔平滑曲线
            def smooth_path(pts):
                if len(pts) < 2:
                    return ""
                if len(pts) == 2:
                    return f"M{pts[0][0]:.1f},{pts[0][1]:.1f} L{pts[1][0]:.1f},{pts[1][1]:.1f}"
                path = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
                for i in range(1, len(pts)):
                    x0, y0 = pts[i-1]
                    x1, y1 = pts[i]
                    # 控制点: 平滑系数
                    cpx = (x0 + x1) / 2
                    path += f" C{cpx:.1f},{y0:.1f} {cpx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
                return path
            
            line_path = smooth_path(points)
            
            # 渐变填充区域 (使用同样的平滑曲线)
            area_path = line_path + f" L{points[-1][0]:.1f},{pad_t + plot_h:.1f} L{points[0][0]:.1f},{pad_t + plot_h:.1f} Z"
            
            # 智能X轴标签: 数据点多时只显示部分日期
            x_label_step = max(1, n // 10)  # 最多显示约10个X轴日期
            # 保证首尾和关键事件日期一定显示
            show_x_label = set()
            show_x_label.add(0)
            show_x_label.add(n - 1)
            for i in range(0, n, x_label_step):
                show_x_label.add(i)
            # 有事件标签的也显示
            for i, h in enumerate(history):
                if h.get("label"):
                    show_x_label.add(i)
            
            # 智能温度值标签: 只在关键点显示(波峰/波谷/首尾/有事件)
            show_val_label = set()
            show_val_label.add(0)
            show_val_label.add(n - 1)
            for i in range(1, n - 1):
                # 局部极值
                if vals[i] >= vals[i-1] and vals[i] >= vals[i+1] and (vals[i] - min(vals[i-1], vals[i+1]) >= 3):
                    show_val_label.add(i)
                if vals[i] <= vals[i-1] and vals[i] <= vals[i+1] and (max(vals[i-1], vals[i+1]) - vals[i] >= 3):
                    show_val_label.add(i)
            # 有事件标签的
            for i, h in enumerate(history):
                if h.get("label"):
                    show_val_label.add(i)
            
            # 数据点 + 标签
            dots_svg = ""
            for i, (pt, h) in enumerate(zip(points, history)):
                x, y = pt
                v = h["value"]
                date = h.get("date", "")
                label = h.get("label", "")
                # 点颜色
                if v <= 15: dc = "#3b82f6"
                elif v <= 35: dc = "#06b6d4"
                elif v <= 55: dc = "#eab308"
                elif v <= 75: dc = "#f97316"
                else: dc = "#ef4444"
                is_last = (i == n - 1)
                is_first = (i == 0)
                
                # X轴日期标签
                if i in show_x_label:
                    dots_svg += f'<text x="{x:.1f}" y="{pad_t + plot_h + 16}" text-anchor="middle" fill="#888" font-size="9">{date}</text>'
                
                # 垂直参考虚线(仅关键点)
                if label or is_last or is_first:
                    dots_svg += f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{pad_t + plot_h:.1f}" stroke="{dc}" stroke-width="0.5" stroke-dasharray="3,3" opacity="0.3"/>'
                
                # 数据点
                if is_last:
                    dots_svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{dc}" opacity="0.2"/>'
                    dots_svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{dc}" stroke="#fff" stroke-width="2.5"/>'
                elif label:
                    dots_svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{dc}" stroke="#1e1e2e" stroke-width="2"/>'
                else:
                    dots_svg += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{dc}" stroke="#1e1e2e" stroke-width="1.5"/>'
                
                # 温度值标签
                if i in show_val_label:
                    vy = y - 14
                    fw = "bold" if is_last else "normal"
                    fs = "12" if is_last else "10"
                    fc = "#fff" if is_last else "#ccc"
                    dots_svg += f'<text x="{x:.1f}" y="{vy:.1f}" text-anchor="middle" fill="{fc}" font-size="{fs}" font-weight="{fw}">{v}°</text>'
                
                # 事件标签
                if label:
                    ly = y + 18
                    # 如果点在下方区域，标签放上方
                    if y > pad_t + plot_h * 0.65:
                        ly = y - 24 if i in show_val_label else y - 14
                    dots_svg += f'<text x="{x:.1f}" y="{ly:.1f}" text-anchor="middle" fill="#aaa" font-size="9">{label}</text>'
            
            chart_html = f'''
            <div class="temp-chart-title">近期温度趋势 <span style="font-size:12px;color:#888;font-weight:normal;">（近1个月 {n}个交易日）</span></div>
            <div class="temp-chart-container">
                <svg viewBox="0 0 {chart_w} {chart_h}" width="100%" height="{chart_h}" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="tempAreaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="{temp_color}" stop-opacity="0.25"/>
                            <stop offset="100%" stop-color="{temp_color}" stop-opacity="0.01"/>
                        </linearGradient>
                        <linearGradient id="tempLineGrad" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stop-color="#f97316"/>
                            <stop offset="40%" stop-color="#eab308"/>
                            <stop offset="70%" stop-color="#06b6d4"/>
                            <stop offset="100%" stop-color="{temp_color}"/>
                        </linearGradient>
                    </defs>
                    <!-- 阶段色带 -->
                    {bands_svg}
                    <!-- Y轴网格 -->
                    {y_gridlines}
                    <!-- 填充区域 -->
                    <path d="{area_path}" fill="url(#tempAreaGrad)"/>
                    <!-- 平滑折线 -->
                    <path d="{line_path}" fill="none" stroke="url(#tempLineGrad)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <!-- 数据点与标签 -->
                    {dots_svg}
                </svg>
            </div>'''
        
        temperature_html = f'''
        <div class="temp-container" style="background: {phase_bg}; border: 1px solid {temp_color}30;">
            <!-- 温度主显示 -->
            <div class="temp-main-row">
                <div class="temp-gauge-area">
                    <div class="temp-big-num" style="color: {temp_color};">{temp_val}°</div>
                    <div class="temp-phase-badge" style="background: {temp_color};">{phase_emoji} {phase}</div>
                    <div class="temp-trend">
                        <span class="temp-trend-arrow" style="color: {change_color_temp};">{trend_arrow}</span>
                        <span style="color: {change_color_temp};">{trend}</span>
                        {"<span class='temp-yesterday'>昨日 " + str(yesterday_temp) + "° (" + str(temp_change) + ")</span>" if yesterday_temp else ""}
                    </div>
                </div>
            </div>
            
            <!-- 阶段刻度条 -->
            <div class="temp-ruler-container">
                <div class="temp-ruler">{phases_ruler}</div>
                <div class="temp-pointer" style="left: {temp_val}%;">
                    <div class="temp-pointer-line" style="background: {temp_color};"></div>
                    <div class="temp-pointer-dot" style="background: {temp_color}; box-shadow: 0 0 10px {temp_color};"></div>
                </div>
            </div>
            
            <!-- 温度趋势折线图 -->
            {chart_html}
            
            <!-- 7维度评分 -->
            <div class="temp-dims-title">七维度评分</div>
            <div class="temp-dims">{dims_html}</div>
            
            <!-- 入场建议 -->
            {entry_html}
            
            <!-- 周期位置 -->
            {cycle_html}
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
        
        /* 威科夫供需分析样式 */
        .sd-container {{
            background: linear-gradient(135deg, #1a1a2e 0%, #1e2a3a 100%);
            border-radius: 16px;
            padding: 24px;
        }}
        
        .sd-main-row {{
            display: flex;
            align-items: center;
            gap: 32px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .sd-phase-area {{
            text-align: center;
            min-width: 160px;
        }}
        
        .sd-phase-emoji {{
            font-size: 48px;
            margin-bottom: 8px;
        }}
        
        .sd-phase-name {{
            font-size: 22px;
            font-weight: 900;
            margin-bottom: 8px;
        }}
        
        .sd-balance-badge {{
            display: inline-block;
            color: white;
            padding: 4px 16px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: bold;
        }}
        
        .sd-score-area {{
            flex: 1;
            min-width: 250px;
        }}
        
        .sd-score-num {{
            font-size: 42px;
            font-weight: 900;
            line-height: 1;
            margin-bottom: 4px;
        }}
        
        .sd-score-label {{
            font-size: 14px;
            color: #aaa;
            margin-bottom: 12px;
        }}
        
        .sd-score-bar-bg {{
            position: relative;
            height: 20px;
            background: linear-gradient(90deg, #22c55e20 0%, #eab30820 50%, #ef444420 100%);
            border-radius: 10px;
            overflow: visible;
            border: 1px solid #3a3a5a;
        }}
        
        .sd-score-bar-center {{
            position: absolute;
            left: 50%;
            top: 0;
            width: 2px;
            height: 100%;
            background: #888;
            transform: translateX(-50%);
        }}
        
        .sd-score-bar-fill {{
            position: absolute;
            top: 2px;
            height: calc(100% - 4px);
            border-radius: 8px;
            opacity: 0.8;
        }}
        
        .sd-score-pointer {{
            position: absolute;
            top: -4px;
            width: 8px;
            height: 28px;
            background: white;
            border-radius: 4px;
            transform: translateX(-50%);
            box-shadow: 0 0 8px rgba(255,255,255,0.5);
        }}
        
        .sd-score-bar-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            margin-top: 4px;
        }}
        
        .sd-phase-ruler {{
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
        }}
        
        .sd-phase-seg {{
            flex: 1;
            height: 28px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            color: white;
            font-weight: bold;
            transition: all 0.3s;
        }}
        
        .sd-evidence {{
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 16px;
        }}
        
        .sd-evidence-title {{
            font-size: 14px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 10px;
        }}
        
        .sd-evidence-list {{
            list-style: none;
            padding: 0;
        }}
        
        .sd-evidence-list li {{
            font-size: 13px;
            color: #bbb;
            padding: 4px 0 4px 18px;
            position: relative;
            line-height: 1.5;
        }}
        
        .sd-evidence-list li::before {{
            content: "▸";
            position: absolute;
            left: 2px;
            color: #6366f1;
        }}
        
        .sd-vp-box {{
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .sd-vp-title {{
            font-size: 14px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 12px;
        }}
        
        .sd-vp-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            margin-bottom: 10px;
        }}
        
        .sd-vp-item {{
            text-align: center;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            padding: 10px;
        }}
        
        .sd-vp-label {{
            font-size: 11px;
            color: #888;
            margin-bottom: 4px;
        }}
        
        .sd-vp-value {{
            font-size: 18px;
            font-weight: bold;
            color: #fff;
        }}
        
        .sd-vp-sub {{
            font-size: 11px;
            color: #aaa;
            margin-top: 2px;
        }}
        
        .sd-vp-interp {{
            font-size: 13px;
            color: #ccc;
            line-height: 1.5;
            padding: 10px;
            background: rgba(255,255,255,0.02);
            border-radius: 8px;
        }}
        
        .sd-divergence {{
            font-size: 13px;
            color: #ddd;
            padding: 10px 14px;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            border-left: 3px solid #4ade80;
            margin-bottom: 16px;
        }}
        
        .sd-events-box {{
            margin-bottom: 16px;
        }}
        
        .sd-events-title {{
            font-size: 14px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 12px;
        }}
        
        .sd-events-timeline {{
            position: relative;
            padding-left: 16px;
        }}
        
        .sd-events-timeline::before {{
            content: "";
            position: absolute;
            left: 5px;
            top: 4px;
            bottom: 4px;
            width: 2px;
            background: #3a3a5a;
        }}
        
        .sd-event-item {{
            position: relative;
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            padding-left: 8px;
        }}
        
        .sd-event-dot {{
            position: absolute;
            left: -16px;
            top: 6px;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            border: 2px solid #1a1a2e;
        }}
        
        .sd-event-content {{
            flex: 1;
            background: rgba(255,255,255,0.03);
            border-radius: 8px;
            padding: 10px 14px;
        }}
        
        .sd-event-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
            flex-wrap: wrap;
        }}
        
        .sd-event-name {{
            font-size: 14px;
            font-weight: bold;
            color: #fff;
        }}
        
        .sd-event-date {{
            font-size: 12px;
            color: #888;
        }}
        
        .sd-event-sig {{
            font-size: 10px;
            color: white;
            padding: 2px 8px;
            border-radius: 8px;
        }}
        
        .sd-event-detail {{
            font-size: 13px;
            color: #aaa;
            line-height: 1.5;
        }}
        
        .sd-zones {{
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 16px;
        }}
        
        .sd-zone-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 6px 0;
            flex-wrap: wrap;
        }}
        
        .sd-zone-label {{
            font-size: 13px;
            font-weight: bold;
            min-width: 160px;
        }}
        
        .sd-zone-tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .sd-zone-tag {{
            padding: 4px 14px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
        }}
        
        .sd-zone-tag.supply {{
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}
        
        .sd-zone-tag.demand {{
            background: rgba(34, 197, 94, 0.15);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }}
        
        .sd-zone-na {{
            font-size: 13px;
            color: #666;
        }}
        
        .sd-signals-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}
        
        .sd-signals-col {{
            background: rgba(255,255,255,0.02);
            border-radius: 10px;
            padding: 14px;
        }}
        
        .sd-signals-title {{
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .sd-signals-col ul {{
            list-style: none;
            padding: 0;
        }}
        
        .sd-signal-item {{
            font-size: 12px;
            color: #bbb;
            padding: 4px 0 4px 16px;
            position: relative;
            line-height: 1.5;
        }}
        
        .sd-signal-item.exhaust::before {{
            content: "↓";
            position: absolute;
            left: 2px;
            color: #22c55e;
        }}
        
        .sd-signal-item.demand::before {{
            content: "↑";
            position: absolute;
            left: 2px;
            color: #ef4444;
        }}
        
        .sd-conclusion {{
            font-size: 14px;
            color: #ddd;
            padding: 14px 16px;
            background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05));
            border-radius: 10px;
            border-left: 3px solid #6366f1;
            line-height: 1.6;
            margin-bottom: 16px;
        }}
        
        .sd-forecast {{
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 14px;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .sd-forecast-title {{
            font-size: 14px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 10px;
        }}
        
        .sd-forecast-item {{
            font-size: 13px;
            color: #ccc;
            padding: 6px 0;
            line-height: 1.5;
        }}
        
        .sd-forecast-label {{
            font-weight: bold;
            color: #8b5cf6;
        }}
        
        .sd-forecast-key {{
            margin-top: 8px;
            font-size: 13px;
            color: #eab308;
            padding: 8px 12px;
            background: rgba(234, 179, 8, 0.08);
            border-radius: 8px;
            border-left: 3px solid #eab308;
        }}
        
        .sd-forecast-key strong {{
            color: #fbbf24;
        }}
        
        /* 市场温度计样式 */
        .temp-container {{
            border-radius: 16px;
            padding: 24px;
            position: relative;
        }}
        
        .temp-main-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }}
        
        .temp-gauge-area {{
            text-align: center;
        }}
        
        .temp-big-num {{
            font-size: 72px;
            font-weight: 900;
            line-height: 1;
            letter-spacing: -4px;
            text-shadow: 0 0 30px currentColor;
        }}
        
        .temp-phase-badge {{
            display: inline-block;
            color: white;
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 16px;
            font-weight: bold;
            margin-top: 8px;
        }}
        
        .temp-trend {{
            margin-top: 10px;
            font-size: 14px;
            color: #ccc;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}
        
        .temp-trend-arrow {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        .temp-yesterday {{
            font-size: 12px;
            color: #888;
            background: #2a2a40;
            padding: 2px 10px;
            border-radius: 10px;
        }}
        
        /* 阶段刻度条 */
        .temp-ruler-container {{
            position: relative;
            margin: 20px 0 30px;
            padding: 0 4px;
        }}
        
        .temp-ruler {{
            display: flex;
            height: 28px;
            border-radius: 14px;
            overflow: hidden;
            gap: 2px;
        }}
        
        .temp-phase-seg {{
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 4px;
            transition: all 0.3s;
        }}
        
        .temp-phase-seg-label {{
            font-size: 11px;
            color: white;
            font-weight: bold;
            text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        }}
        
        .temp-pointer {{
            position: absolute;
            top: -6px;
            transform: translateX(-50%);
        }}
        
        .temp-pointer-line {{
            width: 3px;
            height: 40px;
            margin: 0 auto;
            border-radius: 2px;
        }}
        
        .temp-pointer-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin: -2px auto 0;
            border: 2px solid white;
        }}
        
        /* 温度趋势折线图 */
        .temp-chart-title {{
            font-size: 14px;
            font-weight: bold;
            color: #fff;
            margin: 20px 0 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .temp-chart-container {{
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 12px 8px 4px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.05);
            overflow-x: auto;
        }}
        
        .temp-chart-container svg {{
            display: block;
            min-width: 500px;
        }}
        
        /* 7维度评分 */
        .temp-dims-title {{
            font-size: 14px;
            font-weight: bold;
            color: #fff;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        
        .temp-dims {{
            margin-bottom: 20px;
        }}
        
        .temp-dim-row {{
            display: grid;
            grid-template-columns: 110px 1fr 36px;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
            padding: 4px 0;
        }}
        
        .temp-dim-label {{
            font-size: 12px;
            color: #ccc;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        
        .temp-dim-weight {{
            font-size: 10px;
            color: #666;
            background: #2a2a40;
            padding: 1px 5px;
            border-radius: 6px;
        }}
        
        .temp-dim-bar-bg {{
            height: 16px;
            background: #1a1a30;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .temp-dim-bar-fill {{
            height: 100%;
            border-radius: 8px;
            transition: width 0.5s ease;
            min-width: 4px;
        }}
        
        .temp-dim-score {{
            font-size: 13px;
            font-weight: bold;
            color: #ddd;
            text-align: right;
        }}
        
        .temp-dim-detail {{
            grid-column: 1 / -1;
            font-size: 11px;
            color: #666;
            padding-left: 114px;
            margin-top: -4px;
            margin-bottom: 4px;
        }}
        
        /* 入场建议 */
        .temp-entry {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 14px;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        
        .temp-entry-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .temp-entry-level {{
            font-size: 18px;
            font-weight: bold;
            color: #fbbf24;
        }}
        
        .temp-entry-position {{
            font-size: 13px;
            color: #8b5cf6;
            background: rgba(139,92,246,0.15);
            padding: 4px 12px;
            border-radius: 10px;
        }}
        
        .temp-entry-text {{
            font-size: 13px;
            color: #ccc;
            line-height: 1.6;
        }}
        
        .temp-entry-warning {{
            margin-top: 10px;
            font-size: 12px;
            color: #f97316;
            padding: 8px 12px;
            background: rgba(249,115,22,0.1);
            border-radius: 8px;
            border-left: 3px solid #f97316;
        }}
        
        /* 周期位置 */
        .temp-cycle {{
            background: rgba(255,255,255,0.03);
            border-radius: 10px;
            padding: 12px 14px;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .temp-cycle-desc {{
            font-size: 13px;
            color: #aaa;
            line-height: 1.5;
            margin-bottom: 8px;
        }}
        
        .temp-cycle-metrics {{
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            font-size: 12px;
            color: #888;
        }}
        
        .temp-cycle-metrics span {{
            background: #1a1a30;
            padding: 3px 10px;
            border-radius: 8px;
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
        
        {"<div class='section'><h2>🌡️ 市场温度计</h2>" + temperature_html + "</div>" if temperature_html else ""}
        
        <div class="section">
            <h2>🔥 近期触发因素</h2>
            {triggers_html if triggers_html else '<p style="color:#888">暂无近期触发因素数据</p>'}
        </div>
        
        {"<div class='section'><h2>⚔️ 多方博弈分析</h2>" + participants_html + "</div>" if participants_html else ""}
        
        {"<div class='section'><h2>⚖️ 威科夫供需分析</h2>" + supply_demand_html + "</div>" if supply_demand_html else ""}
        
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
            {"<div class='core-logic-box' style='border-left-color:#3b82f6; background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(59,130,246,0.03));'>⚖️ <strong>供需逻辑:</strong> " + outlook.get("supply_demand_logic", "") + "</div>" if outlook.get("supply_demand_logic") else ""}
            {"<div class='core-logic-box' style='border-left-color:#8b5cf6; background:linear-gradient(135deg,rgba(139,92,246,0.1),rgba(139,92,246,0.03));'>🌡️ <strong>温度指引:</strong> " + outlook.get("temperature_guidance", "") + "</div>" if outlook.get("temperature_guidance") else ""}
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
    
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ 报告已生成: {os.path.abspath(args.output)}")
    return 0


if __name__ == "__main__":
    exit(main())
