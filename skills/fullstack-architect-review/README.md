# fullstack-architect-review

以 Google 前后端工程架构师标准审查代码的 AI 技能。

## 覆盖范围

| 深度 | 技术栈 |
|------|--------|
| 深度覆盖 | React / Next.js / TypeScript / Node.js (Express/Fastify/NestJS/Hono) |
| 标准覆盖 | Vue / Nuxt / Python (Django/FastAPI) |
| 检测级别 | Angular / Svelte / Flask / Go (Gin/Chi/Fiber) |

## 文件结构

```
fullstack-architect-review/
├── SKILL.md              # 主工作流（审查流程 + 报告模板）
├── STANDARDS.md          # 编码规范核心要点（React/Vue/Node.js/Python）
├── REFERENCE.md          # 详细审查清单和代码示例
├── EXAMPLES.md           # 5个审查案例（含评分标准）
├── QUICK_REFERENCE.md    # 一页纸快速审查清单
├── README.md             # 本文件
├── .skillinfo            # 技能元数据
└── scripts/
    ├── detect-stack.sh   # 自动检测项目技术栈
    ├── run-review.sh     # 全量自动化审查
    ├── security-audit.sh # 依赖安全审计
    └── auto-fix.sh       # 自动修复（支持 --dry-run）
```

## 使用方式

### 通过 openskills CLI
```bash
npx openskills read fullstack-architect-review
```

### 自动化脚本
```bash
# SKILL_DIR = openskills 输出的 Base directory
bash "$SKILL_DIR/scripts/detect-stack.sh" /path/to/project
bash "$SKILL_DIR/scripts/run-review.sh" /path/to/project
bash "$SKILL_DIR/scripts/security-audit.sh" /path/to/project
bash "$SKILL_DIR/scripts/auto-fix.sh" /path/to/project          # 实际修复
bash "$SKILL_DIR/scripts/auto-fix.sh" /path/to/project --dry-run # 仅预览
```

## 审查维度

1. **架构设计** -- 分层、模块职责、可扩展性
2. **API设计** -- RESTful规范、响应格式、文档
3. **安全性** -- 认证授权、输入验证、密钥管理
4. **性能** -- 查询优化、缓存、渲染效率
5. **工程质量** -- 类型安全、测试、错误处理
6. **集成完整性** -- 前后端契约、状态同步

## 审查原则

**正确性 > 安全性 > 可维护性 > 性能 > 用户体验 > 简洁性**

基于标准:
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
