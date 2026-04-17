#!/bin/bash
# 初始化Python项目骨架
# 用法: bash init-project.sh <project-name> [--web|--cli|--data|--lib]

set -euo pipefail

if [ $# -lt 1 ]; then
  echo "用法: bash init-project.sh <project-name> [--web|--cli|--data|--lib]"
  echo ""
  echo "类型:"
  echo "  --web   Web后端项目 (FastAPI)"
  echo "  --cli   CLI工具项目 (Typer + Rich)"
  echo "  --data  数据处理项目 (Pandas/Polars)"
  echo "  --lib   通用Python库"
  echo "  (默认)  通用Python项目"
  exit 1
fi

PROJECT_NAME="$1"
PROJECT_TYPE="${2:---lib}"
PKG_NAME=$(echo "$PROJECT_NAME" | tr '-' '_')

echo "📦 创建项目: $PROJECT_NAME (类型: $PROJECT_TYPE)"
echo ""

mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# ---- 基础目录结构 ----
mkdir -p "src/$PKG_NAME/core"
mkdir -p "src/$PKG_NAME/models"
mkdir -p "src/$PKG_NAME/services"
mkdir -p "tests/unit"
mkdir -p "tests/integration"

# ---- __init__.py ----
echo '"""'"$PROJECT_NAME"' — TODO: 项目描述"""' > "src/$PKG_NAME/__init__.py"
touch "src/$PKG_NAME/core/__init__.py"
touch "src/$PKG_NAME/models/__init__.py"
touch "src/$PKG_NAME/services/__init__.py"

# ---- core/config.py ----
cat > "src/$PKG_NAME/core/config.py" << 'PYEOF'
"""应用配置管理"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """通过环境变量或.env文件加载配置"""

    app_name: str = "myapp"
    debug: bool = False
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
PYEOF

# ---- core/exceptions.py ----
cat > "src/$PKG_NAME/core/exceptions.py" << 'PYEOF'
"""自定义异常层级"""


class AppError(Exception):
    """应用错误基类"""

    def __init__(self, message: str, code: str = "UNKNOWN", details: dict | None = None) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ValidationError(AppError):
    """输入验证失败"""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class NotFoundError(AppError):
    """资源不存在"""

    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(f"{resource} '{identifier}' not found", code="NOT_FOUND")


class ConflictError(AppError):
    """资源冲突"""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="CONFLICT")
PYEOF

# ---- tests/conftest.py ----
cat > "tests/conftest.py" << 'PYEOF'
"""共享测试fixture"""

import pytest  # noqa: F401 — pytest fixtures需要此导入
PYEOF

touch "tests/__init__.py"
touch "tests/unit/__init__.py"
touch "tests/integration/__init__.py"

# ---- 根据类型添加依赖 ----
DEPS='    "pydantic>=2.0",\n    "pydantic-settings>=2.0",'
DEV_DEPS='    "pytest>=8.0",\n    "pytest-cov>=5.0",\n    "ruff>=0.8",\n    "mypy>=1.13",\n    "bandit>=1.8",'

case "$PROJECT_TYPE" in
  --web)
    DEPS="$DEPS"'\n    "fastapi>=0.115",\n    "uvicorn[standard]>=0.32",\n    "sqlalchemy[asyncio]>=2.0",\n    "alembic>=1.14",\n    "httpx>=0.27",'
    DEV_DEPS="$DEV_DEPS"'\n    "pytest-asyncio>=0.24",\n    "httpx>=0.27",'
    mkdir -p "src/$PKG_NAME/api/v1"
    mkdir -p "src/$PKG_NAME/repositories"
    touch "src/$PKG_NAME/api/__init__.py"
    touch "src/$PKG_NAME/api/v1/__init__.py"
    touch "src/$PKG_NAME/repositories/__init__.py"
    ;;
  --cli)
    DEPS="$DEPS"'\n    "typer>=0.12",\n    "rich>=13.0",'
    mkdir -p "src/$PKG_NAME/cli"
    touch "src/$PKG_NAME/cli/__init__.py"
    ;;
  --data)
    DEPS="$DEPS"'\n    "polars>=1.0",\n    "sqlalchemy>=2.0",'
    DEV_DEPS="$DEV_DEPS"'\n    "pytest-asyncio>=0.24",'
    mkdir -p "src/$PKG_NAME/pipelines"
    touch "src/$PKG_NAME/pipelines/__init__.py"
    ;;
esac

# ---- pyproject.toml ----
cat > "pyproject.toml" << TOMLEOF
[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "TODO: 项目描述"
requires-python = ">=3.11"
dependencies = [
$(echo -e "$DEPS" | sed 's/^/    /')
]

[project.optional-dependencies]
dev = [
$(echo -e "$DEV_DEPS" | sed 's/^/    /')
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.backends"

[tool.hatch.build.targets.wheel]
packages = ["src/$PKG_NAME"]

[tool.ruff]
target-version = "py311"
line-length = 100
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "PT", "RUF"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
plugins = []

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --tb=short --strict-markers"

[tool.bandit]
exclude_dirs = ["tests"]
TOMLEOF

# ---- .gitignore ----
cat > ".gitignore" << 'GITEOF'
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
.env
.env.local
.mypy_cache/
.pytest_cache/
.ruff_cache/
.coverage
.coverage-report/
htmlcov/
*.egg
.DS_Store
GITEOF

# ---- .env.example ----
cat > ".env.example" << 'ENVEOF'
APP_NAME=myapp
DEBUG=false
LOG_LEVEL=INFO
ENVEOF

# ---- README.md ----
cat > "README.md" << READMEEOF
# $PROJECT_NAME

TODO: 项目描述

## 开发环境

\`\`\`bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
\`\`\`

## 运行测试

\`\`\`bash
pytest
pytest --cov  # 带覆盖率
\`\`\`

## 代码质量

\`\`\`bash
ruff check .          # 代码检查
ruff format .         # 格式化
mypy .                # 类型检查
bandit -r src/        # 安全扫描
\`\`\`
READMEEOF

cd - > /dev/null

echo ""
echo "✅ 项目 $PROJECT_NAME 创建完成!"
echo ""
echo "📁 目录结构:"
find "$PROJECT_NAME" -type f | sort | head -30 | sed 's/^/  /'
echo ""
echo "📋 下一步:"
echo "  cd $PROJECT_NAME"
echo "  python -m venv .venv"
echo "  source .venv/bin/activate"
echo "  pip install -e '.[dev]'"
