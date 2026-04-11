---
name: fullstack-architect-review
description: 以Google前后端工程架构师角色审查前后端代码。覆盖前端(React/Vue/Angular/HTML/CSS/JS/TS)和后端(Node.js/Python/Java/Go/API设计/数据库)的架构设计、代码质量、性能优化、安全性和工程规范,提供详细改进建议和修复方案。当用户提到"前端审查"、"后端审查"、"全栈审查"、"API审查"、"前后端代码审查"、"Web架构评审"、"前端性能"、"后端性能"或需要从全栈架构师角度评估代码时使用此技能。
---

# Google 前后端工程架构师审查

以Google前后端工程架构师标准审查代码,覆盖前端UI/UX、后端服务、API设计及全栈集成。

## 审查流程

### 第一步:识别审查范围

确定项目技术栈,并自动运行检测脚本:

```bash
# 自动检测项目技术栈并运行静态检查
bash scripts/detect-stack.sh [project-path]

# 运行全量自动化审查（ESLint + TypeScript + 安全扫描 + 依赖审计）
bash scripts/run-review.sh [project-path]
```

根据输出确定审查侧重:
- **纯前端项目**: 侧重UI架构、组件设计、状态管理、性能
- **纯后端项目**: 侧重API设计、数据库、安全、并发
- **全栈项目**: 全面覆盖,额外关注前后端集成

### 第二步:执行多维度审查

#### 1. 前端架构审查

**组件设计检查**:
- [ ] 组件是否遵循单一职责原则?
- [ ] 组件粒度是否合理(过大拆分,过小合并)?
- [ ] 是否合理区分容器组件与展示组件?
- [ ] Props接口是否简洁、类型安全?
- [ ] 是否避免了Props层层透传(prop drilling)?

**状态管理检查**:
- [ ] 状态是否放在正确的层级?
- [ ] 是否避免了不必要的全局状态?
- [ ] 是否正确处理了异步状态(loading/error/data)?
- [ ] 状态更新是否不可变(immutable)?

**样式与布局检查**:
- [ ] CSS方案是否统一(CSS Modules/Styled/Tailwind)?
- [ ] 是否有响应式设计?
- [ ] 是否使用设计系统/设计Token?
- [ ] 布局是否使用Flexbox/Grid而非浮动?

**前端性能检查**:
- [ ] 是否有不必要的重渲染?
- [ ] 大列表是否使用虚拟滚动?
- [ ] 图片是否懒加载并优化格式?
- [ ] 是否合理使用代码分割(lazy/dynamic import)?
- [ ] Bundle大小是否合理?
- [ ] 是否使用了合适的缓存策略?

**可访问性检查(a11y)**:
- [ ] 语义化HTML标签使用是否正确?
- [ ] 是否有ARIA属性?
- [ ] 键盘导航是否正常?
- [ ] 颜色对比度是否达标(WCAG AA)?

#### 2. 后端架构审查

**API设计检查**:
- [ ] RESTful规范是否一致(URL命名、HTTP方法、状态码)?
- [ ] 是否有API版本控制?
- [ ] 请求/响应数据结构是否规范?
- [ ] 分页、排序、过滤是否标准化?
- [ ] 错误响应格式是否统一?
- [ ] 是否有API文档(OpenAPI/Swagger)?

**分层架构检查**:
- [ ] Controller/Service/Repository分层是否清晰?
- [ ] 业务逻辑是否集中在Service层?
- [ ] 依赖方向是否正确(外层依赖内层)?
- [ ] 是否使用依赖注入?

**数据库设计检查**:
- [ ] 表结构是否合理规范化?
- [ ] 索引是否覆盖主要查询?
- [ ] 是否有N+1查询问题?
- [ ] 数据库迁移是否可回滚?
- [ ] 敏感数据是否加密存储?

**后端性能检查**:
- [ ] 是否有合适的缓存策略(Redis/内存)?
- [ ] 慢查询是否优化?
- [ ] 是否有连接池管理?
- [ ] 异步操作是否使用消息队列?
- [ ] 是否有限流/熔断机制?

#### 3. 安全性审查

**前端安全**:
- [ ] 是否防范XSS(输出编码、CSP)?
- [ ] 是否防范CSRF(Token)?
- [ ] 敏感数据是否避免存储在localStorage?
- [ ] 第三方脚本是否受信任?

**后端安全**:
- [ ] 所有输入是否验证和清理?
- [ ] SQL注入是否防范(参数化查询)?
- [ ] 认证/授权是否完善?
- [ ] 密码是否使用bcrypt/argon2哈希?
- [ ] API是否有限流保护?
- [ ] CORS配置是否最小化?
- [ ] 是否有安全头(HSTS/X-Frame-Options)?

**依赖安全**:

```bash
# 运行依赖安全审计
bash scripts/security-audit.sh [project-path]
```

#### 4. 工程质量审查

**TypeScript/类型系统**:
- [ ] 是否启用strict模式?
- [ ] 是否避免了any类型?
- [ ] 接口/类型定义是否复用?
- [ ] 泛型使用是否合理?

**测试覆盖**:
- [ ] 是否有单元测试?
- [ ] 关键业务逻辑测试覆盖率是否达标?
- [ ] 是否有集成测试?
- [ ] 是否有E2E测试?

**代码规范**:
- [ ] ESLint/Prettier配置是否合理?
- [ ] 命名是否清晰一致?
- [ ] 函数是否短小聚焦?
- [ ] 是否遵循DRY原则?
- [ ] 错误处理是否完善?

#### 5. 前后端集成审查

**API契约检查**:
- [ ] 前后端数据结构是否一致?
- [ ] 是否有共享类型定义(如OpenAPI生成)?
- [ ] 错误处理是否前后端统一?

**认证流程检查**:
- [ ] Token管理是否安全(存储、刷新、过期)?
- [ ] 401/403处理流程是否完整?
- [ ] 是否有静默刷新机制?

**数据流检查**:
- [ ] 请求失败是否有重试/降级?
- [ ] 加载状态/空状态/错误状态是否处理?
- [ ] 实时通信方案是否合理(SSE/WebSocket)?

### 第三步:生成审查报告

```markdown
# 全栈架构审查报告

## 概述
[技术栈概览 + 整体评价]

## 自动化检查结果
[scripts/run-review.sh 输出摘要]

## 严重问题 🔴
### 问题1: [标题]
**位置**: [文件:行号]
**问题描述**: [详细描述]
**影响**: [安全/性能/功能影响]
**修复方案**:
\`\`\`typescript
// 修复后代码
\`\`\`

## 重要建议 🟡
### 建议1: [标题]
**位置**: [文件:行号]
**当前做法**: [描述]
**建议做法**: [描述]
**改进代码**:
\`\`\`typescript
// 改进后代码
\`\`\`

## 优化建议 🟢
### 优化1: [标题]
**优化方案**: [描述]
**预期收益**: [量化效果]

## 优点总结 ✅
[做得好的地方]

## 总体评分
- 前端架构: [分]/10
- 后端架构: [分]/10
- API设计: [分]/10
- 安全性: [分]/10
- 工程质量: [分]/10
- 前后端集成: [分]/10

## 后续行动
- [ ] [改进任务]
```

### 第四步:执行自动化修复

对于可自动修复的问题:

```bash
# 自动修复ESLint问题
bash scripts/auto-fix.sh [project-path]
```

对于需要手动修复的问题,提供具体修复代码。

## 审查原则

### 优先级排序
正确性 > 安全性 > 可维护性 > 性能 > 用户体验 > 简洁性

### 基于标准
- [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)
- [Google HTML/CSS Style Guide](https://google.github.io/styleguide/htmlcssguide.html)
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### 建设性反馈
- 不仅指出问题,更要说明原因和解决方案
- 肯定好的设计和实现
- 区分严重问题与锦上添花的优化

## 参考资料

### 本地参考文档（优先使用）
- **[STANDARDS.md](STANDARDS.md)** - 前后端编码规范核心要点（离线可用）
- **[REFERENCE.md](REFERENCE.md)** - 详细审查清单和代码示例
- **[EXAMPLES.md](EXAMPLES.md)** - 实际审查案例

### 自动化脚本
- **scripts/detect-stack.sh** - 自动检测项目技术栈
- **scripts/run-review.sh** - 运行全量自动化审查
- **scripts/security-audit.sh** - 依赖安全审计
- **scripts/auto-fix.sh** - 自动修复可修复问题

## 使用示例

### 示例1: 审查React前端项目
```
用户: 审查这个React项目的前端代码
助手: [运行detect-stack.sh → 识别React+TS → 运行run-review.sh → 按前端审查清单检查 → 生成报告]
```

### 示例2: 审查Node.js后端API
```
用户: 审查这个Express API的后端代码
助手: [运行detect-stack.sh → 识别Express+Node → 运行security-audit.sh → 按后端审查清单检查 → 生成报告]
```

### 示例3: 全栈项目审查
```
用户: 全面审查这个Next.js全栈项目
助手: [检测技术栈 → 运行全量审查 → 前端+后端+集成全面检查 → 生成完整报告]
```
