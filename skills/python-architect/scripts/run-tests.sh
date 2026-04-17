#!/bin/bash
# 运行Python测试套件
# 用法: bash run-tests.sh [project-path] [--coverage] [--verbose]

set -uo pipefail

PROJECT_DIR="."
COVERAGE=false
VERBOSE=false

while [ $# -gt 0 ]; do
  case "$1" in
    --coverage) COVERAGE=true ;;
    --verbose) VERBOSE=true ;;
    -*) echo "❌ 未知选项: $1"; exit 1 ;;
    *) PROJECT_DIR="$1" ;;
  esac
  shift
done

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  Python 测试运行"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
echo "========================================="
echo ""

cd "$PROJECT_DIR"

# 检查pytest
if ! command -v pytest &>/dev/null; then
  echo "❌ pytest 未安装"
  echo "💡 安装: pip install pytest pytest-cov pytest-asyncio"
  exit 1
fi

# 构建pytest参数
PYTEST_ARGS=()
PYTEST_ARGS+=("--tb=short")
PYTEST_ARGS+=("--strict-markers")

if [ "$VERBOSE" = true ]; then
  PYTEST_ARGS+=("-v")
fi

if [ "$COVERAGE" = true ]; then
  # 尝试找到包名
  PKG_NAME=""
  if [ -d "src" ]; then
    PKG_NAME=$(ls src/ 2>/dev/null | head -1)
  fi

  if [ -n "$PKG_NAME" ]; then
    PYTEST_ARGS+=("--cov=src/$PKG_NAME" "--cov-report=term-missing" "--cov-report=html:.coverage-report")
  else
    PYTEST_ARGS+=("--cov=." "--cov-report=term-missing" "--cov-report=html:.coverage-report")
  fi
fi

echo "🧪 运行命令: pytest ${PYTEST_ARGS[*]}"
echo ""

pytest "${PYTEST_ARGS[@]}"
EXIT_CODE=$?

echo ""

if [ "$COVERAGE" = true ] && [ -d ".coverage-report" ]; then
  echo "📊 覆盖率报告: .coverage-report/index.html"
fi

if [ "$EXIT_CODE" -eq 0 ]; then
  echo "✅ 所有测试通过"
else
  echo "❌ 测试失败 (exit code: $EXIT_CODE)"
fi

cd - > /dev/null
exit $EXIT_CODE
