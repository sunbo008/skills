#!/bin/bash
# 检测Python项目技术栈
# 用法: bash detect-stack.sh [project-path]

set -euo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  Python 项目技术栈检测"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
echo "========================================="
echo ""

# ---- Python版本 ----
echo "🐍 【Python环境】"
if command -v python3 &>/dev/null; then
  echo "  ✅ Python $(python3 --version 2>&1 | cut -d' ' -f2)"
else
  echo "  ⚠️  未检测到Python3"
fi

if [ -f "$PROJECT_DIR/.python-version" ]; then
  echo "  📌 .python-version: $(cat "$PROJECT_DIR/.python-version")"
fi

# ---- 包管理 ----
echo ""
echo "📦 【包管理器】"
if [ -f "$PROJECT_DIR/poetry.lock" ]; then
  echo "  ✅ Poetry"
elif [ -f "$PROJECT_DIR/Pipfile.lock" ]; then
  echo "  ✅ Pipenv"
elif [ -f "$PROJECT_DIR/uv.lock" ]; then
  echo "  ✅ uv"
elif [ -f "$PROJECT_DIR/pdm.lock" ]; then
  echo "  ✅ PDM"
elif [ -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "  ✅ pip (requirements.txt)"
fi

if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
  echo "  ✅ pyproject.toml 存在"
fi

# ---- 检测依赖的辅助函数 ----
check_dep() {
  local dep="$1"
  local display="$2"
  local found=0

  for file in "$PROJECT_DIR/pyproject.toml" "$PROJECT_DIR/requirements.txt" "$PROJECT_DIR/Pipfile" "$PROJECT_DIR/setup.cfg" "$PROJECT_DIR/setup.py"; do
    if [ -f "$file" ] && grep -qiE "(^|[^a-z0-9_-])${dep}([^a-z0-9_-]|$)" "$file" 2>/dev/null; then
      found=1
      break
    fi
  done

  if [ "$found" -eq 1 ]; then
    echo "  ✅ $display"
    return 0
  fi
  return 1
}

# ---- Web框架 ----
echo ""
echo "🌐 【Web框架】"
check_dep "fastapi" "FastAPI" || true
check_dep "django" "Django" || true
check_dep "flask" "Flask" || true
check_dep "starlette" "Starlette" || true
check_dep "litestar" "Litestar" || true
check_dep "sanic" "Sanic" || true

# ---- 数据库/ORM ----
echo ""
echo "🗄️ 【数据库/ORM】"
check_dep "sqlalchemy" "SQLAlchemy" || true
check_dep "sqlmodel" "SQLModel" || true
check_dep "tortoise-orm" "Tortoise ORM" || true
check_dep "peewee" "Peewee" || true
check_dep "alembic" "Alembic (迁移)" || true
check_dep "psycopg" "PostgreSQL (psycopg)" || true
check_dep "asyncpg" "PostgreSQL (asyncpg)" || true
check_dep "pymysql" "MySQL" || true
check_dep "aiomysql" "MySQL (async)" || true
check_dep "pymongo" "MongoDB" || true
check_dep "motor" "MongoDB (async)" || true
check_dep "redis" "Redis" || true
check_dep "aioredis" "Redis (async)" || true

# ---- 数据处理 ----
echo ""
echo "📊 【数据处理】"
check_dep "pandas" "Pandas" || true
check_dep "polars" "Polars" || true
check_dep "numpy" "NumPy" || true
check_dep "scipy" "SciPy" || true
check_dep "dask" "Dask" || true
check_dep "pyspark" "PySpark" || true
check_dep "apache-airflow" "Airflow" || check_dep "airflow" "Airflow" || true
# apache-airflow 和 airflow 是同一个包的不同写法，用 || 链是正确的

# ---- ML/AI ----
echo ""
echo "🤖 【ML/AI】"
check_dep "scikit-learn" "scikit-learn" || true
check_dep "torch" "PyTorch" || check_dep "pytorch" "PyTorch" || true
# torch 和 pytorch 是同一个包的不同写法，用 || 链是正确的
check_dep "tensorflow" "TensorFlow" || true
check_dep "transformers" "HuggingFace Transformers" || true
check_dep "langchain" "LangChain" || true
check_dep "openai" "OpenAI SDK" || true

# ---- CLI ----
echo ""
echo "⌨️ 【CLI框架】"
check_dep "typer" "Typer" || true
check_dep "click" "Click" || true
check_dep "rich" "Rich (终端美化)" || true

# ---- HTTP客户端 ----
echo ""
echo "🔗 【HTTP客户端】"
check_dep "httpx" "httpx" || true
check_dep "requests" "requests" || true
check_dep "aiohttp" "aiohttp" || true

# ---- 数据验证 ----
echo ""
echo "✅ 【数据验证/序列化】"
check_dep "pydantic" "Pydantic" || true
check_dep "marshmallow" "Marshmallow" || true
check_dep "attrs" "attrs" || true
check_dep "msgspec" "msgspec" || true

# ---- 测试 ----
echo ""
echo "🧪 【测试框架】"
check_dep "pytest" "pytest" || true
check_dep "pytest-cov" "pytest-cov (覆盖率)" || true
check_dep "pytest-asyncio" "pytest-asyncio" || true
check_dep "hypothesis" "Hypothesis (属性测试)" || true
check_dep "factory-boy" "factory-boy (测试工厂)" || true
check_dep "faker" "Faker" || true

# ---- 代码质量工具 ----
echo ""
echo "📐 【代码质量】"
check_dep "ruff" "Ruff (linter+formatter)" || true
check_dep "mypy" "mypy (类型检查)" || true
check_dep "pyright" "Pyright (类型检查)" || true
check_dep "bandit" "Bandit (安全扫描)" || true
check_dep "black" "Black (格式化)" || true
check_dep "isort" "isort (导入排序)" || true
check_dep "pre-commit" "pre-commit" || true

# ---- pyproject.toml 配置检查 ----
if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
  echo ""
  echo "⚙️ 【配置检查】"

  if grep -q '\[tool\.mypy\]' "$PROJECT_DIR/pyproject.toml" 2>/dev/null; then
    if grep -q 'strict.*=.*true' "$PROJECT_DIR/pyproject.toml" 2>/dev/null; then
      echo "  ✅ mypy strict模式已启用"
    else
      echo "  ⚠️  mypy 未启用 strict 模式"
    fi
  else
    echo "  ⚠️  未配置 mypy"
  fi

  if grep -q '\[tool\.ruff\]' "$PROJECT_DIR/pyproject.toml" 2>/dev/null; then
    echo "  ✅ ruff 已配置"
  else
    echo "  ⚠️  未配置 ruff"
  fi

  if grep -q '\[tool\.pytest' "$PROJECT_DIR/pyproject.toml" 2>/dev/null; then
    echo "  ✅ pytest 已配置"
  fi
fi

# ---- 项目结构 ----
echo ""
echo "📁 【项目结构】"

if [ -d "$PROJECT_DIR/src" ]; then
  echo "  ✅ src layout"
elif ls "$PROJECT_DIR"/*/__init__.py &>/dev/null 2>&1; then
  echo "  ⚠️  flat layout (建议迁移到 src layout)"
fi

count_py() {
  find "$PROJECT_DIR" -name "*.py" -not -path "*/\.*" -not -path "*/__pycache__/*" \
    -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" \
    2>/dev/null | wc -l | tr -d ' '
}

count_tests() {
  find "$PROJECT_DIR" -name "test_*.py" -o -name "*_test.py" 2>/dev/null \
    | grep -v __pycache__ | grep -v venv | wc -l | tr -d ' '
}

echo "  📄 Python文件: $(count_py)"
echo "  🧪 测试文件: $(count_tests)"

[ -f "$PROJECT_DIR/Dockerfile" ] && echo "  🐳 Dockerfile 存在" || true
[ -d "$PROJECT_DIR/.github/workflows" ] && echo "  🔄 GitHub Actions 存在" || true

echo ""
echo "========================================="
echo "  检测完成"
echo "========================================="
