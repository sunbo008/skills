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
  echo "[Node.js依赖审计]"

  ORIG_DIR="$(pwd)"
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
    echo "  (!) 未找到lock文件,无法进行精确审计"
  fi

  cd "$ORIG_DIR"
  echo ""
fi

# ---- Python依赖审计 ----
if [ -f "$PROJECT_DIR/requirements.txt" ] || [ -f "$PROJECT_DIR/pyproject.toml" ] || [ -f "$PROJECT_DIR/Pipfile" ]; then
  echo "[Python依赖审计]"

  if command -v pip-audit &> /dev/null; then
    echo "  使用 pip-audit..."
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
      pip-audit -r "$PROJECT_DIR/requirements.txt" 2>&1 || ISSUES=$((ISSUES + 1))
    fi
    if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
      pip-audit --path "$PROJECT_DIR" 2>&1 || ISSUES=$((ISSUES + 1))
    fi
  elif command -v safety &> /dev/null; then
    echo "  使用 safety check..."
    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
      safety check -r "$PROJECT_DIR/requirements.txt" 2>&1 || ISSUES=$((ISSUES + 1))
    fi
  else
    echo "  (!) 未安装 pip-audit 或 safety,跳过"
    echo "  提示: pip install pip-audit"
  fi
  echo ""
fi

# ---- Go依赖审计 ----
if [ -f "$PROJECT_DIR/go.mod" ]; then
  echo "[Go依赖审计]"

  if command -v govulncheck &> /dev/null; then
    echo "  使用 govulncheck..."
    ORIG_DIR="$(pwd)"
    cd "$PROJECT_DIR"
    govulncheck ./... 2>&1 || ISSUES=$((ISSUES + 1))
    cd "$ORIG_DIR"
  else
    echo "  (!) 未安装 govulncheck,跳过"
    echo "  提示: go install golang.org/x/vuln/cmd/govulncheck@latest"
  fi
  echo ""
fi

# ---- .env文件检查 ----
echo "[敏感文件检查]"

check_sensitive() {
  local file="$1"
  local description="$2"
  if [ -f "$PROJECT_DIR/$file" ]; then
    if [ -f "$PROJECT_DIR/.gitignore" ]; then
      # Check for exact match, leading slash, or wildcard patterns
      if grep -qE "^/?${file}$|^\*\.env|^\.env\*|^\.env\." "$PROJECT_DIR/.gitignore" 2>/dev/null; then
        echo "  [OK] $file 在 .gitignore 中"
      else
        echo "  [P0] $file 存在但未在 .gitignore 中! ($description)"
        ISSUES=$((ISSUES + 1))
      fi
    else
      echo "  [P0] $file 存在且无 .gitignore 文件! ($description)"
      ISSUES=$((ISSUES + 1))
    fi
  fi
}

check_sensitive ".env" "环境变量文件"
check_sensitive ".env.local" "本地环境变量"
check_sensitive ".env.production" "生产环境变量"
check_sensitive ".env.development" "开发环境变量"

# Check for .env.example
env_exists=false
for f in .env .env.local .env.development .env.production; do
  if [ -f "$PROJECT_DIR/$f" ]; then
    env_exists=true
    break
  fi
done
if $env_exists; then
  if [ ! -f "$PROJECT_DIR/.env.example" ] && [ ! -f "$PROJECT_DIR/.env.template" ]; then
    echo "  [P1] 存在.env文件但缺少 .env.example 模板"
  fi
fi
echo ""

# ---- 硬编码密钥检查 ----
echo "[硬编码密钥检查]"

SECRETS_FOUND=0

search_secrets() {
  local pattern="$1"
  local description="$2"
  local matches

  matches=$(grep -Ern "$pattern" "$PROJECT_DIR" \
    --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
    --include="*.py" --include="*.go" --include="*.java" \
    --include="*.yaml" --include="*.yml" --include="*.json" --include="*.toml" \
    2>/dev/null \
    | grep -v "node_modules" | grep -v ".git/" | grep -v "dist/" | grep -v ".next/" \
    | grep -v ".venv/" | grep -v "venv/" | grep -v "__pycache__/" \
    | grep -v ".example" | grep -v ".template" | grep -v ".sample" \
    | grep -v "test" | grep -v "spec" | grep -v "mock" | grep -v "fixture" \
    | head -5)

  if [ -n "$matches" ]; then
    echo "  [P0] 可能的$description:"
    echo "$matches" | sed 's/^/    /'
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
  fi
}

# AWS
search_secrets 'AKIA[0-9A-Z]{16}' "AWS Access Key"
# OpenAI / Generic API keys
search_secrets 'sk-[a-zA-Z0-9]{20,}' "API Secret Key (OpenAI等)"
# GitHub PAT
search_secrets 'ghp_[a-zA-Z0-9]{36}' "GitHub Personal Access Token"
# Slack
search_secrets 'xox[bpoas]-[a-zA-Z0-9-]{10,}' "Slack Token"
# Google API Key
search_secrets 'AIza[0-9A-Za-z_-]{35}' "Google API Key"
# Stripe
search_secrets 'sk_live_[0-9a-zA-Z]{20,}' "Stripe Secret Key"
search_secrets 'pk_live_[0-9a-zA-Z]{20,}' "Stripe Publishable Key (live)"
# PEM private keys
search_secrets 'BEGIN.*PRIVATE KEY' "PEM Private Key"
# Database connection strings with credentials
search_secrets 'postgresql://[^:]*:[^@]*@|mysql://[^:]*:[^@]*@|mongodb://[^:]*:[^@]*@|redis://[^:]*:[^@]*@' "数据库连接串(含凭据)"

if [ "$SECRETS_FOUND" -eq 0 ]; then
  echo "  [OK] 未检测到明显的硬编码密钥"
fi
echo ""

# ---- HTTPS检查 ----
echo "[HTTP安全检查]"

HTTP_URLS=$(grep -rn "http://" "$PROJECT_DIR" \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.py" --include="*.go" --include="*.yaml" --include="*.yml" \
  2>/dev/null | grep -v "node_modules" | grep -v ".git/" | grep -v ".venv/" \
  | grep -v "localhost" | grep -v "127.0.0.1" | grep -v "0.0.0.0" \
  | grep -v "http://schemas" | grep -v "http://www.w3.org" | grep -v "http://xmlns" \
  | grep -v "http://json-schema" | grep -v "http://example" \
  | head -10)

if [ -n "$HTTP_URLS" ]; then
  echo "  [P1] 发现非HTTPS URL:"
  echo "$HTTP_URLS" | sed 's/^/    /'
  ISSUES=$((ISSUES + 1))
else
  echo "  [OK] 未发现非HTTPS外部URL"
fi
echo ""

# ---- 汇总 ----
echo "========================================="
echo "  安全审计汇总"
echo "========================================="
if [ "$ISSUES" -gt 0 ]; then
  echo "  [!] 发现 $ISSUES 个安全问题"
  exit 1
else
  echo "  [PASS] 安全审计通过"
  exit 0
fi
