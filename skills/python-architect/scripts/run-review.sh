#!/bin/bash
# 全量Python代码审查
# 用法: bash run-review.sh [project-path]
# 运行 ruff + mypy + bandit + 代码异味检测

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
echo "  Python 全量代码审查"
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

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔍 [$name]"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  if "$@" > "$output_file" 2>&1; then
    echo "  ✅ 通过"
  else
    echo "  ⚠️  发现问题"
    echo "  📄 详细报告: $output_file"
    head -20 "$output_file" | sed 's/^/  │ /'
    local line_count
    line_count=$(wc -l < "$output_file" | tr -d ' ')
    if [ "$line_count" -gt 20 ]; then
      echo "  │ ... (共 $line_count 行)"
    fi
    WARNINGS=$((WARNINGS + 1))
  fi
  echo ""
}

cd "$PROJECT_DIR"

# ---- 1. Ruff (Linter + Formatter检查) ----
if command -v ruff &>/dev/null; then
  run_check "Ruff-Lint" ruff check . --output-format=concise
  run_check "Ruff-Format" ruff format --check .
elif [ -f "pyproject.toml" ] && grep -q "ruff" "pyproject.toml" 2>/dev/null; then
  echo "⚠️  ruff 在依赖中但未安装: pip install ruff"
  echo ""
else
  echo "⏭️  [Ruff] 未安装，跳过 (推荐安装: pip install ruff)"
  echo ""
fi

# ---- 2. mypy (类型检查) ----
if command -v mypy &>/dev/null; then
  run_check "mypy" mypy . --ignore-missing-imports
elif [ -f "pyproject.toml" ] && grep -q "mypy" "pyproject.toml" 2>/dev/null; then
  echo "⚠️  mypy 在依赖中但未安装: pip install mypy"
  echo ""
else
  echo "⏭️  [mypy] 未安装，跳过 (推荐安装: pip install mypy)"
  echo ""
fi

# ---- 3. Bandit (安全扫描) ----
if command -v bandit &>/dev/null; then
  run_check "Bandit" bandit -r . -x ./tests,./venv,./.venv --format txt
else
  echo "⏭️  [Bandit] 未安装，跳过 (推荐安装: pip install bandit)"
  echo ""
fi

# ---- 4. 代码异味检测 ----
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

  count=$(grep -rn "$pattern" . \
    --include="*.py" \
    2>/dev/null | grep -v "venv/" | grep -v ".venv/" | grep -v "__pycache__" \
    | grep -v "test_" | grep -v "_test.py" | grep -v "conftest" \
    | wc -l | tr -d ' ')

  if [ "$count" -gt 0 ]; then
    echo "  $severity $description: $count 处" | tee -a "$SMELL_FILE"
    if [ "$severity" = "🔴" ]; then
      ERRORS=$((ERRORS + count))
    else
      WARNINGS=$((WARNINGS + count))
    fi
  fi
}

check_pattern "eval(" "使用 eval()" "🔴"
check_pattern "exec(" "使用 exec()" "🔴"
check_pattern "pickle\.loads" "pickle.loads (反序列化风险)" "🔴"
check_pattern "os\.system(" "使用 os.system()" "🔴"
check_pattern "shell=True" "subprocess shell=True" "🔴"
check_pattern "except:" "bare except" "🔴"
check_pattern "except Exception:" "过宽异常捕获" "🟡"
check_pattern ": Any" "使用 Any 类型" "🟡"
check_pattern "# type: ignore$" "type: ignore 无注释" "🟡"
check_pattern "# TODO\|# FIXME\|# HACK\|# XXX" "TODO/FIXME标记" "🟡"
check_pattern "print(" "残留 print()" "🟡"
check_pattern "password.*=.*['\"]" "硬编码密码" "🔴"
check_pattern "secret.*=.*['\"]" "硬编码密钥" "🔴"
check_pattern "api_key.*=.*['\"]" "硬编码API Key" "🔴"
check_pattern "SELECT \*" "SQL SELECT *" "🟡"
check_pattern "\.format(" "str.format (考虑f-string)" "🟢"

if [ -s "$SMELL_FILE" ]; then
  echo "  📄 详细报告: $SMELL_FILE"
else
  echo "  ✅ 未发现明显代码异味"
fi
echo ""

# ---- 5. 大文件检测 ----
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 [过大文件检测 (>300行)]"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LARGE_FILES=$(find . -name "*.py" \
  -not -path "./venv/*" -not -path "./.venv/*" -not -path "./__pycache__/*" \
  -not -path "./.git/*" \
  | while read -r file; do
    lines=$(wc -l < "$file" | tr -d ' ')
    if [ "$lines" -gt 300 ]; then
      echo "  ⚠️  $file ($lines 行)"
    fi
  done)

if [ -n "$LARGE_FILES" ]; then
  echo "$LARGE_FILES"
else
  echo "  ✅ 无过大文件"
fi
echo ""

# ---- 6. 类型标注覆盖率估算 ----
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 [类型标注覆盖估算]"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 使用 Python ast 模块准确统计（支持多行函数签名）
TYPE_STATS=$(python3 -c "
import ast, sys, pathlib
total = typed = 0
for p in pathlib.Path('.').rglob('*.py'):
    parts = p.parts
    if any(d in parts for d in ('venv', '.venv', '__pycache__', 'node_modules')):
        continue
    try:
        tree = ast.parse(p.read_text(encoding='utf-8', errors='ignore'))
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total += 1
            if node.returns is not None:
                typed += 1
print(f'{total} {typed}')
" 2>/dev/null) || true

if [ -n "$TYPE_STATS" ]; then
  TOTAL_FUNCS=$(echo "$TYPE_STATS" | awk '{print $1}')
  TYPED_FUNCS=$(echo "$TYPE_STATS" | awk '{print $2}')

  if [ "$TOTAL_FUNCS" -gt 0 ]; then
    PCT=$((TYPED_FUNCS * 100 / TOTAL_FUNCS))
    echo "  函数总数: $TOTAL_FUNCS"
    echo "  有返回类型标注: $TYPED_FUNCS ($PCT%)"
    if [ "$PCT" -lt 50 ]; then
      echo "  🟡 类型标注覆盖率偏低，建议提升到 80%+"
      WARNINGS=$((WARNINGS + 1))
    elif [ "$PCT" -lt 80 ]; then
      echo "  🟢 类型标注覆盖率中等"
    else
      echo "  ✅ 类型标注覆盖率良好"
    fi
  else
    echo "  ⚠️  未找到Python函数"
  fi
else
  echo "  ⚠️  无法运行 Python AST 分析"
fi
echo ""

cd - > /dev/null

# ---- 汇总 ----
echo "========================================="
echo "  审查汇总"
echo "========================================="
echo "  🔴 严重问题: $ERRORS"
echo "  🟡 警告: $WARNINGS"
echo "  📁 报告目录: $REPORT_DIR"
echo ""

if [ "$ERRORS" -gt 0 ]; then
  echo "  ❌ 发现严重问题，需要修复"
  exit 1
elif [ "$WARNINGS" -gt 0 ]; then
  echo "  ⚠️  存在警告，建议修复"
  exit 0
else
  echo "  ✅ 所有检查通过"
  exit 0
fi
