# 审查案例

真实场景的审查报告示例,展示审查标准和输出格式。

---

## 评分标准（Rubric）

所有案例使用统一的 6 维度评分体系,每个维度 0-10 分:

| 分数 | 等级 | 含义 |
|------|------|------|
| 9-10 | 优秀 | 生产就绪,可作为团队范例 |
| 7-8 | 良好 | 少量改进即可,不影响上线 |
| 5-6 | 一般 | 存在明显短板,需改进后部署 |
| 3-4 | 较差 | 多处严重问题,需重点修复 |
| 0-2 | 危险 | 存在安全漏洞或架构硬伤,禁止部署 |

**6 维度定义**:
- **架构设计**: 分层清晰度、模块职责、可扩展性、依赖方向
- **API设计**: RESTful规范、响应格式一致性、版本控制、文档
- **安全性**: 认证授权、输入验证、注入防护、密钥管理
- **性能**: 查询优化、缓存策略、前端渲染效率、资源加载
- **工程质量**: 类型安全、测试覆盖、代码规范、错误处理
- **集成完整性**: 前后端契约、状态同步、错误传播、部署流程

> 纯前端或纯后端项目中不适用的维度标记为 N/A，不参与总分计算。总分 = 适用维度得分之和 / 适用维度数。

---

## 案例1: React + TypeScript 前端项目审查

### 概述
审查一个React 18 + TypeScript + Zustand的电商前端项目,约50个组件。

### 严重问题 [P0]

#### 问题1: XSS漏洞 -- dangerouslySetInnerHTML未清理
**位置**: `src/components/ProductDescription.tsx:23`
**问题描述**: 直接将后端返回的富文本HTML插入DOM,未经过清理
**影响**: 攻击者可注入恶意脚本窃取用户Cookie

**当前代码**:
```tsx
const ProductDescription = ({ html }: { html: string }) => {
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
};
```

**修复方案**:
```tsx
import DOMPurify from 'dompurify';

const ProductDescription = ({ html }: { html: string }) => {
  const sanitizedHtml = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel'],
  });
  return <div dangerouslySetInnerHTML={{ __html: sanitizedHtml }} />;
};
```

#### 问题2: JWT存储在localStorage
**位置**: `src/utils/auth.ts:15`
**问题描述**: 将JWT Token存储在localStorage,可被XSS攻击窃取
**影响**: 一旦存在XSS漏洞,所有用户的认证Token都会被盗

**修复方案**: 改为httpOnly Cookie,由后端设置,前端请求自动携带。

### 重要建议 [P1]

#### 建议1: 商品列表缺少虚拟滚动
**位置**: `src/pages/ProductList.tsx`
**当前做法**: 一次渲染全部500+商品卡片
**建议做法**: 使用react-virtuoso实现虚拟滚动

```tsx
import { VirtuosoGrid } from 'react-virtuoso';

const ProductList = ({ products }: { products: Product[] }) => (
  <VirtuosoGrid
    totalCount={products.length}
    itemContent={(index) => <ProductCard product={products[index]} />}
    listClassName="product-grid"
  />
);
```

#### 建议2: 大量使用any类型
**位置**: 全局（搜索到47处`any`）
**建议做法**: 启用`noImplicitAny`,逐步替换为具体类型或`unknown`

### 优化建议 [P2]

#### 优化1: 图片未使用现代格式
**优化方案**: 使用`<picture>`标签提供WebP/AVIF备选
**预期收益**: 图片体积减少40-60%,LCP改善

### 优点总结
- 组件拆分粒度合理,职责清晰
- 使用Zustand管理状态,方案轻量合适
- TypeScript覆盖率85%
- 有完善的错误边界(ErrorBoundary)

### 总体评分
| 维度 | 分数 | 说明 |
|------|------|------|
| 架构设计 | 7/10 | 组件分层合理,状态管理方案恰当 |
| API设计 | N/A | 纯前端项目 |
| 安全性 | 4/10 | XSS漏洞 + JWT存储不当 |
| 性能 | 5/10 | 缺少虚拟滚动和图片优化 |
| 工程质量 | 6/10 | 有TS但any过多,缺少测试 |
| 集成完整性 | N/A | 纯前端项目 |

---

## 案例2: Node.js + Express 后端API审查

### 概述
审查一个Express + TypeScript + Prisma的RESTful API服务,提供用户管理和订单功能。

### 严重问题 [P0]

#### 问题1: SQL注入风险
**位置**: `src/controllers/searchController.ts:34`
**问题描述**: 搜索功能使用原始SQL拼接用户输入

**当前代码**:
```typescript
const search = async (req: Request, res: Response) => {
  const { keyword } = req.query;
  const results = await prisma.$queryRawUnsafe(
    `SELECT * FROM products WHERE name LIKE '%${keyword}%'`
  );
  res.json(results);
};
```

**修复方案**:
```typescript
const search = async (req: Request, res: Response) => {
  const keyword = z.string().max(100).parse(req.query.keyword);
  const results = await prisma.product.findMany({
    where: { name: { contains: keyword, mode: 'insensitive' } },
    select: { id: true, name: true, price: true },
    take: 50,
  });
  res.json({ code: 0, data: results });
};
```

#### 问题2: 缺少认证中间件
**位置**: `src/routes/orderRoutes.ts`
**问题描述**: 订单相关路由未添加认证中间件,任何人可访问
**影响**: 未授权用户可查看/修改所有订单

**修复方案**:
```typescript
const orderRouter = Router();
orderRouter.use(authMiddleware);
orderRouter.get('/', orderController.list);
orderRouter.get('/:id', orderController.getById);
orderRouter.post('/', orderController.create);
```

### 重要建议 [P1]

#### 建议1: N+1查询问题
**位置**: `src/services/orderService.ts:45`
**当前做法**: 查询订单列表后循环查询每个订单的商品

```typescript
// N+1
const orders = await prisma.order.findMany();
for (const order of orders) {
  order.items = await prisma.orderItem.findMany({
    where: { orderId: order.id },
  });
}
```

**建议做法**:
```typescript
const orders = await prisma.order.findMany({
  include: {
    items: { include: { product: { select: { id: true, name: true } } } },
  },
  take: pageSize,
  skip: (page - 1) * pageSize,
});
```

#### 建议2: 错误处理不统一
**位置**: 多处Controller
**当前做法**: 各Controller各自catch错误,格式不一致
**建议做法**: 统一使用全局错误处理中间件 + 自定义AppError类

### 优点总结
- 使用Prisma ORM,类型安全好
- 有合理的项目分层结构
- 日志使用winston,配置合理

### 总体评分
| 维度 | 分数 | 说明 |
|------|------|------|
| 架构设计 | 6/10 | 分层存在但Controller过厚 |
| API设计 | 5/10 | URL设计尚可,响应格式不统一 |
| 安全性 | 3/10 | SQL注入 + 缺少认证中间件 |
| 性能 | 5/10 | N+1查询,无缓存策略 |
| 工程质量 | 6/10 | 有TS和ORM,但错误处理混乱 |
| 集成完整性 | N/A | 纯后端项目 |

---

## 案例3: Next.js 全栈项目审查

### 概述
审查一个Next.js 14 App Router全栈项目,使用Server Components + Server Actions + Drizzle ORM。

### 严重问题 [P0]

#### 问题1: Server Action缺少授权检查
**位置**: `src/app/actions/updateProfile.ts`

```typescript
// 任何人都能修改任何用户的资料
'use server';
export async function updateProfile(userId: string, data: ProfileData) {
  await db.update(users).set(data).where(eq(users.id, userId));
}
```

**修复方案**:
```typescript
'use server';
import { auth } from '@/lib/auth';

export async function updateProfile(data: ProfileData) {
  const session = await auth();
  if (!session?.user?.id) throw new Error('Unauthorized');

  const validData = profileSchema.parse(data);
  await db.update(users).set(validData).where(eq(users.id, session.user.id));
  revalidatePath('/profile');
}
```

### 重要建议 [P1]

#### 建议1: Client/Server组件边界不清
**位置**: 多个页面组件
**问题**: 整个页面标记为`'use client'`,丧失了Server Component的优势

**建议做法**: 将交互部分提取为客户端子组件,页面保持为Server Component

```tsx
// src/app/products/page.tsx -- Server Component
export default async function ProductsPage() {
  const products = await getProducts();
  return (
    <div>
      <h1>商品列表</h1>
      <ProductFilters />
      <ProductGrid products={products} />
    </div>
  );
}
```

### 优点总结
- 使用App Router,架构现代
- Drizzle ORM类型安全
- 使用Zod进行数据验证
- Tailwind CSS样式方案统一

### 总体评分
| 维度 | 分数 | 说明 |
|------|------|------|
| 架构设计 | 7/10 | App Router使用合理 |
| API设计 | 7/10 | Server Actions替代REST,契约清晰 |
| 安全性 | 4/10 | Server Action缺少授权检查 |
| 性能 | 7/10 | Server Components减少客户端JS |
| 工程质量 | 7/10 | Zod + Drizzle类型安全链路完整 |
| 集成完整性 | 8/10 | 前后端同一代码库,类型共享天然 |

---

## 案例4: FastAPI + SQLAlchemy 后端API审查

### 概述
审查一个FastAPI + SQLAlchemy + Alembic的Python后端API服务,提供用户管理和支付功能。

### 严重问题 [P0]

#### 问题1: 密码使用MD5哈希
**位置**: `app/services/auth_service.py:28`
**问题描述**: 用户密码使用MD5哈希存储,极易被彩虹表攻破

**当前代码**:
```python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()
```

**修复方案**:
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

#### 问题2: 依赖注入缺失导致数据库会话泄漏
**位置**: `app/routers/user_router.py:15`
**问题描述**: 手动创建数据库会话但未在异常时关闭

**当前代码**:
```python
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user
```

**修复方案**:
```python
from fastapi import Depends
from app.database import get_db

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 重要建议 [P1]

#### 建议1: 缺少类型标注
**位置**: 多处service和repository函数
**当前做法**: 函数参数和返回值无类型标注
**建议做法**: 所有公共函数添加类型标注,配合mypy strict模式检查

#### 建议2: 未使用async ORM操作
**位置**: 全局
**当前做法**: 使用同步SQLAlchemy操作阻塞事件循环
**建议做法**: 使用 `sqlalchemy[asyncio]` + `asyncpg` 实现异步数据库访问

### 优点总结
- FastAPI自动生成OpenAPI文档
- 使用Alembic管理数据库迁移
- 项目分层结构（router/service/repository）

### 总体评分
| 维度 | 分数 | 说明 |
|------|------|------|
| 架构设计 | 6/10 | 有分层但依赖注入不完整 |
| API设计 | 7/10 | FastAPI自动文档,路由设计规范 |
| 安全性 | 3/10 | MD5密码哈希是致命缺陷 |
| 性能 | 5/10 | 同步ORM阻塞事件循环 |
| 工程质量 | 4/10 | 缺类型标注,无测试 |
| 集成完整性 | N/A | 纯后端项目 |

---

## 案例5: Vue 3 + Pinia 前端项目审查

### 概述
审查一个Vue 3 + TypeScript + Pinia的后台管理系统,约30个页面组件。

### 严重问题 [P0]

#### 问题1: v-html直接渲染用户输入
**位置**: `src/views/ArticleDetail.vue:45`
**问题描述**: 文章内容通过 `v-html` 直接渲染,未经XSS过滤

**当前代码**:
```vue
<template>
  <div v-html="article.content" />
</template>
```

**修复方案**:
```vue
<script setup lang="ts">
import DOMPurify from 'dompurify'
import { computed } from 'vue'

const props = defineProps<{ article: Article }>()
const safeContent = computed(() => DOMPurify.sanitize(props.article.content))
</script>

<template>
  <div v-html="safeContent" />
</template>
```

### 重要建议 [P1]

#### 建议1: 仍使用Options API
**位置**: 约60%的组件
**当前做法**: 使用 `data()` / `methods` / `computed` 的 Options API 风格
**建议做法**: 迁移至 `<script setup>` Composition API,更好的类型推断和代码组织

#### 建议2: Pinia Store 过于集中
**位置**: `src/stores/index.ts`（800+行）
**当前做法**: 所有状态放在一个巨大的store中
**建议做法**: 按业务域拆分（`useUserStore`, `useOrderStore`, `useSettingsStore`）

### 优化建议 [P2]

#### 优化1: 路由未使用懒加载
**优化方案**: 路由组件改用 `() => import('./views/XXX.vue')` 动态导入
**预期收益**: 首屏 JS 体积减少 40%+

### 优点总结
- 使用Pinia替代Vuex,方向正确
- Element Plus组件库使用规范
- 有基本的权限路由守卫

### 总体评分
| 维度 | 分数 | 说明 |
|------|------|------|
| 架构设计 | 5/10 | Options API混用,Store过于集中 |
| API设计 | N/A | 纯前端项目 |
| 安全性 | 4/10 | v-html XSS风险 |
| 性能 | 5/10 | 路由无懒加载,Bundle偏大 |
| 工程质量 | 5/10 | TS覆盖率低,Options API类型推断差 |
| 集成完整性 | N/A | 纯前端项目 |
