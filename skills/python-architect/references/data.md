# 数据工程领域指南

数据处理、ETL Pipeline、ML Pipeline 的架构设计指南。

## 推荐技术栈

| 场景 | 首选 | 备选 |
|------|------|------|
| DataFrame | Polars (大数据) | Pandas (生态广) |
| 大规模ETL | PySpark / Dask | Ray |
| 编排调度 | Airflow / Prefect | Dagster, Luigi |
| 数据验证 | Pandera / Great Expectations | Pydantic |
| ORM/查询 | SQLAlchemy 2.0 | DuckDB (分析) |
| 序列化 | Parquet (列存) | CSV (兼容) |

## 项目结构

```
src/myetl/
├── pipelines/
│   ├── __init__.py
│   ├── base.py               # Pipeline抽象基类
│   ├── daily_orders.py        # 具体pipeline
│   └── user_metrics.py
├── extractors/               # E: 数据提取
│   ├── database.py
│   ├── api.py
│   └── file.py
├── transformers/             # T: 数据转换
│   ├── clean.py
│   ├── aggregate.py
│   └── enrich.py
├── loaders/                  # L: 数据加载
│   ├── warehouse.py
│   └── file.py
├── validators/               # 数据质量验证
│   ├── schemas.py
│   └── checks.py
├── core/
│   ├── config.py
│   └── exceptions.py
└── utils/
    ├── logging.py
    └── checkpoint.py
```

## 关键模式

### Pipeline抽象

```python
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Literal

import polars as pl

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class PipelineResult:
    name: str
    status: Literal["success", "failed", "skipped"]
    rows_processed: int
    duration_seconds: float
    error: str | None = None

# ABC 用于提供默认 run() 实现；纯接口定义优先用 Protocol
class Pipeline(ABC):
    @abstractmethod
    def extract(self, run_date: date) -> pl.LazyFrame: ...

    @abstractmethod
    def transform(self, data: pl.LazyFrame) -> pl.LazyFrame: ...

    @abstractmethod
    def load(self, data: pl.DataFrame) -> int: ...

    def run(self, run_date: date) -> PipelineResult:
        """Pipeline 顶层入口，兜底捕获异常保证返回 PipelineResult。"""
        start = time.monotonic()
        try:
            raw = self.extract(run_date)
            transformed = self.transform(raw)
            df = transformed.collect()
            rows = self.load(df)
            return PipelineResult(
                name=self.__class__.__name__,
                status="success",
                rows_processed=rows,
                duration_seconds=time.monotonic() - start,
            )
        except (OSError, pl.exceptions.ComputeError, RuntimeError) as e:
            logger.exception("Pipeline %s failed", self.__class__.__name__)
            return PipelineResult(
                name=self.__class__.__name__,
                status="failed",
                rows_processed=0,
                duration_seconds=time.monotonic() - start,
                error=str(e),
            )
```

### 流式处理（避免内存爆炸）

```python
import json
from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import polars as pl

# ❌ 全量加载
df = pd.read_sql("SELECT * FROM huge_table", engine)

# ✅ 分块处理 (Pandas)
for chunk in pd.read_sql("SELECT * FROM huge_table", engine, chunksize=50_000):
    process(chunk)

# ✅ 懒加载 (Polars)
lazy = pl.scan_parquet("data/*.parquet")
result = lazy.filter(pl.col("date") >= cutoff).group_by("user_id").agg(
    pl.col("amount").sum()
).collect()

# ✅ 生成器模式
def extract_rows(path: Path) -> Iterator[dict[str, object]]:
    with open(path) as f:
        for line in f:
            yield json.loads(line)
```

### 数据验证

```python
import pandas as pd
import pandera as pa

schema = pa.DataFrameSchema({
    "user_id": pa.Column(int, nullable=False, unique=True),
    "email": pa.Column(str, pa.Check.str_matches(r"^[\w.]+@[\w.]+$")),
    "amount": pa.Column(float, pa.Check.ge(0)),
    "created_at": pa.Column(pa.DateTime, nullable=False),
})

@pa.check_output(schema)
def transform_users(raw: pd.DataFrame) -> pd.DataFrame:
    """自动验证输出数据质量"""
    ...
```

### 幂等性和断点续跑

```python
from pathlib import Path

import polars as pl

class CheckpointManager:
    """Pipeline checkpoint管理，支持断点续跑"""

    def __init__(self, pipeline_name: str, checkpoint_dir: Path) -> None:
        self._dir = checkpoint_dir / pipeline_name
        self._dir.mkdir(parents=True, exist_ok=True)

    def save(self, stage: str, data: pl.DataFrame) -> None:
        path = self._dir / f"{stage}.parquet"
        data.write_parquet(path)

    def load(self, stage: str) -> pl.DataFrame | None:
        path = self._dir / f"{stage}.parquet"
        if path.exists():
            return pl.read_parquet(path)
        return None

    def has_stage(self, stage: str) -> bool:
        return (self._dir / f"{stage}.parquet").exists()
```

## 性能要点

- Polars: 默认懒执行(`scan_*` + `.collect()`)，自动并行
- Pandas: 大数据用 `chunksize`，类型优化(`category`, `int32`)
- I/O: Parquet >> CSV（压缩率好、列裁剪、类型保留）
- SQL: 批量INSERT (`executemany` / `COPY`)，禁止逐行INSERT
- 内存: 及时 `del` + `gc.collect()` 释放大DataFrame

## 审查重点

| 检查项 | 严重度 |
|--------|--------|
| 大表全量 `SELECT *` 无分块 | 🔴 |
| DataFrame 全量加载到内存 | 🔴 |
| 无数据质量验证 | 🟡 |
| 无幂等性保证 | 🟡 |
| 硬编码数据库连接字符串 | 🔴 |
| 无日志/监控 | 🟡 |
| 无断点续跑能力 | 🟡 |
