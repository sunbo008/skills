#!/bin/bash
# 自动检测项目技术栈
# 用法: bash detect-stack.sh [project-path]

set -euo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  项目技术栈检测报告"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
echo "========================================="
echo ""

# ---- 前端检测 ----
echo "📦 【包管理器】"
if [ -f "$PROJECT_DIR/pnpm-lock.yaml" ]; then
  echo "  ✅ pnpm"
  PKG_MGR="pnpm"
elif [ -f "$PROJECT_DIR/yarn.lock" ]; then
  echo "  ✅ yarn"
  PKG_MGR="yarn"
elif [ -f "$PROJECT_DIR/bun.lockb" ] || [ -f "$PROJECT_DIR/bun.lock" ]; then
  echo "  ✅ bun"
  PKG_MGR="bun"
elif [ -f "$PROJECT_DIR/package-lock.json" ]; then
  echo "  ✅ npm"
  PKG_MGR="npm"
else
  echo "  ⚠️  未检测到Node.js包管理器"
  PKG_MGR=""
fi

if [ -f "$PROJECT_DIR/requirements.txt" ] || [ -f "$PROJECT_DIR/pyproject.toml" ] || [ -f "$PROJECT_DIR/Pipfile" ]; then
  echo "  ✅ Python"
fi
if [ -f "$PROJECT_DIR/go.mod" ]; then
  echo "  ✅ Go modules"
fi
if [ -f "$PROJECT_DIR/pom.xml" ] || [ -f "$PROJECT_DIR/build.gradle" ] || [ -f "$PROJECT_DIR/build.gradle.kts" ]; then
  echo "  ✅ Java/Kotlin (Maven/Gradle)"
fi

echo ""
echo "🎨 【前端框架】"
if [ -f "$PROJECT_DIR/package.json" ]; then
  PKG_JSON="$PROJECT_DIR/package.json"

  check_dep() {
    local dep_name="$1"
    local display_name="$2"
    if grep -q "\"$dep_name\"" "$PKG_JSON" 2>/dev/null; then
      local version
      version=$(grep "\"$dep_name\"" "$PKG_JSON" | head -1 | sed 's/.*: *"\(.*\)".*/\1/')
      echo "  ✅ $display_name ($version)"
      return 0
    fi
    return 1
  }

  check_dep "next" "Next.js" || true
  check_dep "nuxt" "Nuxt.js" || check_dep "nuxt3" "Nuxt 3" || true
  check_dep "react" "React" || true
  check_dep "vue" "Vue.js" || true
  check_dep "@angular/core" "Angular" || true
  check_dep "svelte" "Svelte" || check_dep "@sveltejs/kit" "SvelteKit" || true
  check_dep "solid-js" "Solid.js" || true
  check_dep "astro" "Astro" || true

  echo ""
  echo "🛠️ 【构建工具】"
  check_dep "vite" "Vite" || true
  check_dep "webpack" "Webpack" || true
  check_dep "turbo" "Turborepo" || true
  check_dep "esbuild" "esbuild" || true
  check_dep "rollup" "Rollup" || true

  echo ""
  echo "🎯 【类型系统】"
  check_dep "typescript" "TypeScript" || true
  if [ -f "$PROJECT_DIR/tsconfig.json" ]; then
    echo "  ✅ tsconfig.json 存在"
    if grep -q '"strict": true' "$PROJECT_DIR/tsconfig.json" 2>/dev/null; then
      echo "  ✅ strict模式已启用"
    else
      echo "  ⚠️  strict模式未启用"
    fi
  fi

  echo ""
  echo "🎨 【样式方案】"
  check_dep "tailwindcss" "Tailwind CSS" || true
  check_dep "styled-components" "Styled Components" || true
  check_dep "@emotion/react" "Emotion" || true
  check_dep "sass" "Sass/SCSS" || true
  check_dep "less" "Less" || true

  echo ""
  echo "📊 【状态管理】"
  check_dep "redux" "Redux" || check_dep "@reduxjs/toolkit" "Redux Toolkit" || true
  check_dep "zustand" "Zustand" || true
  check_dep "mobx" "MobX" || true
  check_dep "pinia" "Pinia" || true
  check_dep "jotai" "Jotai" || true
  check_dep "recoil" "Recoil" || true
  check_dep "@tanstack/react-query" "TanStack Query" || check_dep "react-query" "React Query" || true
  check_dep "swr" "SWR" || true

  echo ""
  echo "🔧 【后端框架】"
  check_dep "express" "Express" || true
  check_dep "fastify" "Fastify" || true
  check_dep "@nestjs/core" "NestJS" || true
  check_dep "koa" "Koa" || true
  check_dep "hono" "Hono" || true

  echo ""
  echo "🗄️ 【数据库/ORM】"
  check_dep "prisma" "Prisma" || check_dep "@prisma/client" "Prisma Client" || true
  check_dep "drizzle-orm" "Drizzle ORM" || true
  check_dep "typeorm" "TypeORM" || true
  check_dep "sequelize" "Sequelize" || true
  check_dep "mongoose" "Mongoose (MongoDB)" || true
  check_dep "pg" "PostgreSQL (pg)" || true
  check_dep "mysql2" "MySQL" || true
  check_dep "redis" "Redis" || check_dep "ioredis" "Redis (ioredis)" || true

  echo ""
  echo "🧪 【测试框架】"
  check_dep "jest" "Jest" || true
  check_dep "vitest" "Vitest" || true
  check_dep "@testing-library/react" "React Testing Library" || true
  check_dep "cypress" "Cypress" || true
  check_dep "@playwright/test" "Playwright" || true
  check_dep "mocha" "Mocha" || true

  echo ""
  echo "📐 【代码质量】"
  check_dep "eslint" "ESLint" || true
  check_dep "prettier" "Prettier" || true
  check_dep "husky" "Husky (Git hooks)" || true
  check_dep "lint-staged" "lint-staged" || true
else
  echo "  ⚠️  未找到 package.json"
fi

# ---- Python后端检测 ----
if [ -f "$PROJECT_DIR/requirements.txt" ] || [ -f "$PROJECT_DIR/pyproject.toml" ]; then
  echo ""
  echo "🐍 【Python后端】"
  for file in "$PROJECT_DIR/requirements.txt" "$PROJECT_DIR/pyproject.toml"; do
    if [ -f "$file" ]; then
      grep -qi "django" "$file" 2>/dev/null && echo "  ✅ Django" || true
      grep -qi "flask" "$file" 2>/dev/null && echo "  ✅ Flask" || true
      grep -qi "fastapi" "$file" 2>/dev/null && echo "  ✅ FastAPI" || true
      grep -qi "sqlalchemy" "$file" 2>/dev/null && echo "  ✅ SQLAlchemy" || true
      grep -qi "celery" "$file" 2>/dev/null && echo "  ✅ Celery" || true
    fi
  done
fi

# ---- Go后端检测 ----
if [ -f "$PROJECT_DIR/go.mod" ]; then
  echo ""
  echo "🔷 【Go后端】"
  grep -q "gin-gonic" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  ✅ Gin" || true
  grep -q "go-chi" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  ✅ Chi" || true
  grep -q "fiber" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  ✅ Fiber" || true
  grep -q "echo" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  ✅ Echo" || true
  grep -q "gorm" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  ✅ GORM" || true
fi

# ---- Docker检测 ----
echo ""
echo "🐳 【容器化】"
if [ -f "$PROJECT_DIR/Dockerfile" ] || [ -f "$PROJECT_DIR/docker-compose.yml" ] || [ -f "$PROJECT_DIR/docker-compose.yaml" ]; then
  [ -f "$PROJECT_DIR/Dockerfile" ] && echo "  ✅ Dockerfile"
  [ -f "$PROJECT_DIR/docker-compose.yml" ] || [ -f "$PROJECT_DIR/docker-compose.yaml" ] && echo "  ✅ Docker Compose"
else
  echo "  ⚠️  未检测到Docker配置"
fi

# ---- CI/CD检测 ----
echo ""
echo "🔄 【CI/CD】"
[ -d "$PROJECT_DIR/.github/workflows" ] && echo "  ✅ GitHub Actions" || true
[ -f "$PROJECT_DIR/.gitlab-ci.yml" ] && echo "  ✅ GitLab CI" || true
[ -f "$PROJECT_DIR/Jenkinsfile" ] && echo "  ✅ Jenkins" || true
[ -f "$PROJECT_DIR/.circleci/config.yml" ] && echo "  ✅ CircleCI" || true

# ---- 项目结构 ----
echo ""
echo "📁 【项目结构】"
if [ -f "$PROJECT_DIR/pnpm-workspace.yaml" ] || [ -f "$PROJECT_DIR/lerna.json" ] || ([ -f "$PROJECT_DIR/package.json" ] && grep -q '"workspaces"' "$PROJECT_DIR/package.json" 2>/dev/null); then
  echo "  ✅ Monorepo"
fi

# 统计文件数量
count_files() {
  find "$PROJECT_DIR" -name "$1" -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/dist/*" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' '
}

echo "  📄 TypeScript文件: $(count_files '*.ts') .ts + $(count_files '*.tsx') .tsx"
echo "  📄 JavaScript文件: $(count_files '*.js') .js + $(count_files '*.jsx') .jsx"
echo "  📄 Python文件: $(count_files '*.py')"
echo "  📄 Go文件: $(count_files '*.go')"
echo "  📄 CSS/SCSS文件: $(count_files '*.css') .css + $(count_files '*.scss') .scss"

echo ""
echo "========================================="
echo "  检测完成"
echo "========================================="
