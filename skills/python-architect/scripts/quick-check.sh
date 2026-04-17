#!/bin/bash
# 快速增量检查（开发过程中频繁使用）
# 用法: bash quick-check.sh [project-path]

set -uo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

cd "$PROJECT_DIR"

echo "⚡ 快速检查..."
echo ""

EXIT=0

# Ruff lint + format
if command -v ruff &>/dev/null; then
  echo "📐 [ruff check]"
  ruff check . 2>&1 || EXIT=1
  echo ""
  echo "📐 [ruff format check]"
  ruff format --check . 2>&1 || EXIT=1
  echo ""
fi

# mypy
if command -v mypy &>/dev/null; then
  echo "🔍 [mypy]"
  mypy . --ignore-missing-imports 2>&1 || EXIT=1
  echo ""
fi

# 快速测试（仅上次失败的 + 本次修改的）
if command -v pytest &>/dev/null; then
  echo "🧪 [pytest --lf -x]"
  pytest --lf -x -q --tb=short 2>&1 || EXIT=1
  echo ""
fi

if [ "$EXIT" -eq 0 ]; then
  echo "✅ 快速检查通过"
else
  echo "⚠️  发现问题，请修复"
fi

cd - > /dev/null
exit $EXIT
