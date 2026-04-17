# 审查案例

真实场景的完整审查流程和报告示例。

---

## 案例1: FastAPI Web后端审查

### 概述
审查一个 FastAPI + SQLAlchemy + Pydantic 的用户管理API服务。

### 自动化检查结果
```
ruff:   ⚠️ 12个问题（3个S类安全告警，9个风格问题）
mypy:   ⚠️ 8个错误（5个missing-return-type，3个incompatible-type）
bandit: 🔴 2个高危（B608 SQL注入，B105 硬编码密码）
pytest: ✅ 45/45 通过，覆盖率 72%
```

### 严重问题 🔴

#### 问题1: SQL注入风险
**位置**: `src/app/repositories/user_repo.py:34`
**问题**: 使用f-string构建SQL查询

```python
# ❌ 当前代码
async def search_users(self, keyword: str) -> list[User]:
    query = text(f"SELECT * FROM users WHERE name LIKE '%{keyword}%'")
    result = await self.session.execute(query)
    return [User(**row._mapping) for row in result]
```

**修复**:
```python
# ✅ 参数化查询 + ORM
async def search_users(self, keyword: str) -> list[User]:
    stmt = select(UserModel).where(UserModel.name.ilike(f"%{keyword}%"))
    result = await self.session.execute(stmt)
    return [User.model_validate(row) for row in result.scalars()]
```

#### 问题2: 硬编码JWT密钥
**位置**: `src/app/core/auth.py:8`

```python
# ❌
SECRET_KEY = "super-secret-key-123"

# ✅
from pydantic_settings import BaseSettings

class AuthSettings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

    model_config = {"env_prefix": "AUTH_"}
```

### 重要建议 🟡

#### 建议1: API层混入业务逻辑
**位置**: `src/app/api/routes/users.py`

```python
# ❌ 路由函数里做业务判断
@router.post("/users")
async def create_user(data: CreateUserSchema, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar():
        raise HTTPException(409, "Email exists")
    user = User(**data.model_dump())
    user.password = bcrypt.hash(data.password)
    db.add(user)
    await db.commit()
    return user

# ✅ 分层清晰
@router.post("/users", status_code=201)
async def create_user(
    data: CreateUserRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return await service.create_user(data)
```

#### 建议2: 缺少类型标注
全局搜索到 15 个公共函数缺少返回类型标注，5 处使用 `dict` 做数据传递。

### 评分
- 架构设计: 5/10
- 代码质量: 6/10
- 类型安全: 4/10
- 安全性: 3/10
- 测试覆盖: 7/10

---

## 案例2: 数据处理Pipeline审查

### 概述
审查一个 Pandas + SQLAlchemy 的数据ETL pipeline，每日处理千万级订单数据。

### 严重问题 🔴

#### 问题1: 内存爆炸风险
**位置**: `src/etl/extract.py:22`

```python
# ❌ 一次性加载千万行到内存
def extract_orders(date: str) -> pd.DataFrame:
    engine = create_engine(DB_URL)
    df = pd.read_sql(f"SELECT * FROM orders WHERE date = '{date}'", engine)
    return df
```

**修复**:
```python
# ✅ 分块读取 + 参数化
def extract_orders(date: str, chunk_size: int = 50_000) -> Iterator[pd.DataFrame]:
    engine = create_engine(settings.db_url)
    query = text("SELECT * FROM orders WHERE date = :date")
    for chunk in pd.read_sql(query, engine, params={"date": date}, chunksize=chunk_size):
        yield chunk
```

#### 问题2: 无错误恢复机制

```python
# ❌ 失败则整个pipeline重跑
def run_pipeline(date: str) -> None:
    df = extract_orders(date)      # 10分钟
    df = transform(df)              # 5分钟
    load_to_warehouse(df)           # 3分钟

# ✅ 带checkpoint的恢复机制
def run_pipeline(date: str, *, resume_from: str | None = None) -> None:
    checkpoint = CheckpointManager(f"pipeline_{date}")

    if resume_from != "transform":
        for chunk in extract_orders(date):
            checkpoint.save("extract", chunk)

    if resume_from not in ("load",):
        extracted = checkpoint.load("extract")
        transformed = transform(extracted)
        checkpoint.save("transform", transformed)

    transformed = checkpoint.load("transform")
    load_to_warehouse(transformed)
    checkpoint.cleanup()
```

### 评分
- 架构设计: 4/10
- 代码质量: 5/10
- 性能: 3/10
- 可靠性: 3/10
- 测试覆盖: 2/10

---

## 案例3: CLI工具设计+开发

### 概述
从零设计一个 Typer + Rich 的数据库迁移CLI工具。完整经历"设计→审核→开发→测试"流程。

### 阶段2设计产出

```python
# 技术设计核心 — 接口定义
class MigrationRunner(Protocol):
    def apply(self, migration: Migration) -> MigrationResult: ...
    def rollback(self, migration: Migration) -> MigrationResult: ...
    def get_applied(self) -> list[AppliedMigration]: ...

@dataclass(frozen=True)
class Migration:
    version: str
    description: str
    up_sql: str
    down_sql: str
    checksum: str

@dataclass(frozen=True)
class MigrationResult:
    version: str
    status: Literal["applied", "rolled_back", "failed"]
    duration_ms: int
    error: str | None = None
```

### 阶段3审核发现

🟡 **建议**: `MigrationRunner` 应该支持 dry-run 模式

```python
# 审核后补充
class MigrationRunner(Protocol):
    def apply(self, migration: Migration, *, dry_run: bool = False) -> MigrationResult: ...
```

### 阶段5测试摘要

```
tests/unit/test_migration_parser.py    12 passed
tests/unit/test_migration_runner.py    18 passed
tests/integration/test_cli.py           8 passed
tests/integration/test_postgres.py      6 passed
─────────────────────────────────────────────
44 passed, 0 failed, coverage: 94%
```

### 阶段6验收

```
完整性: ✅ 所有需求已实现且有对应测试
正确性: ✅ 实现与spec一致
工程质量: ✅ ruff/mypy/bandit全部通过
Final: 通过 ✅
```
