# 审查案例

真实场景的审查报告示例,展示审查标准和输出格式。

---

## 案例1: React + TypeScript 前端项目审查

### 概述
审查一个React 18 + TypeScript + Zustand的电商前端项目,约50个组件。

### 严重问题 🔴

#### 问题1: XSS漏洞 — dangerouslySetInnerHTML未清理
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

### 重要建议 🟡

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

### 优化建议 🟢

#### 优化1: 图片未使用现代格式
**优化方案**: 使用`<picture>`标签提供WebP/AVIF备选
**预期收益**: 图片体积减少40-60%,LCP改善

### 优点总结 ✅
- 组件拆分粒度合理,职责清晰
- 使用Zustand管理状态,方案轻量合适
- TypeScript覆盖率85%
- 有完善的错误边界(ErrorBoundary)

### 总体评分
- 前端架构: 7/10
- 安全性: 4/10
- 工程质量: 6/10
- 性能: 5/10

---

## 案例2: Node.js + Express 后端API审查

### 概述
审查一个Express + TypeScript + Prisma的RESTful API服务,提供用户管理和订单功能。

### 严重问题 🔴

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

### 重要建议 🟡

#### 建议1: N+1查询问题
**位置**: `src/services/orderService.ts:45`
**当前做法**: 查询订单列表后循环查询每个订单的商品

```typescript
// ❌ N+1
const orders = await prisma.order.findMany();
for (const order of orders) {
  order.items = await prisma.orderItem.findMany({
    where: { orderId: order.id },
  });
}
```

**建议做法**:
```typescript
// ✅ 使用include一次查询
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

### 优点总结 ✅
- 使用Prisma ORM,类型安全好
- 有合理的项目分层结构
- 日志使用winston,配置合理

### 总体评分
- 后端架构: 6/10
- API设计: 5/10
- 安全性: 3/10
- 数据库: 5/10
- 工程质量: 6/10

---

## 案例3: Next.js 全栈项目审查

### 概述
审查一个Next.js 14 App Router全栈项目,使用Server Components + Server Actions + Drizzle ORM。

### 严重问题 🔴

#### 问题1: Server Action缺少授权检查
**位置**: `src/app/actions/updateProfile.ts`

```typescript
// ❌ 任何人都能修改任何用户的资料
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

### 重要建议 🟡

#### 建议1: Client/Server组件边界不清
**位置**: 多个页面组件
**问题**: 整个页面标记为`'use client'`,丧失了Server Component的优势

**建议做法**: 将交互部分提取为客户端子组件,页面保持为Server Component

```tsx
// src/app/products/page.tsx — Server Component
export default async function ProductsPage() {
  const products = await getProducts(); // 服务端直接查DB
  return (
    <div>
      <h1>商品列表</h1>
      <ProductFilters />      {/* Client Component: 用户交互 */}
      <ProductGrid products={products} /> {/* Server Component: 纯展示 */}
    </div>
  );
}
```

### 优点总结 ✅
- 使用App Router,架构现代
- Drizzle ORM类型安全
- 使用Zod进行数据验证
- Tailwind CSS样式方案统一

### 总体评分
- 前端架构: 7/10
- 后端架构: 6/10
- API设计: 7/10
- 安全性: 4/10
- 工程质量: 7/10
- 前后端集成: 8/10
