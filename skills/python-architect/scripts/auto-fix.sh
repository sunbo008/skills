#!/bin/bash
# 自动修复Python代码问题
# 用法: bash auto-fix.sh [project-path]

set -uo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  Python 自动修复"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
echo "========================================="
echo ""

cd "$PROJECT_DIR"

FIXED=0

# ---- 1. Ruff自动修复 ----
if command -v ruff &>/dev/null; then
  echo "🔧 [Ruff Lint] 自动修复..."
  ruff check . --fix 2>&1
  FIXED=$((FIXED + 1))
  echo ""

  echo "🔧 [Ruff Format] 格式化代码..."
  ruff format . 2>&1
  FIXED=$((FIXED + 1))
  echo ""
else
  echo "⏭️  ruff 未安装，跳过"
  echo ""
fi

# ---- 2. isort (如果ruff没覆盖) ----
if command -v isort &>/dev/null && ! command -v ruff &>/dev/null; then
  echo "🔧 [isort] 排序导入..."
  isort . 2>&1
  FIXED=$((FIXED + 1))
  echo ""
fi

# ---- 3. 列出残留print() ----
echo "🔍 [print()] 检查残留的 print 语句..."
PRINTS=$(grep -rn "print(" . --include="*.py" 2>/dev/null \
  | grep -v "venv/" | grep -v ".venv/" | grep -v "__pycache__" \
  | grep -v "test_" | grep -v "_test.py" | grep -v "conftest" \
  | grep -v "cli" | grep -v "scripts/")

if [ -n "$PRINTS" ]; then
  echo "  ⚠️  以下文件包含 print() (建议替换为 logging):"
  echo "$PRINTS" | head -15 | sed 's/^/    /'
  COUNT=$(echo "$PRINTS" | wc -l | tr -d ' ')
  echo "  📊 共 $COUNT 处"
else
  echo "  ✅ 未发现残留 print()"
fi
echo ""

# ---- 4. 依赖更新检查 ----
echo "📦 [依赖更新] 检查过时依赖..."
if command -v pip &>/dev/null; then
  pip list --outdated --format=columns 2>/dev/null | head -20 || true
fi
echo ""

cd - > /dev/null

echo "========================================="
echo "  自动修复完成"
echo "========================================="
echo "  🔧 执行了 $FIXED 项自动修复"
echo "  💡 请检查 git diff 确认修复内容"
