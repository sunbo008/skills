# 详细审查清单与代码示例

逐项检查的审查清单，附正确/错误代码对比。

---

## 一、架构与设计模式

### 1.1 依赖注入

```python
# ❌ 硬编码依赖 — 无法测试、无法替换
class OrderService:
    def __init__(self):
        self.db = PostgresDatabase("postgresql://prod:5432/orders")
        self.notifier = SmtpEmailSender("smtp.company.com")

# ✅ 依赖注入 — 可测试、可替换
class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        notifier: Notifier,
    ) -> None:
        self._repository = repository
        self._notifier = notifier

    def create_order(self, request: CreateOrderRequest) -> Order:
        order = Order.from_request(request)
        self._repository.save(order)
        self._notifier.send(order.user_email, f"Order {order.id} confirmed")
        return order

# 测试时注入mock
def test_create_order():
    repo = FakeOrderRepository()
    notifier = FakeNotifier()
    service = OrderService(repository=repo, notifier=notifier)
    order = service.create_order(CreateOrderRequest(item_id=1, quantity=2))
    assert repo.saved[-1] == order
    assert notifier.sent[-1].recipient == order.user_email
```

### 1.2 分层架构

```
# ✅ 正确的依赖方向
API/CLI层 → Service层 → Repository层 → 数据库
     ↓           ↓           ↓
   Schema      Model      ORM/Query

# ❌ 违反分层 — API层直接操作数据库
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()  # 业务逻辑泄露到API层
    if not user:
        raise HTTPException(404)
    return user

# ✅ 正确分层
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    return service.get_by_id(user_id)  # API层只做转发
```

### 1.3 策略模式替代条件分支

```python
# ❌ 冗长的if-elif链
def calculate_price(order: Order) -> Decimal:
    if order.type == "standard":
        price = order.subtotal
    elif order.type == "premium":
        price = order.subtotal * Decimal("0.9")
    elif order.type == "wholesale":
        price = order.subtotal * Decimal("0.75")
    # ... 每加一个类型就要改这个函数

# ✅ 策略模式
from typing import Protocol

class PricingStrategy(Protocol):
    def calculate(self, subtotal: Decimal) -> Decimal: ...

PRICING_STRATEGIES: dict[str, PricingStrategy] = {
    "standard": StandardPricing(),
    "premium": PremiumPricing(discount=Decimal("0.1")),
    "wholesale": WholesalePricing(discount=Decimal("0.25")),
}

def calculate_price(order: Order) -> Decimal:
    strategy = PRICING_STRATEGIES.get(order.type)
    if strategy is None:
        raise ValueError(f"Unknown order type: {order.type}")
    return strategy.calculate(order.subtotal)
```

---

## 二、代码质量审查清单

### 2.1 类型安全

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| 公共函数缺少类型标注 | 🔴 | 所有公共API必须标注 |
| 使用 `Any` | 🔴 | 用 `object`、`TypeVar`、`Protocol` 替代 |
| `Dict[str, Any]` 传递数据 | 🟡 | 用 Pydantic Model 或 TypedDict |
| `# type: ignore` 无说明 | 🟡 | 必须注明具体错误码和原因 |
| 缺少 `-> None` 返回标注 | 🟡 | 即使返回None也要标注 |
| `Optional[X]` 旧写法 | 🟢 | 用 `X \| None` (Python 3.10+) |

### 2.2 函数质量

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| 函数超过50行 | 🟡 | 拆分为更小的函数 |
| 参数超过5个 | 🟡 | 封装为dataclass/Pydantic Model |
| 可变默认值 `def f(x=[])` | 🔴 | 改为 `x: list \| None = None` |
| 副作用函数无日志/无返回 | 🟡 | 至少返回操作结果或记录日志 |
| 嵌套超过3层 | 🟡 | 提早返回(guard clause)减少嵌套 |
| 返回 `dict` 而非结构化对象 | 🟡 | 使用 dataclass 或 Pydantic |

### 2.3 错误处理

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| bare `except:` | 🔴 | 必须指定异常类型 |
| `except Exception: pass` | 🔴 | 至少记录日志 |
| 缺少资源清理 | 🔴 | 用 with/contextmanager |
| 异常信息无上下文 | 🟡 | 包含关键变量值 |
| 重复 try/except | 🟡 | 提取为装饰器或中间件 |

### 2.4 性能

```python
# ❌ 全量加载大文件
def process_large_file(path: Path) -> list[Record]:
    with open(path) as f:
        data = json.load(f)  # 全部读入内存
    return [Record(**item) for item in data]

# ✅ 流式处理
def process_large_file(path: Path) -> Iterator[Record]:
    with open(path) as f:
        for line in f:
            yield Record(**json.loads(line))

# ❌ 循环中重复查询
for order in orders:
    user = session.get(User, order.user_id)  # N+1

# ✅ 批量查询
user_ids = {o.user_id for o in orders}
stmt = select(User).where(User.id.in_(user_ids))
users = {u.id: u for u in session.execute(stmt).scalars()}
for order in orders:
    user = users[order.user_id]

# ❌ 字符串拼接循环
result = ""
for item in items:
    result += str(item) + ", "

# ✅ join
result = ", ".join(str(item) for item in items)
```

| 检查项 | 严重度 | 检测方法 |
|--------|--------|----------|
| N+1查询 | 🔴 | 搜索循环内的db查询 |
| 大数据全量加载 | 🔴 | 搜索 `json.load`/`readlines`/`fetchall` |
| 循环内字符串拼接 | 🟡 | 搜索循环内 `+=` 字符串 |
| 缺少缓存 | 🟡 | 重复计算的热路径 |
| 同步I/O在async上下文 | 🔴 | 搜索 `open()`/`requests.` 在 async 函数中 |

---

## 三、安全审查清单

### 3.1 注入攻击

```python
# ❌ SQL注入
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

# ✅ 参数化查询
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))

# ❌ 命令注入
os.system(f"convert {filename} output.pdf")

# ✅ 安全子进程
subprocess.run(["convert", filename, "output.pdf"], check=True)

# ❌ 路径遍历
file_path = BASE_DIR / user_input
content = file_path.read_text()

# ✅ 路径验证
file_path = (BASE_DIR / user_input).resolve()
if not file_path.is_relative_to(BASE_DIR):
    raise SecurityError("Path traversal detected")
content = file_path.read_text()
```

### 3.2 安全检查清单

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| SQL字符串拼接 | 🔴 | 参数化查询 |
| `os.system`/`shell=True` | 🔴 | `subprocess.run([...])` |
| 硬编码密钥/密码 | 🔴 | 环境变量 + dotenv |
| `pickle.loads` 不可信数据 | 🔴 | JSON/Pydantic |
| `eval()`/`exec()` | 🔴 | AST解析或安全替代 |
| 路径遍历未验证 | 🔴 | `resolve()` + `is_relative_to()` |
| 密码未哈希 | 🔴 | bcrypt/argon2 |
| CORS过宽 `allow_origins=["*"]` | 🟡 | 限制具体域名 |
| 日志包含敏感信息 | 🟡 | 脱敏处理 |
| 依赖有已知漏洞 | 🟡 | `pip-audit` 检查 |

---

## 四、测试审查

### 4.1 测试结构

```python
# ✅ 好的测试结构
class TestUserService:
    """按被测类组织"""

    @pytest.fixture
    def service(self, fake_repo, fake_notifier):
        return UserService(repository=fake_repo, notifier=fake_notifier)

    def test_create_valid_user_persists_and_notifies(self, service, fake_repo):
        """正常路径：创建成功 → 保存 + 通知"""
        user = service.create(name="Alice", email="a@b.com")
        assert user.name == "Alice"
        assert fake_repo.saved_count == 1

    def test_create_duplicate_email_raises_conflict(self, service, fake_repo):
        """异常路径：邮箱冲突"""
        fake_repo.existing_emails = {"a@b.com"}
        with pytest.raises(ConflictError, match="email"):
            service.create(name="Bob", email="a@b.com")

    @pytest.mark.parametrize("name", ["", " ", "x" * 101])
    def test_create_invalid_name_raises_validation(self, service, name):
        """边界条件：无效名称"""
        with pytest.raises(ValidationError):
            service.create(name=name, email="valid@email.com")
```

### 4.2 测试质量清单

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| 无测试 | 🔴 | 核心逻辑必须有单元测试 |
| 测试依赖外部服务 | 🟡 | 使用mock/fake替代 |
| 测试之间有顺序依赖 | 🔴 | 每个测试必须独立 |
| 只测正常路径 | 🟡 | 必须覆盖异常和边界 |
| 断言模糊 `assert result` | 🟡 | 断言具体值 `assert result.status == "active"` |
| 测试名不描述行为 | 🟡 | `test_<action>_<scenario>_<expected>` |
| fixture作用域不合理 | 🟡 | DB fixture用session，纯数据用function |

---

## 五、项目结构审查

### 5.1 标准项目结构

```
myproject/
├── pyproject.toml          # 项目元数据 + 工具配置
├── README.md
├── .env.example            # 环境变量模板
├── .gitignore
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── core/           # 配置、异常、常量
│       │   ├── config.py
│       │   └── exceptions.py
│       ├── models/         # 数据模型 (Pydantic/dataclass/ORM)
│       ├── services/       # 业务逻辑
│       ├── repositories/   # 数据访问
│       ├── api/            # Web接口 (FastAPI routes)
│       │   └── v1/
│       ├── cli/            # CLI入口 (Click/Typer)
│       └── utils/          # 纯工具函数
├── tests/
│   ├── conftest.py         # 共享fixture
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                # 运维/部署脚本
├── docs/                   # 文档
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

### 5.2 结构检查清单

| 检查项 | 严重度 | 说明 |
|--------|--------|------|
| 缺少 pyproject.toml | 🔴 | 现代Python项目标配 |
| 代码不在 src/ 下 | 🟡 | 推荐 src layout 避免导入混淆 |
| 测试代码与业务混在一起 | 🔴 | 分离 tests/ 目录 |
| 缺少 __init__.py | 🟡 | 包目录必须有 |
| 配置散落各处 | 🟡 | 集中到 core/config.py |
| .env 提交到git | 🔴 | 加入 .gitignore + 提供 .env.example |
| 缺少依赖锁定 | 🟡 | poetry.lock 或 pip-compile |
