#!/bin/bash
# 全量自动化代码审查
# 用法: bash run-review.sh [project-path]
# 运行ESLint、TypeScript检查、安全扫描、依赖审计

set -uo pipefail

PROJECT_DIR="${1:-.}"
REPORT_DIR="$PROJECT_DIR/.review-report"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

mkdir -p "$REPORT_DIR"

echo "========================================="
echo "  全量自动化代码审查"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
echo "  时间: $(date)"
echo "========================================="
echo ""

ERRORS=0
WARNINGS=0

run_check() {
  local name="$1"
  local cmd="$2"
  local output_file="$REPORT_DIR/${name}_${TIMESTAMP}.txt"

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔍 [$name]"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if eval "$cmd" > "$output_file" 2>&1; then
    echo "  ✅ 通过"
  else
    local exit_code=$?
    echo "  ⚠️  发现问题 (exit code: $exit_code)"
    echo "  📄 详细报告: $output_file"
    head -20 "$output_file" | sed 's/^/  │ /'
    local line_count
    line_count=$(wc -l < "$output_file" | tr -d ' ')
    if [ "$line_count" -gt 20 ]; then
      echo "  │ ... (共 $line_count 行,查看完整报告)"
    fi
    WARNINGS=$((WARNINGS + 1))
  fi
  echo ""
}

# ---- 1. ESLint检查 ----
if [ -f "$PROJECT_DIR/package.json" ]; then
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

  # ESLint
  if [ -f ".eslintrc" ] || [ -f ".eslintrc.js" ] || [ -f ".eslintrc.json" ] || [ -f ".eslintrc.cjs" ] || [ -f "eslint.config.js" ] || [ -f "eslint.config.mjs" ] || [ -f "eslint.config.ts" ]; then
    run_check "ESLint" "$RUN_CMD eslint . --max-warnings=0 --format=compact 2>&1 || true"
  else
    echo "⏭️  [ESLint] 未检测到ESLint配置,跳过"
    echo ""
  fi

  # TypeScript
  if [ -f "tsconfig.json" ]; then
    run_check "TypeScript" "$RUN_CMD tsc --noEmit 2>&1 || true"
  else
    echo "⏭️  [TypeScript] 未检测到tsconfig.json,跳过"
    echo ""
  fi

  # Prettier格式检查
  if [ -f ".prettierrc" ] || [ -f ".prettierrc.js" ] || [ -f ".prettierrc.json" ] || [ -f "prettier.config.js" ] || [ -f "prettier.config.mjs" ]; then
    run_check "Prettier" "$RUN_CMD prettier --check 'src/**/*.{ts,tsx,js,jsx}' 2>&1 || true"
  fi

  cd - > /dev/null
fi

# ---- 2. 安全扫描 ----
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
run_check "依赖安全审计" "bash '$SCRIPT_DIR/security-audit.sh' '$PROJECT_DIR' 2>&1 || true"

# ---- 3. 代码异味检测 ----
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 [代码异味检测]"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

SMELL_FILE="$REPORT_DIR/code-smells_${TIMESTAMP}.txt"
> "$SMELL_FILE"

check_pattern() {
  local pattern="$1"
  local description="$2"
  local severity="$3"
  local count

  count=$(grep -rn "$pattern" "$PROJECT_DIR/src" "$PROJECT_DIR/app" "$PROJECT_DIR/pages" "$PROJECT_DIR/components" "$PROJECT_DIR/lib" "$PROJECT_DIR/utils" "$PROJECT_DIR/server" "$PROJECT_DIR/api" \
    --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" --include="*.py" --include="*.go" \
    2>/dev/null | grep -v "node_modules" | grep -v ".next" | grep -v "dist" | wc -l | tr -d ' ')

  if [ "$count" -gt 0 ]; then
    echo "  $severity $description: $count 处" | tee -a "$SMELL_FILE"
    if [ "$severity" = "🔴" ]; then
      ERRORS=$((ERRORS + count))
    else
      WARNINGS=$((WARNINGS + count))
    fi
  fi
}

check_pattern "as any" "使用 'as any' 类型断言" "🟡"
check_pattern "@ts-ignore" "使用 @ts-ignore" "🟡"
check_pattern "@ts-expect-error" "使用 @ts-expect-error" "🟡"
check_pattern "dangerouslySetInnerHTML" "使用 dangerouslySetInnerHTML" "🔴"
check_pattern "innerHTML" "直接操作 innerHTML" "🔴"
check_pattern "eval(" "使用 eval()" "🔴"
check_pattern "document\.write" "使用 document.write" "🔴"
check_pattern "localStorage\.\(set\|get\)Item.*token" "Token存储在localStorage" "🔴"
check_pattern "console\.log" "残留 console.log" "🟡"
check_pattern "TODO\|FIXME\|HACK\|XXX" "TODO/FIXME/HACK标记" "🟡"
check_pattern "password.*=.*['\"]" "硬编码密码" "🔴"
check_pattern "secret.*=.*['\"]" "硬编码密钥" "🔴"
check_pattern "api[_-]*key.*=.*['\"]" "硬编码API Key" "🔴"
check_pattern "SELECT \*" "使用 SELECT *" "🟡"
check_pattern "queryRawUnsafe\|queryRaw\b" "使用原始SQL查询" "🟡"
check_pattern "!important" "使用CSS !important" "🟡"

if [ -s "$SMELL_FILE" ]; then
  echo "  📄 详细报告: $SMELL_FILE"
else
  echo "  ✅ 未发现明显代码异味"
fi
echo ""

# ---- 4. 文件大小检测 ----
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 [过大文件检测 (>300行)]"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LARGE_FILES=$(find "$PROJECT_DIR" \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" \
  | grep -v "node_modules" | grep -v ".next" | grep -v "dist" | grep -v ".git" \
  | while read -r file; do
    lines=$(wc -l < "$file" | tr -d ' ')
    if [ "$lines" -gt 300 ]; then
      echo "  ⚠️  $file ($lines 行)"
    fi
  done)

if [ -n "$LARGE_FILES" ]; then
  echo "$LARGE_FILES"
  WARNINGS=$((WARNINGS + $(echo "$LARGE_FILES" | wc -l | tr -d ' ')))
else
  echo "  ✅ 无过大文件"
fi
echo ""

# ---- 汇总 ----
echo "========================================="
echo "  审查汇总"
echo "========================================="
echo "  🔴 严重问题: $ERRORS"
echo "  🟡 警告: $WARNINGS"
echo "  📁 报告目录: $REPORT_DIR"
echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "  ❌ 发现严重问题,需要修复后再部署"
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo "  ⚠️  存在警告,建议修复"
  exit 0
else
  echo "  ✅ 所有检查通过"
  exit 0
fi
