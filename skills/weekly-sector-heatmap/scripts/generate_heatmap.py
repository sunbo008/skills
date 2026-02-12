#!/usr/bin/env python3
"""
周板块热度图生成器

根据提供的板块热度数据生成交互式HTML热力跟踪图。
支持多种数据输入格式：JSON文件、CSV文件或Python字典。

使用示例:
    python generate_heatmap.py --data data.json --output heatmap.html
    python generate_heatmap.py --data data.csv --output heatmap.html
"""

import argparse
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>周板块热度跟踪图 - {week_range}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: #fff;
        }}
        .header h1 {{
            font-size: 2.2rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .header p {{
            color: #94a3b8;
            font-size: 1rem;
        }}
        .chart-container {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        #heatmap {{
            width: 100%;
            height: 500px;
        }}
        #trend-chart {{
            width: 100%;
            height: 400px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .stat-card h3 {{
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 8px;
        }}
        .stat-card .value {{
            color: #fff;
            font-size: 1.8rem;
            font-weight: bold;
        }}
        .stat-card .value.positive {{
            color: #10b981;
        }}
        .stat-card .value.negative {{
            color: #ef4444;
        }}
        .top-sectors {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .top-sectors h2 {{
            color: #fff;
            font-size: 1.3rem;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .sector-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 12px;
        }}
        .sector-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.05);
            padding: 12px 16px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        .sector-item:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }}
        .sector-rank {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            margin-right: 12px;
        }}
        .sector-rank.gold {{
            background: linear-gradient(135deg, #ffd700, #ffed4a);
            color: #000;
        }}
        .sector-rank.silver {{
            background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
            color: #000;
        }}
        .sector-rank.bronze {{
            background: linear-gradient(135deg, #cd7f32, #daa520);
            color: #000;
        }}
        .sector-rank.normal {{
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }}
        .sector-info {{
            flex: 1;
        }}
        .sector-name {{
            color: #fff;
            font-weight: 500;
        }}
        .sector-score {{
            color: #00d4ff;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        .footer {{
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>周板块热度跟踪图</h1>
            <p>数据周期: {week_range} | 生成时间: {generate_time}</p>
        </div>
        
        <div class="stats-grid">
            {stats_cards}
        </div>
        
        <div class="chart-container">
            <div id="heatmap"></div>
        </div>
        
        <div class="chart-container">
            <div id="trend-chart"></div>
        </div>
        
        <div class="top-sectors">
            <h2>本周热门板块 TOP 10</h2>
            <div class="sector-list">
                {sector_list}
            </div>
        </div>
        
        <div class="footer">
            <p>数据来源: 网络公开信息整理 | 仅供参考，不构成投资建议</p>
        </div>
    </div>
    
    <script>
        // 热力图数据
        const heatmapData = {heatmap_data};
        const sectors = {sectors};
        const days = {days};
        
        // 初始化热力图
        const heatmapChart = echarts.init(document.getElementById('heatmap'));
        const heatmapOption = {{
            title: {{
                text: '板块每日热度分布',
                left: 'center',
                textStyle: {{
                    color: '#fff',
                    fontSize: 16
                }}
            }},
            tooltip: {{
                position: 'top',
                formatter: function(params) {{
                    return `${{sectors[params.data[1]]}} - ${{days[params.data[0]]}}<br/>热度指数: <strong>${{params.data[2]}}</strong>`;
                }},
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#333',
                textStyle: {{
                    color: '#fff'
                }}
            }},
            grid: {{
                left: '15%',
                right: '10%',
                top: '15%',
                bottom: '15%'
            }},
            xAxis: {{
                type: 'category',
                data: days,
                splitArea: {{
                    show: true
                }},
                axisLabel: {{
                    color: '#94a3b8'
                }},
                axisLine: {{
                    lineStyle: {{
                        color: '#334155'
                    }}
                }}
            }},
            yAxis: {{
                type: 'category',
                data: sectors,
                splitArea: {{
                    show: true
                }},
                axisLabel: {{
                    color: '#94a3b8'
                }},
                axisLine: {{
                    lineStyle: {{
                        color: '#334155'
                    }}
                }}
            }},
            visualMap: {{
                min: 0,
                max: 100,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '0%',
                inRange: {{
                    color: ['#1e3a5f', '#2563eb', '#7c3aed', '#ec4899', '#ef4444']
                }},
                textStyle: {{
                    color: '#94a3b8'
                }}
            }},
            series: [{{
                name: '热度',
                type: 'heatmap',
                data: heatmapData,
                label: {{
                    show: true,
                    color: '#fff',
                    fontSize: 10
                }},
                emphasis: {{
                    itemStyle: {{
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }}
                }}
            }}]
        }};
        heatmapChart.setOption(heatmapOption);
        
        // 趋势图数据
        const trendData = {trend_data};
        
        // 初始化趋势图
        const trendChart = echarts.init(document.getElementById('trend-chart'));
        const trendOption = {{
            title: {{
                text: '热门板块周趋势变化',
                left: 'center',
                textStyle: {{
                    color: '#fff',
                    fontSize: 16
                }}
            }},
            tooltip: {{
                trigger: 'axis',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#333',
                textStyle: {{
                    color: '#fff'
                }}
            }},
            legend: {{
                data: sectors.slice(0, 5),
                top: '10%',
                textStyle: {{
                    color: '#94a3b8'
                }}
            }},
            grid: {{
                left: '5%',
                right: '5%',
                bottom: '5%',
                top: '25%',
                containLabel: true
            }},
            xAxis: {{
                type: 'category',
                boundaryGap: false,
                data: days,
                axisLabel: {{
                    color: '#94a3b8'
                }},
                axisLine: {{
                    lineStyle: {{
                        color: '#334155'
                    }}
                }}
            }},
            yAxis: {{
                type: 'value',
                name: '热度指数',
                nameTextStyle: {{
                    color: '#94a3b8'
                }},
                axisLabel: {{
                    color: '#94a3b8'
                }},
                axisLine: {{
                    lineStyle: {{
                        color: '#334155'
                    }}
                }},
                splitLine: {{
                    lineStyle: {{
                        color: '#1e293b'
                    }}
                }}
            }},
            series: trendData
        }};
        trendChart.setOption(trendOption);
        
        // 响应式调整
        window.addEventListener('resize', function() {{
            heatmapChart.resize();
            trendChart.resize();
        }});
    </script>
</body>
</html>
'''


def load_data_from_json(filepath: str) -> Dict[str, Any]:
    """从JSON文件加载数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_data_from_csv(filepath: str) -> Dict[str, Any]:
    """从CSV文件加载数据
    
    CSV格式要求:
    第一行: 板块名称
    第一列: 日期 (如: 周一, 周二, ...)
    其余: 热度数值
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if len(rows) < 2:
        raise ValueError("CSV文件格式错误: 至少需要2行数据")
    
    sectors = rows[0][1:]  # 第一行除了第一个单元格外都是板块名称
    days = []
    data = {}
    
    for row in rows[1:]:
        if len(row) < 2:
            continue
        day = row[0]
        days.append(day)
        data[day] = {}
        for i, value in enumerate(row[1:]):
            if i < len(sectors):
                try:
                    data[day][sectors[i]] = float(value)
                except ValueError:
                    data[day][sectors[i]] = 0
    
    return {
        "sectors": sectors,
        "days": days,
        "data": data
    }


def generate_heatmap_data(data: Dict[str, Any]) -> List[List]:
    """生成ECharts热力图所需的数据格式"""
    sectors = data["sectors"]
    days = data["days"]
    daily_data = data["data"]
    
    heatmap_data = []
    for day_idx, day in enumerate(days):
        for sector_idx, sector in enumerate(sectors):
            value = daily_data.get(day, {}).get(sector, 0)
            heatmap_data.append([day_idx, sector_idx, round(value, 1)])
    
    return heatmap_data


def generate_trend_data(data: Dict[str, Any]) -> List[Dict]:
    """生成趋势图数据"""
    sectors = data["sectors"][:5]  # 取前5个板块
    days = data["days"]
    daily_data = data["data"]
    
    colors = ['#00d4ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444']
    
    trend_data = []
    for idx, sector in enumerate(sectors):
        series_data = []
        for day in days:
            value = daily_data.get(day, {}).get(sector, 0)
            series_data.append(round(value, 1))
        
        trend_data.append({
            "name": sector,
            "type": "line",
            "smooth": True,
            "data": series_data,
            "lineStyle": {"width": 3},
            "itemStyle": {"color": colors[idx % len(colors)]},
            "areaStyle": {"opacity": 0.1}
        })
    
    return trend_data


def calculate_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """计算统计数据"""
    sectors = data["sectors"]
    days = data["days"]
    daily_data = data["data"]
    
    # 计算各板块平均热度
    sector_avg = {}
    for sector in sectors:
        values = [daily_data.get(day, {}).get(sector, 0) for day in days]
        sector_avg[sector] = sum(values) / len(values) if values else 0
    
    # 排序获取TOP10
    sorted_sectors = sorted(sector_avg.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # 计算整体统计
    all_values = []
    for day in days:
        for sector in sectors:
            all_values.append(daily_data.get(day, {}).get(sector, 0))
    
    max_heat = max(all_values) if all_values else 0
    avg_heat = sum(all_values) / len(all_values) if all_values else 0
    
    # 找出最热板块
    hottest_sector = sorted_sectors[0][0] if sorted_sectors else "N/A"
    
    return {
        "top_sectors": sorted_sectors,
        "max_heat": round(max_heat, 1),
        "avg_heat": round(avg_heat, 1),
        "hottest_sector": hottest_sector,
        "total_sectors": len(sectors)
    }


def generate_stats_cards(stats: Dict[str, Any]) -> str:
    """生成统计卡片HTML"""
    cards = [
        f'''<div class="stat-card">
            <h3>最热板块</h3>
            <div class="value">{stats["hottest_sector"]}</div>
        </div>''',
        f'''<div class="stat-card">
            <h3>最高热度</h3>
            <div class="value positive">{stats["max_heat"]}</div>
        </div>''',
        f'''<div class="stat-card">
            <h3>平均热度</h3>
            <div class="value">{stats["avg_heat"]}</div>
        </div>''',
        f'''<div class="stat-card">
            <h3>追踪板块数</h3>
            <div class="value">{stats["total_sectors"]}</div>
        </div>'''
    ]
    return '\n'.join(cards)


def generate_sector_list(stats: Dict[str, Any]) -> str:
    """生成板块排行列表HTML"""
    items = []
    for idx, (sector, score) in enumerate(stats["top_sectors"], 1):
        if idx == 1:
            rank_class = "gold"
        elif idx == 2:
            rank_class = "silver"
        elif idx == 3:
            rank_class = "bronze"
        else:
            rank_class = "normal"
        
        items.append(f'''<div class="sector-item">
            <span class="sector-rank {rank_class}">{idx}</span>
            <div class="sector-info">
                <div class="sector-name">{sector}</div>
            </div>
            <span class="sector-score">{round(score, 1)}</span>
        </div>''')
    
    return '\n'.join(items)


def generate_html(data: Dict[str, Any], output_path: str, week_range: str = None):
    """生成完整的HTML文件"""
    # 计算日期范围
    if not week_range:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_range = f"{week_start.strftime('%Y-%m-%d')} 至 {week_end.strftime('%Y-%m-%d')}"
    
    # 生成各部分数据
    heatmap_data = generate_heatmap_data(data)
    trend_data = generate_trend_data(data)
    stats = calculate_stats(data)
    stats_cards = generate_stats_cards(stats)
    sector_list = generate_sector_list(stats)
    
    # 填充模板
    html_content = HTML_TEMPLATE.format(
        week_range=week_range,
        generate_time=datetime.now().strftime('%Y-%m-%d %H:%M'),
        stats_cards=stats_cards,
        sector_list=sector_list,
        heatmap_data=json.dumps(heatmap_data),
        sectors=json.dumps(data["sectors"], ensure_ascii=False),
        days=json.dumps(data["days"], ensure_ascii=False),
        trend_data=json.dumps(trend_data, ensure_ascii=False)
    )
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"热力图已生成: {output_path}")
    return output_path


def create_sample_data() -> Dict[str, Any]:
    """创建示例数据用于测试"""
    sectors = [
        "人工智能", "新能源车", "光伏", "半导体", "医药生物",
        "白酒", "银行", "房地产", "军工", "消费电子"
    ]
    days = ["周一", "周二", "周三", "周四", "周五"]
    
    import random
    random.seed(42)
    
    data = {}
    for day in days:
        data[day] = {}
        for sector in sectors:
            # 为每个板块生成有趋势的随机数据
            base = random.randint(30, 80)
            data[day][sector] = base + random.randint(-15, 15)
    
    return {
        "sectors": sectors,
        "days": days,
        "data": data
    }


def main():
    parser = argparse.ArgumentParser(description='生成周板块热度跟踪图')
    parser.add_argument('--data', '-d', type=str, help='数据文件路径 (JSON或CSV格式)')
    parser.add_argument('--output', '-o', type=str, default='sector_heatmap.html', help='输出HTML文件路径')
    parser.add_argument('--week', '-w', type=str, help='周期描述 (如: 2024-01-08 至 2024-01-12)')
    parser.add_argument('--sample', action='store_true', help='使用示例数据生成演示图')
    
    args = parser.parse_args()
    
    if args.sample:
        data = create_sample_data()
    elif args.data:
        if args.data.endswith('.json'):
            data = load_data_from_json(args.data)
        elif args.data.endswith('.csv'):
            data = load_data_from_csv(args.data)
        else:
            raise ValueError("不支持的文件格式，请使用JSON或CSV文件")
    else:
        print("请指定数据文件 (--data) 或使用示例数据 (--sample)")
        return
    
    generate_html(data, args.output, args.week)


if __name__ == '__main__':
    main()
