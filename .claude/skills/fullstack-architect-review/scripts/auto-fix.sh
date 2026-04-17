#!/bin/bash
# 自动修复可修复的代码问题
# 用法: bash auto-fix.sh [project-path] [--dry-run]

set -uo pipefail

PROJECT_DIR="${1:-.}"
DRY_RUN=false
if [ "${2:-}" = "--dry-run" ]; then
  DRY_RUN=true
fi

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  自动修复"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
if $DRY_RUN; then
  echo "  模式: DRY RUN (仅预览,不修改文件)"
fi
echo "========================================="
echo ""

ORIG_DIR="$(pwd)"
cd "$PROJECT_DIR"

# Warn if working tree is dirty
if ! $DRY_RUN && git rev-parse --is-inside-work-tree &> /dev/null; then
  if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    echo "[⚠ 警告] 检测到未提交的更改。建议先运行 git commit 或 git stash 再执行自动修复。"
    echo "  继续执行将直接修改工作区文件,可通过 git checkout/restore 回退。"
    echo ""
  fi
fi

# 检测包管理器
RUN_CMD=()
if [ -f "pnpm-lock.yaml" ]; then
  RUN_CMD=("pnpm" "exec")
elif [ -f "yarn.lock" ]; then
  RUN_CMD=("yarn")
elif [ -f "bun.lockb" ] || [ -f "bun.lock" ]; then
  RUN_CMD=("bunx")
else
  RUN_CMD=("npx")
fi

FIXED=0

# ---- 1. ESLint自动修复 ----
HAS_ESLINT=false
for cfg in .eslintrc .eslintrc.js .eslintrc.json .eslintrc.cjs \
           eslint.config.js eslint.config.mjs eslint.config.cjs eslint.config.ts; do
  if [ -f "$cfg" ]; then
    HAS_ESLINT=true
    break
  fi
done

HAS_BIOME=false
if [ -f "biome.json" ] || [ -f "biome.jsonc" ]; then
  HAS_BIOME=true
fi

if $HAS_ESLINT && $HAS_BIOME; then
  echo "[⚠ 警告] 同时检测到 ESLint 和 Biome 配置,仅执行 Biome(优先)以避免冲突。"
  echo "  如需 ESLint,请移除 biome.json 后重新执行。"
  echo ""
fi

if $HAS_BIOME; then
  echo "[Biome] 自动修复..."
  if $DRY_RUN; then
    echo "  (dry-run) 将执行: ${RUN_CMD[*]} biome check --fix ."
  else
    if "${RUN_CMD[@]}" biome check --fix . 2>&1; then
      echo "  [OK] Biome修复完成"
    else
      echo "  [!] Biome修复完成(部分问题需手动修复)"
    fi
    FIXED=$((FIXED + 1))
  fi
  echo ""
elif $HAS_ESLINT; then
  echo "[ESLint] 自动修复..."
  if $DRY_RUN; then
    echo "  (dry-run) 将执行: ${RUN_CMD[*]} eslint . --fix"
  else
    if "${RUN_CMD[@]}" eslint . --fix --max-warnings=999 2>&1; then
      echo "  [OK] ESLint修复完成"
    else
      echo "  [!] ESLint修复完成(部分问题需手动修复)"
    fi
    FIXED=$((FIXED + 1))
  fi
  echo ""
fi

# ---- 2. Prettier格式化 ----
HAS_PRETTIER=false
for cfg in .prettierrc .prettierrc.js .prettierrc.json .prettierrc.cjs \
           prettier.config.js prettier.config.mjs prettier.config.cjs; do
  if [ -f "$cfg" ]; then
    HAS_PRETTIER=true
    break
  fi
done

if $HAS_PRETTIER; then
  echo "[Prettier] 格式化代码..."
  PRETTIER_GLOBS=()
  for dir in src app pages components lib; do
    if [ -d "$dir" ]; then
      PRETTIER_GLOBS+=("$dir/**/*.{ts,tsx,js,jsx,vue,css,scss,json}")
    fi
  done

  if [ ${#PRETTIER_GLOBS[@]} -gt 0 ]; then
    if $DRY_RUN; then
      echo "  (dry-run) 将执行: ${RUN_CMD[*]} prettier --write ${PRETTIER_GLOBS[*]}"
    else
      if "${RUN_CMD[@]}" prettier --write "${PRETTIER_GLOBS[@]}" 2>&1; then
        echo "  [OK] Prettier格式化完成"
      else
        echo "  [!] Prettier格式化完成(部分文件可能未覆盖)"
      fi
      FIXED=$((FIXED + 1))
    fi
  fi
  echo ""
fi

# ---- 3. Python格式化 (Ruff) ----
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  if command -v ruff &> /dev/null; then
    echo "[Ruff] Python代码格式化+修复..."
    if $DRY_RUN; then
      echo "  (dry-run) 将执行: ruff check --fix . && ruff format ."
    else
      ruff check --fix . 2>&1 || true
      ruff format . 2>&1 || true
      echo "  [OK] Ruff修复完成"
      FIXED=$((FIXED + 1))
    fi
    echo ""
  fi
fi

# ---- 4. console.log 检测 ----
echo "[console.log] 检查残留的调试日志..."
CONSOLE_LOGS=$(grep -rn "console\.log" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  2>/dev/null | grep -v "node_modules" | grep -v ".next" | grep -v "dist" \
  | grep -v "eslint" | grep -v "prettier" | grep -v "jest" | grep -v "vitest" \
  | grep -v "__tests__" | grep -v ".test." | grep -v ".spec." || true)

if [ -n "$CONSOLE_LOGS" ]; then
  echo "  [!] 以下文件包含console.log(建议手动移除或替换为logger):"
  echo "$CONSOLE_LOGS" | head -20 | sed 's/^/    /'
  COUNT=$(echo "$CONSOLE_LOGS" | wc -l | tr -d ' ')
  echo "  共 $COUNT 处"
else
  echo "  [OK] 未发现残留console.log"
fi
echo ""

# ---- 5. 依赖更新检查 ----
echo "[依赖更新] 检查可更新的依赖..."
if [ -f "package.json" ]; then
  if [ -f "pnpm-lock.yaml" ]; then
    pnpm outdated 2>&1 | head -30 || true
  elif [ -f "yarn.lock" ]; then
    yarn outdated 2>&1 | head -30 || true
  else
    npm outdated 2>&1 | head -30 || true
  fi
fi
echo ""

cd "$ORIG_DIR"

# ---- 汇总 ----
echo "========================================="
echo "  自动修复完成"
echo "========================================="
echo "  执行了 $FIXED 项自动修复"
if ! $DRY_RUN; then
  echo "  请检查 git diff 确认修复内容"
fi
echo "  部分问题需要手动修复,请参考审查报告"
echo ""
