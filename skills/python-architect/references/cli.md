# CLI 工具领域指南

Python CLI工具/命令行应用的架构设计指南。

## 推荐技术栈

| 场景 | 首选 | 备选 |
|------|------|------|
| CLI框架 | Typer | Click |
| 终端美化 | Rich | - |
| 进度条 | Rich Progress | tqdm |
| 配置文件 | TOML (tomllib) | YAML |
| 环境变量 | pydantic-settings | python-dotenv |

## 项目结构

```
src/mytool/
├── cli/
│   ├── __init__.py
│   ├── main.py               # Typer app 入口
│   ├── commands/              # 子命令
│   │   ├── init.py
│   │   ├── run.py
│   │   └── config.py
│   └── formatters.py         # 输出格式化(table/json/csv)
├── core/
│   ├── config.py
│   └── exceptions.py
├── services/                  # 核心业务逻辑
└── utils/
```

## 关键模式

### Typer应用结构

```python
# cli/main.py
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(
    name="mytool",
    help="工具描述",
    no_args_is_help=True,
)
console = Console()

@app.command()
def run(
    input_path: Path = typer.Argument(..., help="输入文件路径", exists=True),
    output: Path = typer.Option("output", "-o", "--output", help="输出目录"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="详细输出"),
    format: str = typer.Option("table", "-f", "--format", help="输出格式: table/json/csv"),
) -> None:
    """执行主要操作"""
    try:
        result = service.process(input_path, verbose=verbose)
        _render_output(result, format=format, output=output)
    except AppError as e:
        console.print(f"[red]错误:[/red] {e.message}")
        raise typer.Exit(code=1) from None

@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="显示当前配置"),
) -> None:
    """管理配置"""
    if show:
        _print_config()

def _render_output(result: Result, *, format: str, output: Path) -> None:
    """根据格式输出结果"""
    if format == "json":
        console.print_json(result.model_dump_json())
    elif format == "csv":
        output.write_text(result.to_csv())
        console.print(f"✅ 已写入 {output}")
    else:
        table = _build_table(result)
        console.print(table)
```

### Rich美化输出

```python
from rich.table import Table
from rich.progress import track
from rich.panel import Panel

def _build_table(items: list[Item]) -> Table:
    table = Table(title="处理结果", show_lines=True)
    table.add_column("名称", style="cyan")
    table.add_column("状态", justify="center")
    table.add_column("耗时", justify="right")

    for item in items:
        status = "[green]✅[/green]" if item.ok else "[red]❌[/red]"
        table.add_row(item.name, status, f"{item.duration:.1f}s")
    return table

def process_files(paths: list[Path]) -> None:
    for path in track(paths, description="处理中..."):
        _process_one(path)
```

### 错误处理与退出码

```python
import functools

import typer
from rich.console import Console

console = Console()

@app.callback()
def main() -> None:
    """mytool — 工具描述"""
    pass

# 退出码约定: 0=成功, 1=应用错误, 2=输入错误

class CliErrorHandler:
    @staticmethod
    def handle(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                console.print(f"[red]输入错误:[/red] {e.message}")
                raise typer.Exit(code=2) from None
            except AppError as e:
                console.print(f"[red]错误:[/red] {e.message}")
                raise typer.Exit(code=1) from None
            except KeyboardInterrupt:
                console.print("\n[yellow]用户中断[/yellow]")
                raise typer.Exit(code=130) from None
        return wrapper
```

### 配置管理

```python
# 优先级: 命令行参数 > 环境变量 > 配置文件 > 默认值
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_LOCATIONS = [
    Path.cwd() / ".mytool.toml",
    Path.home() / ".config" / "mytool" / "config.toml",
]

@dataclass(frozen=True)
class ToolConfig:
    output_dir: Path = Path("output")
    verbose: bool = False
    format: str = "table"
    extra: dict[str, object] = field(default_factory=dict)

def load_config() -> ToolConfig:
    for path in CONFIG_LOCATIONS:
        if path.exists():
            with open(path, "rb") as f:
                raw = tomllib.load(f)
            return ToolConfig(**{k: v for k, v in raw.items() if k in ToolConfig.__dataclass_fields__})
    return ToolConfig()
```

## 设计原则

1. **逻辑与展示分离** — CLI层只做参数解析和输出格式化，核心逻辑在service层
2. **可测试** — 业务逻辑不依赖typer/click，可独立单元测试
3. **优雅退出** — 捕获 `KeyboardInterrupt`，清理临时文件
4. **进度反馈** — 长时操作必须有进度条或状态输出
5. **帮助文档** — 每个命令和参数必须有 `help` 描述
6. **退出码规范** — 0/1/2 分别表示成功/应用错误/输入错误

## 审查重点

| 检查项 | 严重度 |
|--------|--------|
| 业务逻辑写在CLI命令函数里 | 🟡 |
| 缺少 `--help` 描述 | 🟡 |
| 长时操作无进度反馈 | 🟡 |
| 未处理 KeyboardInterrupt | 🟡 |
| 退出码不规范（全用0或全用1） | 🟡 |
| 输出不支持机器可读格式(json) | 🟡 |
| 硬编码路径而非参数化 | 🔴 |
