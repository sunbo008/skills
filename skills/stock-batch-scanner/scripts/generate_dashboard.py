#!/usr/bin/env python3
"""
筛选结果看板生成器
读取 screened.json，生成交互式HTML看板 (排序/搜索/筛选)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
import os
import argparse
from datetime import datetime
from pathlib import Path


def generate_dashboard_html(data: dict) -> str:
    scan_date = data.get("scan_date", "")
    scan_mode = data.get("scan_mode", "")
    total_scanned = data.get("total_scanned", 0)
    results = data.get("results", [])

    rows_json = json.dumps(results, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全市场扫描看板 - {scan_date}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; background: #0d1117; color: #e6edf3; }}
.header {{ background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%); padding: 24px 32px; border-bottom: 1px solid #30363d; }}
.header h1 {{ font-size: 22px; font-weight: 600; margin-bottom: 12px; }}
.stats {{ display: flex; gap: 24px; flex-wrap: wrap; }}
.stat {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 20px; min-width: 140px; }}
.stat-label {{ font-size: 12px; color: #8b949e; margin-bottom: 4px; }}
.stat-value {{ font-size: 24px; font-weight: 700; }}
.stat-value.green {{ color: #3fb950; }}
.stat-value.blue {{ color: #58a6ff; }}
.stat-value.orange {{ color: #d29922; }}
.toolbar {{ padding: 16px 32px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }}
.search-box {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 8px 14px; color: #e6edf3; font-size: 14px; width: 240px; outline: none; }}
.search-box:focus {{ border-color: #58a6ff; }}
.filter-btn {{ background: #21262d; border: 1px solid #30363d; border-radius: 6px; padding: 8px 14px; color: #e6edf3; cursor: pointer; font-size: 13px; }}
.filter-btn:hover {{ background: #30363d; }}
.filter-btn.active {{ background: #1f6feb; border-color: #1f6feb; }}
.table-wrap {{ padding: 0 32px 32px; overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th {{ background: #161b22; color: #8b949e; font-weight: 600; padding: 10px 12px; text-align: left; border-bottom: 2px solid #30363d; cursor: pointer; user-select: none; white-space: nowrap; }}
th:hover {{ color: #e6edf3; }}
th.sorted-asc::after {{ content: " ▲"; color: #58a6ff; }}
th.sorted-desc::after {{ content: " ▼"; color: #58a6ff; }}
td {{ padding: 10px 12px; border-bottom: 1px solid #21262d; white-space: nowrap; }}
tr:hover td {{ background: #161b22; }}
.up {{ color: #f85149; }}
.down {{ color: #3fb950; }}
.neutral {{ color: #8b949e; }}
.score-bar {{ display: inline-block; height: 6px; border-radius: 3px; background: #1f6feb; vertical-align: middle; margin-left: 6px; }}
.tag {{ display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin: 1px; }}
.tag-zt {{ background: #f8514920; color: #f85149; border: 1px solid #f8514940; }}
.code-link {{ color: #58a6ff; text-decoration: none; }}
.code-link:hover {{ text-decoration: underline; }}
.empty {{ text-align: center; padding: 60px; color: #8b949e; font-size: 16px; }}
.footer {{ text-align: center; padding: 20px; color: #484f58; font-size: 12px; }}
</style>
</head>
<body>

<div class="header">
  <h1>全市场扫描看板</h1>
  <div class="stats">
    <div class="stat">
      <div class="stat-label">扫描日期</div>
      <div class="stat-value blue">{scan_date[:10] if scan_date else '-'}</div>
    </div>
    <div class="stat">
      <div class="stat-label">扫描模式</div>
      <div class="stat-value">{'本地' if scan_mode == 'local' else 'API'}</div>
    </div>
    <div class="stat">
      <div class="stat-label">扫描总数</div>
      <div class="stat-value">{total_scanned}</div>
    </div>
    <div class="stat">
      <div class="stat-label">通过筛选</div>
      <div class="stat-value green">{len(results)}</div>
    </div>
    <div class="stat">
      <div class="stat-label">筛选条件</div>
      <div class="stat-value orange" style="font-size:14px">涨停+多头+右侧</div>
    </div>
  </div>
</div>

<div class="toolbar">
  <input type="text" class="search-box" id="searchBox" placeholder="搜索代码或名称...">
  <button class="filter-btn" onclick="filterByScore(80)">评分≥80</button>
  <button class="filter-btn" onclick="filterByScore(60)">评分≥60</button>
  <button class="filter-btn" onclick="filterByScore(0)">全部</button>
  <button class="filter-btn" onclick="filterMultiZT()">多次涨停</button>
  <span style="margin-left:auto; color:#8b949e; font-size:12px;">点击表头排序</span>
</div>

<div class="table-wrap">
<table id="resultTable">
<thead>
<tr>
  <th data-col="rank">#</th>
  <th data-col="code">代码</th>
  <th data-col="name">名称</th>
  <th data-col="price">现价</th>
  <th data-col="change_pct">今日涨跌</th>
  <th data-col="score">评分</th>
  <th data-col="limit_up_count">涨停次数</th>
  <th data-col="limit_up_dates">涨停日期</th>
  <th data-col="change_5d">5日涨幅</th>
  <th data-col="change_20d">20日涨幅</th>
  <th data-col="ma20_slope">MA20斜率</th>
  <th data-col="turnover">换手率</th>
</tr>
</thead>
<tbody id="tableBody"></tbody>
</table>
</div>

<div class="footer">
  筛选条件: 近40交易日有涨停 + MA5>MA10>MA20>MA60多头排列 + 右侧买点(MA20上升+回踩反弹确认)<br>
  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} | stock-batch-scanner
</div>

<script>
const RAW_DATA = {rows_json};
let currentData = [...RAW_DATA];
let sortCol = 'score';
let sortDir = 'desc';

function render(data) {{
  const tbody = document.getElementById('tableBody');
  if (!data.length) {{
    tbody.innerHTML = '<tr><td colspan="12" class="empty">无符合条件的股票</td></tr>';
    return;
  }}
  tbody.innerHTML = data.map((r, i) => {{
    const chgClass = r.change_pct > 0 ? 'up' : r.change_pct < 0 ? 'down' : 'neutral';
    const c5Class = r.change_5d > 0 ? 'up' : r.change_5d < 0 ? 'down' : 'neutral';
    const c20Class = r.change_20d > 0 ? 'up' : r.change_20d < 0 ? 'down' : 'neutral';
    const ztTags = (r.limit_up_dates || []).slice(-3).map(d => '<span class="tag tag-zt">' + d.slice(5) + '</span>').join('');
    const barW = Math.min(r.score, 100);
    return '<tr>' +
      '<td>' + (i+1) + '</td>' +
      '<td><a class="code-link" href="https://quote.eastmoney.com/' + (r.code.startsWith('6')?'sh':'sz') + r.code + '.html" target="_blank">' + r.code + '</a></td>' +
      '<td>' + (r.name||'') + '</td>' +
      '<td>' + (r.price ? r.price.toFixed(2) : '-') + '</td>' +
      '<td class="' + chgClass + '">' + (r.change_pct>=0?'+':'') + r.change_pct.toFixed(2) + '%</td>' +
      '<td>' + r.score + '<span class="score-bar" style="width:' + barW + 'px"></span></td>' +
      '<td>' + r.limit_up_count + '</td>' +
      '<td>' + ztTags + '</td>' +
      '<td class="' + c5Class + '">' + (r.change_5d>=0?'+':'') + r.change_5d.toFixed(1) + '%</td>' +
      '<td class="' + c20Class + '">' + (r.change_20d>=0?'+':'') + r.change_20d.toFixed(1) + '%</td>' +
      '<td>' + (r.ma20_slope||0).toFixed(2) + '%</td>' +
      '<td>' + (r.turnover||0).toFixed(2) + '%</td>' +
      '</tr>';
  }}).join('');
}}

function sortData(col) {{
  if (sortCol === col) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
  else {{ sortCol = col; sortDir = 'desc'; }}
  document.querySelectorAll('th').forEach(th => th.classList.remove('sorted-asc','sorted-desc'));
  const th = document.querySelector('th[data-col="'+col+'"]');
  if (th) th.classList.add(sortDir === 'asc' ? 'sorted-asc' : 'sorted-desc');
  currentData.sort((a,b) => {{
    let va = a[col] ?? '', vb = b[col] ?? '';
    if (typeof va === 'string') return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
    return sortDir === 'asc' ? va - vb : vb - va;
  }});
  render(currentData);
}}

function filterByScore(min) {{
  currentData = RAW_DATA.filter(r => r.score >= min);
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  render(currentData);
}}

function filterMultiZT() {{
  currentData = RAW_DATA.filter(r => r.limit_up_count >= 2);
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  render(currentData);
}}

document.getElementById('searchBox').addEventListener('input', function() {{
  const q = this.value.trim().toLowerCase();
  if (!q) {{ currentData = [...RAW_DATA]; }}
  else {{ currentData = RAW_DATA.filter(r => r.code.includes(q) || (r.name||'').toLowerCase().includes(q)); }}
  render(currentData);
}});

document.querySelectorAll('th[data-col]').forEach(th => {{
  th.addEventListener('click', () => sortData(th.dataset.col));
}});

render(currentData);
sortData('score');
</script>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(description="生成筛选结果看板")
    parser.add_argument("--data", required=True, help="screened.json 路径")
    parser.add_argument("--output", required=True, help="输出HTML路径")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    html = generate_dashboard_html(data)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 看板已生成: {output_path}")


if __name__ == "__main__":
    main()
