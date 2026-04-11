#!/bin/bash
# 依赖安全审计脚本
# 用法: bash security-audit.sh [project-path]

set -uo pipefail

PROJECT_DIR="${1:-.}"

echo "========================================="
echo "  依赖安全审计"
echo "========================================="
echo ""

ISSUES=0

# ---- Node.js依赖审计 ----
if [ -f "$PROJECT_DIR/package.json" ]; then
  echo "📦 【Node.js依赖审计】"

  cd "$PROJECT_DIR"

  if [ -f "pnpm-lock.yaml" ]; then
    echo "  使用 pnpm audit..."
    pnpm audit --no-fix 2>&1 || ISSUES=$((ISSUES + 1))
  elif [ -f "yarn.lock" ]; then
    echo "  使用 yarn audit..."
    yarn audit 2>&1 || ISSUES=$((ISSUES + 1))
  elif [ -f "package-lock.json" ]; then
    echo "  使用 npm audit..."
    npm audit 2>&1 || ISSUES=$((ISSUES + 1))
  else
    echo "  ⚠️  未找到lock文件,无法进行精确审计"
  fi

  cd - > /dev/null
  echo ""
fi

# ---- Python依赖审计 ----
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "🐍 【Python依赖审计】"

  if command -v pip-audit &> /dev/null; then
    echo "  使用 pip-audit..."
    pip-audit -r "$PROJECT_DIR/requirements.txt" 2>&1 || ISSUES=$((ISSUES + 1))
  elif command -v safety &> /dev/null; then
    echo "  使用 safety check..."
    safety check -r "$PROJECT_DIR/requirements.txt" 2>&1 || ISSUES=$((ISSUES + 1))
  else
    echo "  ⚠️  未安装 pip-audit 或 safety,跳过"
    echo "  💡 安装: pip install pip-audit"
  fi
  echo ""
fi

# ---- Go依赖审计 ----
if [ -f "$PROJECT_DIR/go.mod" ]; then
  echo "🔷 【Go依赖审计】"

  if command -v govulncheck &> /dev/null; then
    echo "  使用 govulncheck..."
    cd "$PROJECT_DIR"
    govulncheck ./... 2>&1 || ISSUES=$((ISSUES + 1))
    cd - > /dev/null
  else
    echo "  ⚠️  未安装 govulncheck,跳过"
    echo "  💡 安装: go install golang.org/x/vuln/cmd/govulncheck@latest"
  fi
  echo ""
fi

# ---- .env文件检查 ----
echo "🔐 【敏感文件检查】"

check_sensitive() {
  local file="$1"
  local description="$2"
  if [ -f "$PROJECT_DIR/$file" ]; then
    # 检查是否在.gitignore中
    if [ -f "$PROJECT_DIR/.gitignore" ] && grep -q "^$file$\|^/$file$" "$PROJECT_DIR/.gitignore" 2>/dev/null; then
      echo "  ✅ $file 已在 .gitignore 中"
    else
      echo "  🔴 $file 存在但未在 .gitignore 中! ($description)"
      ISSUES=$((ISSUES + 1))
    fi
  fi
}

check_sensitive ".env" "环境变量文件"
check_sensitive ".env.local" "本地环境变量"
check_sensitive ".env.production" "生产环境变量"
check_sensitive ".env.development" "开发环境变量"

# 检查是否有.env.example
if [ -f "$PROJECT_DIR/.env" ] || [ -f "$PROJECT_DIR/.env.local" ]; then
  if [ ! -f "$PROJECT_DIR/.env.example" ] && [ ! -f "$PROJECT_DIR/.env.template" ]; then
    echo "  🟡 存在.env文件但缺少 .env.example 模板"
  fi
fi
echo ""

# ---- 硬编码密钥检查 ----
echo "🔑 【硬编码密钥检查】"

SECRETS_FOUND=0

search_secrets() {
  local pattern="$1"
  local description="$2"
  local matches

  matches=$(grep -rn "$pattern" "$PROJECT_DIR" \
    --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
    --include="*.py" --include="*.go" --include="*.java" --include="*.yaml" --include="*.yml" \
    2>/dev/null | grep -v "node_modules" | grep -v ".git/" | grep -v "dist/" | grep -v ".next/" \
    | grep -v ".example" | grep -v ".template" | grep -v ".sample" \
    | grep -v "test" | grep -v "spec" | grep -v "mock" | head -5)

  if [ -n "$matches" ]; then
    echo "  🔴 可能的$description:"
    echo "$matches" | sed 's/^/    /'
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
  fi
}

search_secrets 'AKIA[0-9A-Z]\{16\}' "AWS Access Key"
search_secrets 'sk-[a-zA-Z0-9]\{20,}' "API Secret Key"
search_secrets 'ghp_[a-zA-Z0-9]\{36\}' "GitHub Personal Access Token"
search_secrets 'xox[bpoas]-[a-zA-Z0-9-]\{10,}' "Slack Token"

if [ "$SECRETS_FOUND" -eq 0 ]; then
  echo "  ✅ 未检测到明显的硬编码密钥"
fi
echo ""

# ---- HTTPS检查 ----
echo "🌐 【HTTP安全检查】"

HTTP_URLS=$(grep -rn "http://" "$PROJECT_DIR" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.py" --include="*.go" --include="*.yaml" --include="*.yml" \
  2>/dev/null | grep -v "node_modules" | grep -v ".git/" | grep -v "localhost" \
  | grep -v "127.0.0.1" | grep -v "0.0.0.0" | grep -v "http://schemas" \
  | grep -v "http://www.w3.org" | grep -v "http://xmlns" | head -10)

if [ -n "$HTTP_URLS" ]; then
  echo "  🟡 发现非HTTPS URL:"
  echo "$HTTP_URLS" | sed 's/^/    /'
  ISSUES=$((ISSUES + 1))
else
  echo "  ✅ 未发现非HTTPS外部URL"
fi
echo ""

# ---- 汇总 ----
echo "========================================="
echo "  安全审计汇总"
echo "========================================="
if [ "$ISSUES" -gt 0 ]; then
  echo "  ⚠️  发现 $ISSUES 个安全问题"
  exit 1
else
  echo "  ✅ 安全审计通过"
  exit 0
fi
