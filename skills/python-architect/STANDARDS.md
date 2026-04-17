# Python 编码规范核心要点

基于 Google Python Style Guide + PEP 8 + 业界最佳实践。离线可用。

---

## 1. 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/包 | snake_case，短小 | `user_service.py`, `utils/` |
| 类 | PascalCase | `UserService`, `HttpClient` |
| 函数/方法 | snake_case | `get_user_by_id`, `validate_input` |
| 变量 | snake_case | `user_name`, `is_active` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| 私有成员 | 前缀 `_` | `_cache`, `_validate()` |
| 类型变量 | PascalCase 或 单字母 | `T`, `ItemType` |
| Protocol | 描述行为 + 后缀可选 | `Serializable`, `Repository` |

**命名原则**:
- 名字要自解释：`get_active_users()` 而非 `get_u()`
- 布尔值用 `is_/has_/can_/should_` 前缀
- 避免缩写（除非是领域通用缩写如 `url`, `http`, `db`）
- 避免单字母变量（循环计数器 `i, j, k` 和 lambda 除外）

## 2. 类型标注

**必须标注的场景**:
- 所有公共函数的参数和返回值
- 类属性
- 复杂数据结构

```python
# ✅ 完整的类型标注
from collections.abc import Sequence
from typing import TypeAlias

UserId: TypeAlias = int

def get_users(
    ids: Sequence[UserId],
    *,
    active_only: bool = True,
    limit: int | None = None,
) -> list[User]:
    ...

# ✅ 使用 Protocol 定义接口
from typing import Protocol, runtime_checkable

@runtime_checkable
class Repository(Protocol):
    def get(self, id: int) -> Model | None: ...
    def save(self, entity: Model) -> Model: ...
    def delete(self, id: int) -> None: ...

# ✅ 泛型
from typing import TypeVar, Generic

T = TypeVar("T")

class Cache(Generic[T]):
    def get(self, key: str) -> T | None: ...
    def set(self, key: str, value: T, ttl: int = 300) -> None: ...
```

**禁止的做法**:
- `Any` — 用 `object`、`TypeVar` bound 或具体类型替代
- 不标注返回值（`-> None` 也要写）
- `Dict[str, Any]` 做数据传递 — 用 Pydantic Model 或 TypedDict

## 3. 函数设计

```python
# ✅ 好的函数设计
def create_user(
    name: str,
    email: str,
    *,                          # 强制关键字参数
    role: UserRole = UserRole.MEMBER,
    send_welcome: bool = True,
) -> User:
    """创建新用户。

    Args:
        name: 用户显示名称，1-100字符。
        email: 用户邮箱，必须唯一。
        role: 用户角色，默认为普通成员。
        send_welcome: 是否发送欢迎邮件。

    Returns:
        创建成功的用户对象。

    Raises:
        ValidationError: 输入数据不合法。
        ConflictError: 邮箱已被注册。
    """
    validated = _validate_user_input(name=name, email=email)
    user = _persist_user(validated, role=role)
    if send_welcome:
        _send_welcome_email(user)
    return user
```

**设计原则**:
- 函数做且仅做一件事，理想长度 20 行，上限 50 行
- 超过 3 个参数的函数使用 `*` 强制关键字参数
- 可变默认值是 Bug 之源：`def f(items: list | None = None)`
- 优先返回值而非修改入参（纯函数思维）
- 生成器处理大数据集：`yield` 而非构建完整列表

## 4. 类设计

```python
# ✅ 使用 dataclass 做数据容器
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(frozen=True)  # 不可变优先
class User:
    id: int
    name: str
    email: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# ✅ 使用 Pydantic 做输入验证
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    role: UserRole = UserRole.MEMBER

    model_config = {"strict": True}

# ✅ 使用 Protocol 而非 ABC（除非需要默认实现）
class Notifier(Protocol):
    async def send(self, recipient: str, message: str) -> bool: ...

class EmailNotifier:
    """实现 Notifier 协议，无需显式继承"""
    async def send(self, recipient: str, message: str) -> bool:
        ...
```

**设计原则**:
- 组合优于继承，继承层级最多 2 层
- `frozen=True` dataclass 是默认选择
- 使用 `__slots__` 优化内存（高频创建的对象）
- 避免 God Class — 类的方法超过 10 个就该考虑拆分

## 5. 错误处理

```python
# ✅ 自定义异常层级
class AppError(Exception):
    """应用错误基类"""
    def __init__(self, message: str, code: str, details: dict | None = None) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ValidationError(AppError):
    """输入验证失败"""
    pass

class NotFoundError(AppError):
    """资源不存在"""
    pass

class ConflictError(AppError):
    """资源冲突（如唯一约束）"""
    pass

# ✅ 正确的异常处理
def get_user(user_id: int) -> User:
    try:
        return repository.get(user_id)
    except DBConnectionError:
        logger.exception("Database connection failed for user_id=%d", user_id)
        raise ServiceUnavailableError("Database temporarily unavailable") from None

# ❌ 禁止的做法
try:
    ...
except Exception:     # 太宽泛
    pass              # 吞掉异常
```

**原则**:
- 具体异常优先，`except ValueError` 而非 `except Exception`
- 异常消息包含上下文：`f"User {user_id} not found"` 而非 `"not found"`
- 使用 `logger.exception()` 记录异常（自动包含堆栈）
- 资源清理用 `contextmanager` 或 `try/finally`
- `raise ... from e` 保留异常链，`from None` 明确截断

## 6. 导入规范

```python
# 1. 标准库
import os
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import TypeAlias

# 2. 第三方库
import httpx
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

# 3. 本项目
from myapp.core.config import settings
from myapp.core.exceptions import NotFoundError
from myapp.models.user import User
```

**规则**:
- 使用 ruff 的 `I` 规则自动管理导入顺序（等效 isort，profile=black）
- 禁止 `from module import *`
- 禁止在函数内部 import（除非解决循环依赖）
- 使用绝对导入而非相对导入（包内例外）

## 7. 文档字符串 (Google风格)

```python
def fetch_paginated(
    endpoint: str,
    *,
    page: int = 1,
    page_size: int = 20,
    timeout: float = 10.0,
) -> PaginatedResponse:
    """从API获取分页数据。

    对指定endpoint发起GET请求，返回分页结果。
    自动处理重试和超时。

    Args:
        endpoint: API端点路径（不含base URL）。
        page: 页码，从1开始。
        page_size: 每页条数，最大100。
        timeout: 请求超时秒数。

    Returns:
        包含items列表和分页元数据的响应对象。

    Raises:
        ValidationError: page < 1 或 page_size > 100。
        TimeoutError: 请求超时。
        ApiError: API返回非2xx状态码。

    Example:
        >>> response = fetch_paginated("/users", page=2, page_size=10)
        >>> len(response.items)
        10
    """
```

**规则**:
- 所有公共函数、类、模块必须有 docstring
- 私有函数可选，但复杂逻辑建议有
- 使用 Google 风格（Args/Returns/Raises/Example）
- 第一行是一句话总结，空一行后是详细说明

## 8. 异步编程

```python
# ✅ async/await 最佳实践
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    session = await create_session()
    try:
        yield session
        await session.commit()
    except Exception:  # DB 会话管理需要兜底回滚，此处宽捕获是标准模式
        await session.rollback()
        raise
    finally:
        await session.close()

async def fetch_all_users(client: httpx.AsyncClient) -> list[User]:
    """并发获取多页用户数据"""
    first_page = await client.get("/users?page=1")
    total_pages = first_page.json()["total_pages"]

    tasks = [
        client.get(f"/users?page={p}")
        for p in range(2, total_pages + 1)
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    users = first_page.json()["items"]
    for resp in responses:
        if isinstance(resp, Exception):
            logger.error("Failed to fetch page: %s", resp)
            continue
        users.extend(resp.json()["items"])
    return [User(**u) for u in users]
```

**原则**:
- I/O密集 → async/await，CPU密集 → ProcessPoolExecutor
- 不要在 async 函数中调用阻塞操作（用 `run_in_executor`）
- `asyncio.gather()` 并发，`asyncio.Semaphore` 限制并发数
- 异步上下文管理器管理资源生命周期

## 9. 项目配置

```toml
# pyproject.toml — 推荐的统一配置
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-asyncio>=0.24",
    "ruff>=0.8",
    "mypy>=1.13",
    "bandit>=1.8",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "PT", "RUF"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short --strict-markers"

[tool.bandit]
exclude_dirs = ["tests"]
```

## 10. 日志规范

### 基本原则

- 使用 `logging` 标准库或 `structlog`，禁止用 `print()` 做日志
- 每个模块使用 `logger = logging.getLogger(__name__)`
- 生产环境使用 JSON 格式输出，便于日志聚合系统解析

### Log Level 使用策略

| Level | 用途 | 示例 |
|-------|------|------|
| `DEBUG` | 开发调试信息，生产环境关闭 | 函数入参、中间状态 |
| `INFO` | 关键业务事件 | 用户注册成功、任务启动/完成 |
| `WARNING` | 可恢复的异常情况 | 重试、降级、配置缺失使用默认值 |
| `ERROR` | 需要关注的错误 | 外部服务调用失败、数据校验失败 |
| `CRITICAL` | 系统不可用 | 数据库连接丢失、配置加载失败 |

### 敏感信息脱敏

```python
import logging

logger = logging.getLogger(__name__)

# ❌ 日志中暴露敏感信息
logger.info("User login: email=%s, password=%s", email, password)

# ✅ 脱敏处理
logger.info("User login: email=%s", email)
```

### 结构化日志（推荐）

```python
import structlog

logger = structlog.get_logger()

logger.info("order_created", order_id=order.id, user_id=user.id, amount=order.total)
```

## 11. 关键禁忌

| 禁止 | 替代方案 |
|------|----------|
| `eval()` / `exec()` | 使用 AST 解析或安全替代 |
| `pickle.loads(untrusted)` | 使用 JSON 或 Pydantic |
| `os.system()` / `shell=True` | 使用 `subprocess.run([...])` |
| `from module import *` | 显式导入 |
| bare `except:` | `except SpecificError:` |
| 可变默认值 `def f(x=[])` | `def f(x: list | None = None)` |
| `type: ignore` 无注释 | `type: ignore[specific-code]  # reason` |
| 全局可变状态 | 依赖注入或上下文变量 |
| 硬编码密钥/密码 | 环境变量 + python-dotenv |
| `print()` 做日志 | `logging` 或 `structlog` |
