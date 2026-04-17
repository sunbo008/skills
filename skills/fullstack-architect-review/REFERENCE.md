# 详细审查清单与代码示例

审查时逐项检查的详细清单,附带正确/错误代码对比。

---

## 一、前端详细审查

### 1.1 React组件反模式

**反模式: 在渲染中创建对象/函数（仅当子组件使用 React.memo 时有意义）**
```tsx
// ❌ 每次渲染创建新对象引用,若 Child 使用 React.memo 则会导致无谓重渲染
const Parent = () => {
  return <Child style={{ color: 'red' }} onClick={() => doSomething()} />;
};

// ✅ 静态值提取到组件外; 回调仅在子组件使用 React.memo 优化时才需要 useCallback
const style = { color: 'red' };
const Parent = () => {
  const handleClick = useCallback(() => doSomething(), []);
  return <MemoizedChild style={style} onClick={handleClick} />;
};

// 注意: 如果 Child 未使用 React.memo, useCallback 不会带来性能收益
```

**反模式: useEffect中的状态同步**
```tsx
// ❌ 用useEffect同步派生状态
const [items, setItems] = useState([]);
const [filteredItems, setFilteredItems] = useState([]);
useEffect(() => {
  setFilteredItems(items.filter(i => i.active));
}, [items]);

// ✅ 直接计算派生值
const [items, setItems] = useState([]);
const filteredItems = useMemo(
  () => items.filter(i => i.active),
  [items]
);
```

**反模式: 过大组件**
```tsx
// ❌ 一个组件500+行,混合多种职责
const UserDashboard = () => {
  // 30行认证逻辑
  // 50行数据获取
  // 40行表单处理
  // 300行JSX混合图表、表格、表单
};

// ✅ 按职责拆分
const UserDashboard = () => (
  <DashboardLayout>
    <UserStats />
    <RecentOrders />
    <ProfileForm />
  </DashboardLayout>
);
```

### 1.2 状态管理审查清单

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| 全局状态中存放可计算值 | 🟡 | 应改为派生状态 |
| 未序列化数据存入Redux/Zustand | 🟡 | 如Date对象、类实例 |
| 组件内部状态泄露到全局 | 🔴 | 仅本组件使用的状态不应提升 |
| 异步状态未处理loading/error | 🔴 | 用户体验和稳定性问题 |
| 乐观更新未处理回滚 | 🟡 | 失败时需要恢复UI状态 |
| 缺少数据缓存/重验证策略 | 🟡 | 考虑使用React Query/SWR |

### 1.3 性能审查清单

| 检查项 | 检测方法 | 优化方案 |
|--------|----------|----------|
| 不必要的重渲染 | React DevTools Profiler | React.memo + 稳定引用 |
| Bundle过大 | webpack-bundle-analyzer | 代码分割 + tree-shaking |
| 首屏加载慢 | Lighthouse FCP/LCP | SSR/SSG + 关键资源预加载 |
| 图片未优化 | Lighthouse | WebP/AVIF + 响应式图片 + lazy |
| 未使用的代码 | Coverage工具 | 移除或动态导入 |
| 字体闪烁(FOUT) | 视觉检查 | font-display: swap + preload |
| 长任务阻塞主线程 | Performance面板 | Web Worker或requestIdleCallback |
| 内存泄漏 | Memory面板 | 清理事件监听/定时器/订阅 |

### 1.4 可访问性审查

```html
<!-- ❌ 常见可访问性问题 -->
<div onclick="handleClick()">点击我</div>
<img src="logo.png">
<input placeholder="请输入邮箱">

<!-- ✅ 正确做法 -->
<button type="button" onClick={handleClick}>点击我</button>
<img src="logo.png" alt="公司Logo">
<label htmlFor="email">邮箱</label>
<input id="email" type="email" placeholder="请输入邮箱" aria-describedby="email-hint">
<span id="email-hint">我们不会分享您的邮箱</span>
```

---

## 二、后端详细审查

### 2.1 API设计反模式

**反模式: 动词URL**
```
# ❌
GET  /api/getUsers
POST /api/createUser
POST /api/deleteUser/123

# ✅
GET    /api/v1/users
POST   /api/v1/users
DELETE /api/v1/users/123
```

**反模式: 不一致的响应结构**
```json
// ❌ 不同接口返回格式不一致
// GET /users → { "users": [...] }
// GET /orders → { "data": [...], "count": 10 }
// GET /products → [...]

// ✅ 统一响应封装
// GET /users → { "code": 0, "data": { "items": [...], "total": 50 } }
// GET /orders → { "code": 0, "data": { "items": [...], "total": 10 } }
```

**反模式: 缺少输入验证**
```typescript
// ❌ 直接信任请求数据
app.post('/users', async (req, res) => {
  const user = await db.users.create(req.body);
  res.json(user);
});

// ✅ 验证 + 清理输入
const createUserSchema = z.object({
  name: z.string().min(1).max(100).trim(),
  email: z.string().email().toLowerCase(),
  age: z.number().int().min(0).max(150).optional(),
});

app.post('/users', async (req, res) => {
  const data = createUserSchema.parse(req.body);
  const user = await userService.create(data);
  res.status(201).json({ code: 0, data: user });
});
```

### 2.2 数据库审查清单

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| N+1查询 | 🔴 | 使用JOIN/eager loading/DataLoader |
| 缺少索引的WHERE字段 | 🔴 | 分析慢查询日志,添加索引 |
| SELECT * | 🟡 | 只查所需字段 |
| 大表无分页 | 🔴 | 强制分页,限制最大pageSize |
| 事务范围过大 | 🟡 | 缩小事务范围,减少锁持有时间 |
| 硬删除 | 🟡 | 考虑软删除(deleted_at) |
| 缺少唯一约束 | 🔴 | 业务唯一字段需加UNIQUE |
| 明文存储敏感数据 | 🔴 | 密码hash,PII加密 |

**N+1查询示例**:
```typescript
// ❌ N+1: 查N个用户,每个用户再查订单
const users = await User.findAll();
for (const user of users) {
  user.orders = await Order.findAll({ where: { userId: user.id } });
}

// ✅ 使用JOIN或include
const users = await User.findAll({
  include: [{ model: Order }],
});

// ✅ 或使用DataLoader批量加载
const orderLoader = new DataLoader(async (userIds) => {
  const orders = await Order.findAll({ where: { userId: userIds } });
  return userIds.map(id => orders.filter(o => o.userId === id));
});
```

### 2.3 安全审查清单

| 检查项 | 严重度 | 检测方法 |
|--------|--------|----------|
| SQL注入 | 🔴 | 搜索字符串拼接SQL |
| XSS | 🔴 | 搜索innerHTML/dangerouslySetInnerHTML |
| CSRF | 🔴 | 检查表单提交是否有Token |
| 不安全的JWT存储 | 🔴 | 检查localStorage中是否存Token |
| 未配置CORS | 🟡 | 检查CORS中间件配置 |
| 缺少限流 | 🟡 | 检查是否有rate-limit中间件 |
| 密码明文/弱hash | 🔴 | 搜索密码处理逻辑 |
| 硬编码密钥 | 🔴 | 搜索key/secret/password字符串 |
| 日志泄露敏感信息 | 🟡 | 检查日志是否包含密码/Token |
| 未验证文件上传 | 🔴 | 检查文件类型/大小验证 |

### 2.4 错误处理审查

```typescript
// ❌ 吞掉错误
try {
  await riskyOperation();
} catch (e) {
  // nothing
}

// ❌ 暴露内部信息
app.use((err, req, res, next) => {
  res.status(500).json({ error: err.stack });
});

// ✅ 结构化错误处理
class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: unknown
  ) {
    super(message);
  }
}

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      code: err.code,
      message: err.message,
      details: err.details,
    });
  }
  logger.error('Unhandled error', { error: err, requestId: req.id });
  res.status(500).json({
    code: 'INTERNAL_ERROR',
    message: 'An unexpected error occurred',
  });
});
```

---

## 三、全栈集成审查

### 3.1 API客户端封装

以下示例使用 fetch 封装,也可替换为 axios/ky/ofetch 等库:

```typescript
// ✅ 统一API客户端 (框架无关)
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit,
  _retried = false,
): Promise<T> {
  const { headers: customHeaders, ...restOptions } = options ?? {};
  const defaultHeaders: Record<string, string> =
    restOptions.body instanceof FormData
      ? {}
      : { 'Content-Type': 'application/json' };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    credentials: 'include',
    ...restOptions,
    headers: { ...defaultHeaders, ...(customHeaders as Record<string, string>) },
  });

  if (response.status === 401 && !_retried) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      return apiFetch<T>(endpoint, options, true);
    }
    redirectToLogin();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    throw await normalizeError(response);
  }

  return response.json();
}

// ✅ Token 刷新需防止并发竞态
let refreshPromise: Promise<boolean> | null = null;

async function tryRefreshToken(): Promise<boolean> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });
      return res.ok;
    } catch {
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}
```

### 3.2 类型共享

```typescript
// ✅ 共享类型定义(monorepo中)
// packages/shared/types/user.ts
export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

export interface CreateUserRequest {
  name: string;
  email: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}
```

### 3.3 环境变量审查

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| API密钥在前端代码中 | 🔴 | 必须放后端,通过API代理 |
| .env文件提交到git | 🔴 | 加入.gitignore |
| 生产配置硬编码 | 🟡 | 使用环境变量 |
| 前端变量缺少前缀 | 🟡 | NEXT_PUBLIC_/VITE_/REACT_APP_ |
| 缺少.env.example | 🟡 | 团队需要知道需配置哪些变量 |

---

## 四、Vue详细审查

### 4.1 Vue组件反模式

**反模式: Options API + 无类型标注**
```vue
<!-- ❌ Options API 类型推断差,逻辑分散 -->
<script>
export default {
  data() {
    return { count: 0, users: [] }
  },
  methods: {
    increment() { this.count++ },
    async fetchUsers() { this.users = await api.getUsers() }
  },
  mounted() { this.fetchUsers() }
}
</script>

<!-- ✅ Composition API + TypeScript -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'

const count = ref(0)
const users = ref<User[]>([])

const increment = () => count.value++
const fetchUsers = async () => { users.value = await api.getUsers() }

onMounted(fetchUsers)
</script>
```

**反模式: 模板中复杂表达式**
```vue
<!-- ❌ 模板中放复杂逻辑 -->
<template>
  <span>{{ items.filter(i => i.active).reduce((s, i) => s + i.price, 0).toFixed(2) }}</span>
</template>

<!-- ✅ 提取为 computed -->
<script setup lang="ts">
import { computed, ref } from 'vue'

interface Item { active: boolean; price: number }
const items = ref<Item[]>([])

const activeTotal = computed(() =>
  items.value.filter(i => i.active).reduce((s, i) => s + i.price, 0).toFixed(2)
)
</script>
<template>
  <span>{{ activeTotal }}</span>
</template>
```

### 4.2 Vue审查清单

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| 使用 Options API | 🟡 | 应迁移到 Composition API |
| Props 使用运行时声明 | 🟡 | 应使用 `defineProps<T>()` 类型声明 |
| v-html 未经 XSS 过滤 | 🔴 | 必须使用 DOMPurify |
| 未使用 Pinia 的 storeToRefs | 🟡 | 直接解构 store 会丢失响应性 |
| 路由未使用懒加载 | 🟡 | 应使用 `() => import('./XXX.vue')` |
| 组件未使用 `<script setup>` | 🟡 | `<script setup>` 编译更优,类型推断更好 |

---

## 五、Python后端详细审查

### 5.1 FastAPI反模式

**反模式: 手动管理数据库会话**
```python
# ❌ 异常时会话未关闭,连接泄漏
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    return user

# ✅ 使用依赖注入管理生命周期
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**反模式: 同步操作阻塞事件循环**
```python
# ❌ FastAPI使用async但数据库操作是同步的
@router.get("/users")
async def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# ✅ 使用异步ORM或线程池
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### 5.2 Django审查清单

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| N+1查询 | 🔴 | 使用 select_related / prefetch_related |
| Fat Model | 🟡 | 复杂业务逻辑应抽到 Service 层 |
| 未使用 F() 表达式 | 🟡 | 计数器更新应用 F() 避免竞态 |
| SECRET_KEY 硬编码 | 🔴 | 必须使用环境变量 |
| DEBUG=True 在生产 | 🔴 | 生产环境必须关闭 |
| 未配置 ALLOWED_HOSTS | 🔴 | 生产环境必须限定域名 |
| 缺少 CSRF 中间件 | 🔴 | CsrfViewMiddleware 不得移除 |

### 5.3 Python安全审查

| 检查项 | 严重度 | 检测方法 |
|--------|--------|----------|
| MD5/SHA1 密码哈希 | 🔴 | 搜索 hashlib.md5/sha1 |
| eval()/exec() | 🔴 | 搜索 eval / exec 调用 |
| pickle 反序列化不可信数据 | 🔴 | 搜索 pickle.loads |
| subprocess shell=True | 🔴 | 搜索 subprocess + shell=True |
| SQL 字符串拼接 | 🔴 | 搜索 f-string/format 拼接 SQL |
| 缺少类型标注 | 🟡 | 运行 mypy --strict |
| 未使用 bandit 扫描 | 🟡 | bandit -r . |
