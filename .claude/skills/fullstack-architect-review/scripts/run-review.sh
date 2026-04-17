#!/bin/bash
# 全量自动化代码审查
# 用法: bash run-review.sh [project-path]

set -uo pipefail

PROJECT_DIR="${1:-.}"
REPORT_DIR="$PROJECT_DIR/.review-report"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: 目录不存在: $PROJECT_DIR"
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
  shift
  local output_file="$REPORT_DIR/${name}_${TIMESTAMP}.txt"

  echo "--------------------------------------------"
  echo "  [$name]"
  echo "--------------------------------------------"

  if "$@" > "$output_file" 2>&1; then
    echo "  [OK] 通过"
  else
    echo "  [!] 发现问题"
    echo "  报告: $output_file"
    head -20 "$output_file" | sed 's/^/  | /'
    local line_count
    line_count=$(wc -l < "$output_file" | tr -d ' ')
    if [ "$line_count" -gt 20 ]; then
      echo "  | ... (共 $line_count 行,查看完整报告)"
    fi
    WARNINGS=$((WARNINGS + 1))
  fi
  echo ""
}

# ---- 1. Node.js工具链检查 ----
if [ -f "$PROJECT_DIR/package.json" ]; then
  ORIG_DIR="$(pwd)"

  cd "$PROJECT_DIR"

  # 检测包管理器
  if [ -f "pnpm-lock.yaml" ]; then
    RUN_CMD=("pnpm" "exec")
  elif [ -f "yarn.lock" ]; then
    RUN_CMD=("yarn")
  elif [ -f "bun.lockb" ] || [ -f "bun.lock" ]; then
    RUN_CMD=("bunx")
  else
    RUN_CMD=("npx")
  fi

  # ESLint (支持 flat config 全部变体)
  HAS_ESLINT=false
  for cfg in .eslintrc .eslintrc.js .eslintrc.json .eslintrc.cjs \
             eslint.config.js eslint.config.mjs eslint.config.cjs eslint.config.ts; do
    if [ -f "$cfg" ]; then
      HAS_ESLINT=true
      break
    fi
  done

  # Biome 检测
  HAS_BIOME=false
  if [ -f "biome.json" ] || [ -f "biome.jsonc" ]; then
    HAS_BIOME=true
  fi

  if $HAS_ESLINT; then
    run_check "ESLint" "${RUN_CMD[@]}" eslint . --max-warnings=0 --format=compact
  elif $HAS_BIOME; then
    run_check "Biome" "${RUN_CMD[@]}" biome check .
  else
    echo "  [SKIP] ESLint/Biome 未检测到配置"
    echo ""
  fi

  # TypeScript
  if [ -f "tsconfig.json" ]; then
    run_check "TypeScript" "${RUN_CMD[@]}" tsc --noEmit
  else
    echo "  [SKIP] TypeScript 未检测到 tsconfig.json"
    echo ""
  fi

  # Prettier格式检查 -- 自动发现源码目录
  HAS_PRETTIER=false
  for cfg in .prettierrc .prettierrc.js .prettierrc.json .prettierrc.cjs \
             prettier.config.js prettier.config.mjs prettier.config.cjs; do
    if [ -f "$cfg" ]; then
      HAS_PRETTIER=true
      break
    fi
  done

  if $HAS_PRETTIER; then
    PRETTIER_GLOBS=()
    for dir in src app pages components lib; do
      if [ -d "$dir" ]; then
        PRETTIER_GLOBS+=("$dir/**/*.{ts,tsx,js,jsx,vue}")
      fi
    done
    if [ ${#PRETTIER_GLOBS[@]} -gt 0 ]; then
      run_check "Prettier" "${RUN_CMD[@]}" prettier --check "${PRETTIER_GLOBS[@]}"
    fi
  fi

  cd "$ORIG_DIR"
fi

# ---- 2. 安全扫描 ----
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
run_check "依赖安全审计" bash "$SCRIPT_DIR/security-audit.sh" "$PROJECT_DIR"

# ---- 3. 代码异味检测 ----
echo "--------------------------------------------"
echo "  [代码异味检测]"
echo "--------------------------------------------"

SMELL_FILE="$REPORT_DIR/code-smells_${TIMESTAMP}.txt"
> "$SMELL_FILE"

# Build a list of existing source directories to search (array for space-safe paths)
SEARCH_DIRS=()
for dir in src app pages components lib utils server api; do
  if [ -d "$PROJECT_DIR/$dir" ]; then
    SEARCH_DIRS+=("$PROJECT_DIR/$dir")
  fi
done

check_pattern() {
  local pattern="$1"
  local description="$2"
  local severity="$3"

  if [ ${#SEARCH_DIRS[@]} -eq 0 ]; then
    return
  fi

  local file_count
  file_count=$(grep -Erl "$pattern" "${SEARCH_DIRS[@]}" \
    --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
    --include="*.py" --include="*.go" --include="*.vue" \
    2>/dev/null | grep -v "node_modules" | grep -v ".next" | grep -v "dist" \
    | wc -l | tr -d ' ')

  if [ "$file_count" -gt 0 ]; then
    local match_count
    match_count=$(grep -Ern "$pattern" "${SEARCH_DIRS[@]}" \
      --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
      --include="*.py" --include="*.go" --include="*.vue" \
      2>/dev/null | grep -v "node_modules" | grep -v ".next" | grep -v "dist" \
      | wc -l | tr -d ' ')
    echo "  $severity $description: $match_count 处 ($file_count 文件)" | tee -a "$SMELL_FILE"
    if [ "$severity" = "[P0]" ]; then
      ERRORS=$((ERRORS + file_count))
    else
      WARNINGS=$((WARNINGS + file_count))
    fi
  fi
}

check_pattern "as any" "使用 'as any' 类型断言" "[P1]"
check_pattern "@ts-ignore" "使用 @ts-ignore" "[P1]"
check_pattern "dangerouslySetInnerHTML" "使用 dangerouslySetInnerHTML" "[P0]"
check_pattern "v-html" "使用 v-html (Vue XSS风险)" "[P0]"
check_pattern "innerHTML" "直接操作 innerHTML" "[P0]"
check_pattern "eval(" "使用 eval()" "[P0]"
check_pattern "new Function(" "使用 new Function()" "[P0]"
check_pattern "document\.write" "使用 document.write" "[P0]"
check_pattern 'localStorage\.(set|get)Item' "使用 localStorage (检查是否存储敏感数据)" "[P1]"
check_pattern "console\.log" "残留 console.log" "[P2]"
check_pattern "TODO|FIXME|HACK|XXX" "TODO/FIXME/HACK标记" "[P2]"
check_pattern 'password.*=.*['"'"'"]' "疑似硬编码密码" "[P0]"
check_pattern 'secret.*=.*['"'"'"]' "疑似硬编码密钥" "[P0]"
check_pattern 'api[_-]*key.*=.*['"'"'"]' "疑似硬编码API Key" "[P0]"
check_pattern "SELECT \*" "使用 SELECT *" "[P1]"
check_pattern 'queryRawUnsafe|queryRaw\b|\$queryRaw' "使用原始SQL查询" "[P1]"
check_pattern "!important" "使用CSS !important" "[P2]"

if [ -s "$SMELL_FILE" ]; then
  echo "  报告: $SMELL_FILE"
else
  echo "  [OK] 未发现明显代码异味"
fi
echo ""

# ---- 4. 文件大小检测 ----
echo "--------------------------------------------"
echo "  [过大文件检测 (>300行)]"
echo "--------------------------------------------"

find "$PROJECT_DIR" -type f \( \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
  -o -name "*.py" -o -name "*.go" -o -name "*.vue" \
\) -not -path "*/node_modules/*" -not -path "*/.next/*" \
   -not -path "*/dist/*" -not -path "*/.git/*" \
   -not -path "*/.venv/*" -not -path "*/venv/*" \
   -not -path "*/__pycache__/*" \
   -not -name "*.test.*" -not -name "*.spec.*" \
   -not -name "*.generated.*" -not -name "*.min.*" \
| while read -r file; do
  lines=$(wc -l < "$file" | tr -d ' ')
  if [ "$lines" -gt 300 ]; then
    echo "  (!) $file ($lines 行)"
  fi
done

echo ""

# ---- 汇总 ----
echo "========================================="
echo "  审查汇总"
echo "========================================="
echo "  [P0] 严重问题(按文件计): $ERRORS"
echo "  [P1/P2] 警告(按文件计): $WARNINGS"
echo "  报告目录: $REPORT_DIR"
echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "  [FAIL] 发现严重问题,需要修复后再部署"
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo "  [WARN] 存在警告,建议修复"
  exit 0
else
  echo "  [PASS] 所有检查通过"
  exit 0
fi
