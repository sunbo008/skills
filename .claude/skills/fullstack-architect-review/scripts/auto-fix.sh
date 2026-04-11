#!/bin/bash
# 自动修复可修复的代码问题
# 用法: bash auto-fix.sh [project-path]

set -uo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  自动修复"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
echo "========================================="
echo ""

cd "$PROJECT_DIR"

# 检测包管理器
if [ -f "pnpm-lock.yaml" ]; then
  RUN_CMD="pnpm exec"
elif [ -f "yarn.lock" ]; then
  RUN_CMD="yarn"
elif [ -f "bun.lockb" ] || [ -f "bun.lock" ]; then
  RUN_CMD="bunx"
else
  RUN_CMD="npx"
fi

FIXED=0

# ---- 1. ESLint自动修复 ----
if [ -f ".eslintrc" ] || [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f ".eslintrc.cjs" ] || [ -f "eslint.config.js" ] || [ -f "eslint.config.mjs" ] || [ -f "eslint.config.ts" ]; then
  echo "🔧 [ESLint] 自动修复..."
  if $RUN_CMD eslint . --fix --max-warnings=999 2>&1; then
    echo "  ✅ ESLint修复完成"
    FIXED=$((FIXED + 1))
  else
    echo "  ⚠️  ESLint修复完成(部分问题需手动修复)"
    FIXED=$((FIXED + 1))
  fi
  echo ""
fi

# ---- 2. Prettier格式化 ----
if [ -f ".prettierrc" ] || [ -f ".prettierrc.js" ] || [ -f ".prettierrc.json" ] || [ -f "prettier.config.js" ] || [ -f "prettier.config.mjs" ]; then
  echo "🔧 [Prettier] 格式化代码..."
  if $RUN_CMD prettier --write "src/**/*.{ts,tsx,js,jsx,css,scss,json}" 2>&1; then
    echo "  ✅ Prettier格式化完成"
    FIXED=$((FIXED + 1))
  else
    echo "  ⚠️  Prettier格式化完成(部分文件可能未覆盖)"
  fi
  echo ""
fi

# ---- 3. 移除console.log ----
echo "🔧 [console.log] 检查并列出残留的console.log..."
CONSOLE_LOGS=$(grep -rn "console\.log" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  2>/dev/null | grep -v "node_modules" | grep -v ".next" | grep -v "dist" \
  | grep -v "eslint" | grep -v "prettier" | grep -v "jest" | grep -v "vitest" \
  | grep -v "__tests__" | grep -v ".test." | grep -v ".spec.")

if [ -n "$CONSOLE_LOGS" ]; then
  echo "  ⚠️  以下文件包含console.log(建议手动移除或替换为logger):"
  echo "$CONSOLE_LOGS" | head -20 | sed 's/^/    /'
  COUNT=$(echo "$CONSOLE_LOGS" | wc -l | tr -d ' ')
  echo "  📊 共 $COUNT 处"
else
  echo "  ✅ 未发现残留console.log"
fi
echo ""

# ---- 4. 排序imports (如果有插件) ----
if grep -q "simple-import-sort\|import-sort\|sort-imports" "package.json" 2>/dev/null; then
  echo "🔧 [Import排序] 通过ESLint --fix已处理"
  echo ""
fi

# ---- 5. 依赖更新检查 ----
echo "📦 [依赖更新] 检查可更新的依赖..."
if command -v $RUN_CMD &> /dev/null; then
  if [ -f "pnpm-lock.yaml" ]; then
    pnpm outdated 2>&1 | head -30 || true
  elif [ -f "yarn.lock" ]; then
    yarn outdated 2>&1 | head -30 || true
  else
    npm outdated 2>&1 | head -30 || true
  fi
fi
echo ""

cd - > /dev/null

# ---- 汇总 ----
echo "========================================="
echo "  自动修复完成"
echo "========================================="
echo "  🔧 执行了 $FIXED 项自动修复"
echo "  💡 请检查git diff确认修复内容"
echo "  💡 部分问题需要手动修复,请参考审查报告"
echo ""
