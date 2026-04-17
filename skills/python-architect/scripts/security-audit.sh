#!/bin/bash
# Python项目安全审计
# 用法: bash security-audit.sh [project-path]

set -uo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  Python 安全审计"
echo "========================================="
echo ""

ISSUES=0

cd "$PROJECT_DIR"

# ---- 1. 依赖漏洞扫描 ----
echo "📦 【依赖漏洞扫描】"

if command -v pip-audit &>/dev/null; then
  echo "  使用 pip-audit..."
  pip-audit 2>&1 || ISSUES=$((ISSUES + 1))
elif command -v safety &>/dev/null; then
  echo "  使用 safety check..."
  if [ -f "requirements.txt" ]; then
    safety check -r requirements.txt 2>&1 || ISSUES=$((ISSUES + 1))
  else
    safety check 2>&1 || ISSUES=$((ISSUES + 1))
  fi
else
  echo "  ⚠️  未安装 pip-audit 或 safety"
  echo "  💡 安装: pip install pip-audit"
fi
echo ""

# ---- 2. Bandit安全扫描 ----
echo "🔒 【Bandit 安全扫描】"

if command -v bandit &>/dev/null; then
  bandit -r . -x ./tests,./venv,./.venv -ll --format txt 2>&1 || ISSUES=$((ISSUES + 1))
else
  echo "  ⚠️  未安装 bandit"
  echo "  💡 安装: pip install bandit"
fi
echo ""

# ---- 3. 敏感文件检查 ----
echo "🔐 【敏感文件检查】"

check_sensitive() {
  local file="$1"
  local desc="$2"
  if [ -f "$file" ]; then
    if git check-ignore -q "$file" 2>/dev/null; then
      echo "  ✅ $file 已被 git 忽略"
    elif [ -f ".gitignore" ] && grep -qE "(^|/)${file}$|^\*\.env|\.env\*" ".gitignore" 2>/dev/null; then
      echo "  ✅ $file 已在 .gitignore 中"
    else
      echo "  🔴 $file 存在但未被 git 忽略! ($desc)"
      ISSUES=$((ISSUES + 1))
    fi
  fi
}

check_sensitive ".env" "环境变量文件"
check_sensitive ".env.local" "本地环境变量"
check_sensitive ".env.production" "生产环境变量"
check_sensitive "credentials.json" "凭证文件"
check_sensitive "service-account.json" "GCP服务账号"

if [ -f ".env" ] && [ ! -f ".env.example" ]; then
  echo "  🟡 存在 .env 但缺少 .env.example 模板"
fi
echo ""

# ---- 4. 硬编码密钥检查 ----
echo "🔑 【硬编码密钥检查】"

SECRETS_FOUND=0

search_secret() {
  local pattern="$1"
  local desc="$2"
  local matches

  matches=$(grep -rn "$pattern" . --include="*.py" --include="*.yaml" --include="*.yml" --include="*.toml" \
    2>/dev/null | grep -v "venv/" | grep -v ".venv/" | grep -v "__pycache__" \
    | grep -v ".example" | grep -v "test_" | grep -v "_test.py" | head -5)

  if [ -n "$matches" ]; then
    echo "  🔴 可能的 $desc:"
    echo "$matches" | sed 's/^/    /'
    SECRETS_FOUND=$((SECRETS_FOUND + 1))
  fi
}

search_secret 'AKIA[0-9A-Z]\{16\}' "AWS Access Key"
search_secret 'sk-[a-zA-Z0-9]\{20,}' "API Secret Key (OpenAI等)"
search_secret 'ghp_[a-zA-Z0-9]\{36\}' "GitHub Personal Access Token"
search_secret "password\s*=\s*['\"][^'\"]\{3,\}['\"]" "硬编码密码"
search_secret "secret\s*=\s*['\"][^'\"]\{3,\}['\"]" "硬编码密钥"
search_secret "api_key\s*=\s*['\"][^'\"]\{3,\}['\"]" "硬编码API Key"

if [ "$SECRETS_FOUND" -eq 0 ]; then
  echo "  ✅ 未检测到明显的硬编码密钥"
fi
echo ""

# ---- 5. 危险函数使用 ----
echo "⚠️  【危险函数检查】"

check_danger() {
  local pattern="$1"
  local desc="$2"
  local count
  count=$(grep -rn "$pattern" . --include="*.py" 2>/dev/null \
    | grep -v "venv/" | grep -v ".venv/" | grep -v "__pycache__" \
    | grep -v "test_" | grep -v "_test.py" | wc -l | tr -d ' ')
  if [ "$count" -gt 0 ]; then
    echo "  🔴 $desc: $count 处"
    grep -rn "$pattern" . --include="*.py" 2>/dev/null \
      | grep -v "venv/" | grep -v ".venv/" | grep -v "__pycache__" \
      | grep -v "test_" | head -3 | sed 's/^/    /'
    ISSUES=$((ISSUES + 1))
  fi
}

check_danger "eval(" "eval() 代码注入风险"
check_danger "exec(" "exec() 代码注入风险"
check_danger "pickle\.loads" "pickle反序列化攻击"
check_danger "os\.system(" "os.system() 命令注入"
check_danger "shell=True" "subprocess shell注入"
check_danger "yaml\.load(" "yaml.load() 不安全 (用 safe_load)"
check_danger "__import__(" "动态导入风险"
echo ""

# ---- 6. HTTPS检查 ----
echo "🌐 【HTTP安全检查】"
HTTP_URLS=$(grep -rn "http://" . --include="*.py" 2>/dev/null \
  | grep -v "venv/" | grep -v ".venv/" | grep -v "__pycache__" \
  | grep -v "localhost" | grep -v "127.0.0.1" | grep -v "0.0.0.0" \
  | grep -v "http://schemas" | grep -v "test_" | head -10)

if [ -n "$HTTP_URLS" ]; then
  echo "  🟡 发现非HTTPS URL:"
  echo "$HTTP_URLS" | sed 's/^/    /'
else
  echo "  ✅ 未发现非HTTPS外部URL"
fi
echo ""

cd - > /dev/null

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
