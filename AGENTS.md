# AGENTS

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke: `npx openskills read <skill-name>` (run in your shell)
  - For multiple: `npx openskills read skill-one,skill-two`
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>cpp-architect-review</name>
<description>以Google C++软件架构师角色审查和修复开发方案。检查架构设计、代码质量、性能优化、安全性和编码规范,提供详细的改进建议和修复方案。当用户提到"审查方案"、"检查设计"、"架构评审"、"代码审查"、"C++规范检查"或需要从架构师角度评估C++代码时使用此技能。</description>
<location>project</location>
</skill>

<skill>
<name>cpp-task-driven-dev</name>
<description>C++项目迭代开发工作流。整合openspec需求分析与任务拆解、Google C++架构师角色审核、cursor-agent CLI代码开发、单测与自动化测试、验收验证的闭环迭代流程。当用户提到"任务开发"、"迭代开发"、"C++开发流程"、"C++开发"、"openspec需求"、"架构审核"、"cursor-agent开发"或需要按流程完成C++编码任务时使用此技能。</description>
<location>project</location>
</skill>

<skill>
<name>pdf-password-remover</name>
<description>移除PDF文件的权限密码(Owner Password)，解锁打印、复制、编辑等受限操作。使用libqpdf C++ API实现，独立二进制无额外运行时依赖。当用户提到"PDF解密"、"移除PDF密码"、"PDF权限密码"、"解锁PDF"、"PDF打印限制"或需要移除PDF文件的操作限制时使用此技能。</description>
<location>project</location>
</skill>

<skill>
<name>stock-anomaly-analysis</name>
<description>个股异动多维度深度分析。针对某个股票，通过网络数据从游资、主力、机构、国家监管层、散户五大维度综合分析其异动（大涨、大跌、涨停、跌停、放量等）的原因，解读多方博弈格局，并预测未来发展行情。当用户提到"个股异动"、"股票为什么涨/跌"、"涨停原因"、"异动分析"、"主力分析"、"游资分析"、"机构持仓"、"多方博弈"或需要分析某只股票突然变化的原因时使用此技能。</description>
<location>project</location>
</skill>

<skill>
<name>stock-batch-scanner</name>
<description>全A股批量扫描选股。从本地K线数据或API批量筛选"近2月涨停+多头排列+右侧买点"的股票，生成交互式看板，并衔接stock-anomaly-analysis做深度分析。当用户提到"全市场扫描"、"批量选股"、"筛选股票"、"今日选股"、"扫描全A"或需要从全市场中筛选符合条件的股票时使用此技能。</description>
<location>project</location>
</skill>

<skill>
<name>fullstack-architect-review</name>
<description>以Google前后端工程架构师角色审查前后端代码。覆盖前端(React/Vue/Angular/HTML/CSS/JS/TS)和后端(Node.js/Python/Java/Go/API设计/数据库)的架构设计、代码质量、性能优化、安全性和工程规范,提供详细改进建议和修复方案。当用户提到"前端审查"、"后端审查"、"全栈审查"、"API审查"、"前后端代码审查"、"Web架构评审"、"前端性能"、"后端性能"或需要从全栈架构师角度评估代码时使用此技能。</description>
<location>project</location>
</skill>

<skill>
<name>web-search</name>
<description>Perform web searches and fetch web page content without any API keys, supporting Baidu, Bing, and DuckDuckGo search engines. Use this skill whenever the user needs to search the internet, look up current information, find documentation, research a topic, check latest news, or fetch content from a URL. Also trigger when the user mentions searching online, googling something, looking something up on the web, or needs real-time/up-to-date information that the model doesn't have. Even if the user just casually says "search for", "look up", "query", or "find", use this skill.</description>
<location>project</location>
</skill>

<skill>
<name>weekly-sector-heatmap</name>
<description>生成股票板块周热度跟踪图。用于收集整理本周热门股票板块TOP10，生成交互式热力图HTML文件。当用户提到"板块热度"、"热门板块"、"板块热力图"、"周板块分析"或需要分析股票市场板块趋势时使用此技能。</description>
<location>project</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
