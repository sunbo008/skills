# Skills

个人维护的 AI Skills 集合，专为 Claude / Cursor 等 AI 助手设计。每个 Skill 包含结构化的工作流程描述和辅助脚本，让 AI 能够高效地完成特定领域的复杂任务。

## 技能列表

| 技能 | 说明 | 关键词触发 |
|------|------|-----------|
| [个股异动分析](skills/stock-anomaly-analysis/) | 深度分析个股异动原因，追踪主力资金、龙虎榜、政策面等，生成 HTML 分析报告 | 个股异动、涨停原因、异动分析、主力分析 |
| [周板块热度图](skills/weekly-sector-heatmap/) | 收集本周 A 股热门板块 TOP10，生成交互式热力跟踪图 | 板块热度、热门板块、板块热力图、周板块分析 |

## 目录结构

```
skills/
├── README.md                          # 项目说明
├── requirements.txt                   # Python 依赖
├── .gitignore
└── skills/                            # 技能目录
    ├── stock-anomaly-analysis/        # 个股异动分析
    │   ├── SKILL.md                   # 技能定义（工作流程 + 规则）
    │   └── scripts/
    │       ├── fetch_stock_data.py    # 数据获取（腾讯财经/东方财富 API）
    │       └── generate_report.py     # HTML 报告生成
    └── weekly-sector-heatmap/         # 周板块热度图
        ├── SKILL.md                   # 技能定义
        └── scripts/
            └── generate_heatmap.py    # 交互式热力图生成（ECharts）
```

## 技能结构规范

每个技能遵循统一的目录结构：

```
skills/<skill-name>/
├── SKILL.md          # 必需 — 技能定义文件
└── scripts/          # 可选 — 辅助脚本
    └── *.py
```

### SKILL.md 格式

```markdown
---
name: skill-name
description: 技能描述。当用户提到"关键词A"、"关键词B"时使用此技能。
---

# 技能标题

简要说明。

## 工作流程

### 第一步: ...
### 第二步: ...

## scripts/

- `script_name.py`: 脚本说明
```

- **YAML frontmatter**: 包含 `name` 和 `description`，`description` 中应列出触发关键词
- **工作流程**: 清晰的分步骤说明，AI 会按步骤执行
- **脚本说明**: 列出 `scripts/` 下各脚本的用途和用法

## 使用方式

### 通过 OpenSkills 安装（推荐）

使用 [OpenSkills](https://github.com/anthropics/openskills) 一键安装：

```bash
# 安装全部技能
npx openskills install sunbo008/skills

# 安装单个技能
npx openskills install sunbo008/skills/stock-anomaly-analysis
npx openskills install sunbo008/skills/weekly-sector-heatmap
```

### 在 Claude Code 中手动安装

将技能复制到 Claude 的 skills 目录：

```bash
# 将整个 skills 目录链接或复制到 ~/.claude/skills/
cp -r skills/* ~/.claude/skills/
```

安装后，当对话中提到相关关键词时，Claude 会自动识别并调用对应技能。

### 在 Cursor 中手动安装

将技能复制到 Cursor 的 skills 目录：

```bash
# 将整个 skills 目录链接或复制到 ~/.cursor/skills/
cp -r skills/* ~/.cursor/skills/
```

### 运行辅助脚本

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 示例：获取股票实时数据
python skills/stock-anomaly-analysis/scripts/fetch_stock_data.py 002195

# 示例：生成板块热力图
python skills/weekly-sector-heatmap/scripts/generate_heatmap.py --data data.json --output heatmap.html
```

## 添加新技能

1. 在 `skills/` 下创建新目录，使用 kebab-case 命名：

   ```bash
   mkdir -p skills/my-new-skill/scripts
   ```

2. 创建 `SKILL.md`，包含 YAML frontmatter 和工作流程描述（参考上方格式规范）

3. 如需辅助脚本，放入 `scripts/` 目录，并在 `SKILL.md` 末尾说明用法

4. 更新本 README 的技能列表

## 依赖

- Python >= 3.10
- 依赖包详见 [requirements.txt](requirements.txt)

## 许可

仅供个人使用。
