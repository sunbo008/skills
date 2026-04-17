# Web 后端领域指南

Python Web后端架构设计与审查的领域专项指南。

## 推荐技术栈

| 场景 | 首选 | 备选 |
|------|------|------|
| API服务 | FastAPI | Litestar, Flask |
| 全栈Web | Django | - |
| ORM | SQLAlchemy 2.0 (async) | SQLModel, Tortoise |
| 数据库迁移 | Alembic | Django Migrations |
| 验证/序列化 | Pydantic v2 | msgspec |
| HTTP客户端 | httpx | aiohttp |
| 任务队列 | Celery + Redis | arq, Dramatiq |
| 缓存 | Redis (aioredis) | 内存LRU |

## FastAPI 项目结构

```
src/myapp/
├── api/
│   ├── v1/
│   │   ├── routes/
│   │   │   ├── users.py       # 路由定义
│   │   │   └── orders.py
│   │   ├── deps.py            # 依赖注入
│   │   └── router.py          # v1路由汇总
│   └── middleware.py           # 中间件
├── core/
│   ├── config.py              # Settings (pydantic-settings)
│   ├── exceptions.py          # 自定义异常
│   ├── security.py            # JWT/认证
│   └── database.py            # DB引擎/会话
├── models/
│   ├── domain.py              # 领域模型 (dataclass/Pydantic)
│   └── orm.py                 # ORM模型 (SQLAlchemy)
├── schemas/
│   ├── requests.py            # 请求schema
│   └── responses.py           # 响应schema
├── services/                  # 业务逻辑
├── repositories/              # 数据访问
└── main.py                    # 应用入口
```

## 关键模式

### 路由层 — 薄而清晰

```python
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/users", status_code=201)
async def create_user(
    data: CreateUserRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """路由只做: 接收请求 → 调用service → 返回响应"""
    return await service.create(data)
```

### Service层 — 业务逻辑核心

```python
class UserService:
    def __init__(self, repo: UserRepository, notifier: Notifier) -> None:
        self._repo = repo
        self._notifier = notifier

    async def create(self, data: CreateUserRequest) -> UserResponse:
        if await self._repo.exists_by_email(data.email):
            raise ConflictError(f"Email {data.email} already registered")
        user = User(name=data.name, email=data.email, password_hash=hash_password(data.password))
        saved = await self._repo.save(user)
        await self._notifier.send_welcome(saved.email)
        return UserResponse.model_validate(saved)
```

### 依赖注入

```python
# api/v1/deps.py
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

def get_user_service(
    session: AsyncSession = Depends(get_db_session),
) -> UserService:
    repo = SqlUserRepository(session)
    notifier = EmailNotifier(settings.smtp_url)
    return UserService(repo=repo, notifier=notifier)
```

### 统一异常处理

```python
# api/middleware.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    status_map = {
        "VALIDATION_ERROR": 422,
        "NOT_FOUND": 404,
        "CONFLICT": 409,
        "UNAUTHORIZED": 401,
        "FORBIDDEN": 403,
    }
    return JSONResponse(
        status_code=status_map.get(exc.code, 500),
        content={"code": exc.code, "message": exc.message, "details": exc.details},
    )
```

### 安全检查要点

- JWT存httpOnly Cookie，不存localStorage
- CORS限制具体域名，不用 `allow_origins=["*"]`
- 限流: `slowapi` 或 nginx层
- 输入验证全部用Pydantic，禁止信任原始request body
- 密码: `bcrypt` 或 `argon2-cffi`，cost factor ≥ 12
- SQL: 只用ORM或参数化查询
- 安全头: HSTS, X-Content-Type-Options, X-Frame-Options

## 性能要点

- 使用 `async def` 路由 + async ORM
- 大查询使用游标分页（`keyset pagination`）而非 OFFSET
- 热数据缓存到Redis，设TTL
- 连接池: SQLAlchemy `pool_size` + `max_overflow`
- 后台任务: 用 Celery/arq 而非 `BackgroundTasks`（需可靠性时）
