# 前后端编码规范核心要点

基于Google Style Guide和业界最佳实践的离线参考文档。

---

## 一、前端规范

### 1. TypeScript/JavaScript

**命名规范**:
| 类型 | 规范 | 示例 |
|------|------|------|
| 类/接口/类型/枚举 | PascalCase | `UserProfile`, `ApiResponse` |
| 函数/方法 | camelCase | `getUserById`, `handleClick` |
| 变量/参数 | camelCase | `userName`, `isLoading` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| 文件(组件) | PascalCase | `UserCard.tsx`, `AuthProvider.tsx` |
| 文件(工具/hooks) | camelCase | `useAuth.ts`, `formatDate.ts` |
| CSS类 | kebab-case | `user-card`, `nav-item--active` |

**TypeScript严格模式必须项**:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

**禁止的做法**:
- `any` 类型（用 `unknown` + 类型守卫替代）
- `@ts-ignore`（用 `@ts-expect-error` + 注释原因替代）
- 非空断言 `!`（用可选链 `?.` + 空值合并 `??` 替代）
- `var` 声明（用 `const` 优先，必要时 `let`）
- `==` 松散比较（用 `===` 严格比较）

**推荐模式**:
```typescript
// ✅ 使用const断言缩窄类型
const ROUTES = {
  HOME: '/',
  PROFILE: '/profile',
} as const;

// ✅ 使用discriminated union处理状态
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

// ✅ 使用泛型约束确保类型安全
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

### 2. React规范

**组件设计原则**:
```typescript
// ✅ 函数组件 + 直接类型标注（不推荐 React.FC）
interface UserCardProps {
  user: User;
  onEdit?: (id: string) => void;
}

const UserCard = ({ user, onEdit }: UserCardProps) => {
  // 组件逻辑
};

// ✅ 自定义Hook封装复用逻辑
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debouncedValue;
}
```

> **为何不推荐 `React.FC`**: 隐式包含 `children` 属性、与泛型组件兼容性差、增加不必要的类型噪音。直接标注 Props 类型更简洁、更灵活。

**Hooks使用规范**:
- `useMemo` / `useCallback`: 仅在子组件通过 `React.memo` 优化或依赖引用稳定性时使用,不要为每个回调都包裹 useCallback
- `useEffect` 依赖数组: 必须完整,使用eslint-plugin-react-hooks强制检查
- 避免在useEffect中更新触发自身重执行的状态
- 复杂状态逻辑用 `useReducer` 替代多个 `useState`

**性能优化要求**:
- 列表渲染必须有稳定 `key`（禁止用index作为动态列表key）
- 超过100项的列表使用虚拟滚动（react-window/react-virtuoso）
- 路由级别使用 `React.lazy` + `Suspense`
- 图片使用 `loading="lazy"` 并提供宽高避免CLS

### 3. CSS/样式规范

**推荐方案优先级**: CSS Modules > Tailwind CSS > CSS-in-JS > 全局CSS

**BEM命名（全局CSS场景）**:
```css
/* Block */
.user-card { }
/* Element */
.user-card__avatar { }
/* Modifier */
.user-card--highlighted { }
```

**关键规则**:
- 禁止使用 `!important`（组件库覆盖除外）
- 禁止使用ID选择器设置样式
- 使用CSS变量管理设计Token
- 移动优先的响应式设计（min-width媒体查询）
- 字体大小和间距使用 `rem`,边框/阴影/细线等视觉细节可用 `px`

### 4. HTML可访问性

**必须项**:
- 所有 `<img>` 必须有 `alt` 属性
- 表单控件必须有关联 `<label>`
- 交互元素必须可键盘操作
- 使用语义化标签: `<nav>`, `<main>`, `<article>`, `<section>`
- 模态框必须管理焦点陷阱
- ARIA属性仅在语义标签无法满足时使用

---

## 二、后端规范

### 1. RESTful API设计

**URL设计**:
```
GET    /api/v1/users          # 列表
GET    /api/v1/users/:id      # 详情
POST   /api/v1/users          # 创建
PUT    /api/v1/users/:id      # 全量更新
PATCH  /api/v1/users/:id      # 部分更新
DELETE /api/v1/users/:id      # 删除

# 子资源
GET    /api/v1/users/:id/orders
# 操作(非CRUD)
POST   /api/v1/users/:id/activate
```

**命名规则**: URL用kebab-case复数名词,查询参数用camelCase

**HTTP状态码使用**:
| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | OK | GET/PUT/PATCH成功 |
| 201 | Created | POST创建成功 |
| 204 | No Content | DELETE成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突 |
| 422 | Unprocessable | 业务逻辑验证失败 |
| 429 | Too Many Requests | 限流 |
| 500 | Internal Error | 服务端异常 |

**统一响应格式**:
```json
// 成功
{
  "code": 0,
  "data": { },
  "message": "success"
}

// 分页
{
  "code": 0,
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}

// 错误
{
  "code": 40001,
  "message": "Validation failed",
  "details": [
    { "field": "email", "message": "Invalid email format" }
  ]
}
```

### 2. 后端架构分层

```
src/
├── controllers/    # 处理HTTP请求/响应,参数校验,调用service
├── services/       # 核心业务逻辑,事务管理
├── repositories/   # 数据访问层,ORM操作
├── models/         # 数据模型定义
├── middlewares/     # 认证、日志、错误处理等中间件
├── validators/     # 请求参数验证schema
├── utils/          # 纯工具函数
├── config/         # 配置管理
└── types/          # 共享类型定义
```

**分层原则**:
- Controller层: 仅做请求解析、参数校验、调用Service、格式化响应
- Service层: 所有业务逻辑在此,可注入Repository,管理事务
- Repository层: 仅数据库操作,不含业务逻辑
- 禁止跨层调用(Controller直接调Repository)

### 3. 数据库规范

**SQL规范**:
- 表名: snake_case 复数 (`user_profiles`)
- 字段名: snake_case (`created_at`, `is_active`)
- 主键: `id` (BIGINT自增或UUID)
- 必须有 `created_at`, `updated_at` 时间戳
- 软删除用 `deleted_at` 字段
- 外键字段: `{关联表单数}_id` (`user_id`)

**查询优化**:
- WHERE条件字段必须有索引
- 复合索引遵循最左前缀原则
- 禁止 `SELECT *`，只查询需要的字段
- 分页使用游标而非OFFSET（大数据量时）
- 注意N+1问题,使用JOIN或批量查询

### 4. 安全规范

**认证/授权**:
- JWT存储在httpOnly + secure + sameSite Cookie中
- Access Token短期(15分钟),Refresh Token长期(7天)
- 密码使用bcrypt(cost>=12)或argon2id
- 敏感操作需二次验证

**输入验证**:
- 所有输入必须在服务端验证（不信任客户端）
- 使用白名单验证而非黑名单
- 使用参数化查询防SQL注入
- 使用DOMPurify等库防XSS
- 文件上传验证类型、大小、内容

**HTTP安全头**:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-XSS-Protection: 0  # 已弃用,设为0禁用浏览器XSS过滤器(该过滤器本身存在安全漏洞)
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 三、全栈集成规范

### API契约管理
- 使用OpenAPI/Swagger定义API契约
- 前后端共享类型定义（通过代码生成工具）
- API变更需向后兼容,重大变更升版本

### 错误处理一致性
- 后端返回结构化错误,前端统一拦截处理
- 网络错误、业务错误、系统错误分别处理
- 用户可见错误信息需国际化

### 环境与配置
- 敏感配置使用环境变量,禁止硬编码
- 前端环境变量使用框架约定前缀(NEXT_PUBLIC_/VITE_)
- 不同环境(dev/staging/prod)配置隔离

---

## 四、Vue规范

### 1. Composition API（Vue 3）

**组件设计原则**:
```vue
<script setup lang="ts">
// ✅ 使用 <script setup> + TypeScript
interface Props {
  user: User
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
})

const emit = defineEmits<{
  update: [user: User]
  delete: [id: string]
}>()
</script>
```

**Composables（组合式函数）规范**:
```typescript
import { ref, readonly, watch, type Ref } from 'vue'

// ✅ 以 use 前缀命名,返回响应式引用
export function useUserList(page: Ref<number>) {
  const users = ref<User[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function fetch() {
    loading.value = true
    error.value = null
    try {
      users.value = await api.getUsers(page.value)
    } catch (e) {
      error.value = e as Error
    } finally {
      loading.value = false
    }
  }

  watch(page, fetch, { immediate: true })

  return { users: readonly(users), loading: readonly(loading), error: readonly(error) }
}
```

**关键规则**:
- 优先使用 Composition API（`<script setup>`），避免 Options API
- Props 使用 TypeScript 类型声明（`defineProps<T>()`），不用运行时声明
- 模板中避免复杂表达式，提取为 `computed`
- 状态管理使用 Pinia（不再推荐 Vuex）

### 2. Vue命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `UserCard.vue` |
| 组件注册 | PascalCase | `<UserCard />` |
| Composables | camelCase + use前缀 | `useAuth.ts` |
| Emits | camelCase | `@update-user` (模板) / `updateUser` (script) |
| Props | camelCase | `userName` (script) / `user-name` (模板) |

---

## 五、Python后端规范

### 1. 代码风格

遵循 [PEP 8](https://peps.python.org/pep-0008/) + [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)。

**命名规范**:
| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/包 | snake_case | `user_service.py` |
| 类 | PascalCase | `UserRepository` |
| 函数/方法 | snake_case | `get_user_by_id` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 私有成员 | 前缀 `_` | `_internal_cache` |

**类型标注（必须，使用 Python 3.10+ 现代语法）**:
```python
# ✅ 所有公共函数必须有类型标注 (Python 3.10+ 使用 X | None 代替 Optional[X])
def get_user(user_id: int) -> User | None:
    ...

# ✅ Pydantic模型用于请求/响应验证
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int | None = Field(default=None, ge=0, le=150)
```

### 2. FastAPI规范

```python
# ✅ 路由分层: router -> service -> repository
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user
```

**关键规则**:
- 使用 `async def` 处理 I/O 操作
- 依赖注入通过 `Depends()` 实现
- 请求验证使用 Pydantic 模型
- 异常使用 `HTTPException` 或自定义异常处理器
- 使用 `Alembic` 管理数据库迁移

### 3. Django规范

```python
# ✅ 视图使用类视图或DRF ViewSet
from rest_framework import viewsets, permissions

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().select_related('profile')
```

**关键规则**:
- 使用 `select_related` / `prefetch_related` 避免 N+1 查询
- Model 中不放业务逻辑（保持 thin model 或使用 Service 层）
- 使用 Django ORM 的 `F()` / `Q()` 表达式避免竞态条件
- 敏感设置通过 `django-environ` 或环境变量管理

### 4. Python工具链

- **Linter**: Ruff（替代 flake8 + isort + pyupgrade）
- **类型检查**: mypy（strict 模式）
- **安全扫描**: bandit
- **测试**: pytest + pytest-cov
- **格式化**: Ruff format（替代 black）
