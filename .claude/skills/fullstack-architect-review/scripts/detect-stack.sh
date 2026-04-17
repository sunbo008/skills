#!/bin/bash
# 自动检测项目技术栈
# 用法: bash detect-stack.sh [project-path]

set -euo pipefail

PROJECT_DIR="${1:-.}"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: 目录不存在: $PROJECT_DIR"
  exit 1
fi

echo "========================================="
echo "  项目技术栈检测报告"
echo "  路径: $(cd "$PROJECT_DIR" && pwd)"
echo "========================================="
echo ""

HAS_JQ=false
if command -v jq &> /dev/null; then
  HAS_JQ=true
fi

# ---- 包管理器检测 ----
echo "[包管理器]"
PKG_MGR=""
if [ -f "$PROJECT_DIR/pnpm-lock.yaml" ]; then
  echo "  * pnpm"
  PKG_MGR="pnpm"
elif [ -f "$PROJECT_DIR/yarn.lock" ]; then
  echo "  * yarn"
  PKG_MGR="yarn"
elif [ -f "$PROJECT_DIR/bun.lockb" ] || [ -f "$PROJECT_DIR/bun.lock" ]; then
  echo "  * bun"
  PKG_MGR="bun"
elif [ -f "$PROJECT_DIR/package-lock.json" ]; then
  echo "  * npm"
  PKG_MGR="npm"
else
  echo "  (!) 未检测到Node.js包管理器"
fi

if [ -f "$PROJECT_DIR/requirements.txt" ] || [ -f "$PROJECT_DIR/pyproject.toml" ] || [ -f "$PROJECT_DIR/Pipfile" ]; then
  echo "  * Python"
fi
if [ -f "$PROJECT_DIR/go.mod" ]; then
  echo "  * Go modules"
fi
if [ -f "$PROJECT_DIR/pom.xml" ] || [ -f "$PROJECT_DIR/build.gradle" ] || [ -f "$PROJECT_DIR/build.gradle.kts" ]; then
  echo "  * Java/Kotlin (Maven/Gradle)"
fi

echo ""

# JSON dependency checker: uses jq when available, falls back to grep
check_dep() {
  local dep_name="$1"
  local display_name="$2"
  local pkg_json="$PROJECT_DIR/package.json"

  if [ ! -f "$pkg_json" ]; then
    return 1
  fi

  local version=""
  if $HAS_JQ; then
    version=$(jq -r --arg d "$dep_name" '
      (.dependencies[$d] // .devDependencies[$d] // .peerDependencies[$d]) // empty
    ' "$pkg_json" 2>/dev/null)
  else
    version=$(grep -A0 "\"$dep_name\"" "$pkg_json" 2>/dev/null \
      | head -1 | sed 's/.*: *"\([^"]*\)".*/\1/' || true)
  fi

  if [ -n "$version" ]; then
    echo "  * $display_name ($version)"
    return 0
  fi
  return 1
}

# ---- 前端框架 ----
if [ -f "$PROJECT_DIR/package.json" ]; then
  echo "[前端框架]"
  check_dep "next" "Next.js" || true
  check_dep "nuxt" "Nuxt.js" || check_dep "nuxt3" "Nuxt 3" || true
  check_dep "react" "React" || true
  check_dep "vue" "Vue.js" || true
  check_dep "@angular/core" "Angular" || true
  check_dep "svelte" "Svelte" || check_dep "@sveltejs/kit" "SvelteKit" || true
  check_dep "solid-js" "Solid.js" || true
  check_dep "astro" "Astro" || true

  echo ""
  echo "[构建工具]"
  check_dep "vite" "Vite" || true
  check_dep "webpack" "Webpack" || true
  check_dep "turbo" "Turborepo" || true
  check_dep "esbuild" "esbuild" || true
  check_dep "rollup" "Rollup" || true

  echo ""
  echo "[类型系统]"
  check_dep "typescript" "TypeScript" || true
  if [ -f "$PROJECT_DIR/tsconfig.json" ]; then
    echo "  * tsconfig.json 存在"
    if grep -q '"strict": true' "$PROJECT_DIR/tsconfig.json" 2>/dev/null; then
      echo "  * strict模式已启用"
    else
      echo "  (!) strict模式未启用"
    fi
  fi

  # module type detection
  if $HAS_JQ; then
    pkg_type=$(jq -r '.type // empty' "$PROJECT_DIR/package.json" 2>/dev/null)
    if [ -n "$pkg_type" ]; then
      echo "  * package type: $pkg_type"
    fi
  fi

  echo ""
  echo "[样式方案]"
  check_dep "tailwindcss" "Tailwind CSS" || true
  check_dep "styled-components" "Styled Components" || true
  check_dep "@emotion/react" "Emotion" || true
  check_dep "sass" "Sass/SCSS" || true
  check_dep "less" "Less" || true

  echo ""
  echo "[状态管理]"
  check_dep "@reduxjs/toolkit" "Redux Toolkit" || check_dep "redux" "Redux" || true
  check_dep "zustand" "Zustand" || true
  check_dep "mobx" "MobX" || true
  check_dep "pinia" "Pinia" || true
  check_dep "jotai" "Jotai" || true
  check_dep "@tanstack/react-query" "TanStack Query" || check_dep "react-query" "React Query" || true
  check_dep "swr" "SWR" || true

  echo ""
  echo "[后端框架]"
  check_dep "express" "Express" || true
  check_dep "fastify" "Fastify" || true
  check_dep "@nestjs/core" "NestJS" || true
  check_dep "koa" "Koa" || true
  check_dep "hono" "Hono" || true

  echo ""
  echo "[数据库/ORM]"
  check_dep "@prisma/client" "Prisma Client" || check_dep "prisma" "Prisma" || true
  check_dep "drizzle-orm" "Drizzle ORM" || true
  check_dep "typeorm" "TypeORM" || true
  check_dep "sequelize" "Sequelize" || true
  check_dep "mongoose" "Mongoose (MongoDB)" || true
  check_dep "pg" "PostgreSQL (pg)" || true
  check_dep "mysql2" "MySQL" || true
  check_dep "redis" "Redis" || check_dep "ioredis" "Redis (ioredis)" || true

  echo ""
  echo "[测试框架]"
  check_dep "jest" "Jest" || true
  check_dep "vitest" "Vitest" || true
  check_dep "@testing-library/react" "React Testing Library" || true
  check_dep "cypress" "Cypress" || true
  check_dep "@playwright/test" "Playwright" || true
  check_dep "mocha" "Mocha" || true

  echo ""
  echo "[代码质量]"
  check_dep "eslint" "ESLint" || true
  check_dep "@biomejs/biome" "Biome" || true
  check_dep "prettier" "Prettier" || true
  check_dep "husky" "Husky (Git hooks)" || true
  check_dep "lint-staged" "lint-staged" || true
else
  echo "  (!) 未找到 package.json"
fi

# ---- Python后端检测 ----
if [ -f "$PROJECT_DIR/requirements.txt" ] || [ -f "$PROJECT_DIR/pyproject.toml" ] || [ -f "$PROJECT_DIR/Pipfile" ]; then
  echo ""
  echo "[Python后端]"
  PY_FILES=()
  for file in "$PROJECT_DIR/requirements.txt" "$PROJECT_DIR/pyproject.toml" "$PROJECT_DIR/Pipfile"; do
    [ -f "$file" ] && PY_FILES+=("$file")
  done
  check_py_dep() {
    local pattern="$1" display="$2"
    for file in "${PY_FILES[@]}"; do
      if grep -qi "$pattern" "$file" 2>/dev/null; then
        echo "  * $display"
        return
      fi
    done
  }
  check_py_dep "django" "Django"
  check_py_dep "flask" "Flask"
  check_py_dep "fastapi" "FastAPI"
  check_py_dep "sqlalchemy" "SQLAlchemy"
  check_py_dep "celery" "Celery"
  check_py_dep "pydantic" "Pydantic"
  check_py_dep "alembic" "Alembic"

  echo "  [Python工具链]"
  command -v ruff &> /dev/null && echo "  * Ruff (linter/formatter)" || true
  command -v mypy &> /dev/null && echo "  * mypy (type checker)" || true
  command -v pytest &> /dev/null && echo "  * pytest" || true
fi

# ---- Go后端检测 ----
if [ -f "$PROJECT_DIR/go.mod" ]; then
  echo ""
  echo "[Go后端]"
  grep -q "gin-gonic" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  * Gin" || true
  grep -q "go-chi" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  * Chi" || true
  grep -q "fiber" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  * Fiber" || true
  grep -q "echo" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  * Echo" || true
  grep -q "gorm" "$PROJECT_DIR/go.mod" 2>/dev/null && echo "  * GORM" || true
fi

# ---- Docker检测 ----
echo ""
echo "[容器化]"
if [ -f "$PROJECT_DIR/Dockerfile" ] || [ -f "$PROJECT_DIR/docker-compose.yml" ] || [ -f "$PROJECT_DIR/docker-compose.yaml" ]; then
  [ -f "$PROJECT_DIR/Dockerfile" ] && echo "  * Dockerfile"
  { [ -f "$PROJECT_DIR/docker-compose.yml" ] || [ -f "$PROJECT_DIR/docker-compose.yaml" ]; } && echo "  * Docker Compose"
else
  echo "  (!) 未检测到Docker配置"
fi

# ---- CI/CD检测 ----
echo ""
echo "[CI/CD]"
[ -d "$PROJECT_DIR/.github/workflows" ] && echo "  * GitHub Actions" || true
[ -f "$PROJECT_DIR/.gitlab-ci.yml" ] && echo "  * GitLab CI" || true
[ -f "$PROJECT_DIR/Jenkinsfile" ] && echo "  * Jenkins" || true
[ -f "$PROJECT_DIR/.circleci/config.yml" ] && echo "  * CircleCI" || true

# ---- 项目结构 ----
echo ""
echo "[项目结构]"
if [ -f "$PROJECT_DIR/pnpm-workspace.yaml" ] || [ -f "$PROJECT_DIR/lerna.json" ]; then
  echo "  * Monorepo"
elif [ -f "$PROJECT_DIR/package.json" ] && $HAS_JQ; then
  workspaces=$(jq -r '.workspaces // empty' "$PROJECT_DIR/package.json" 2>/dev/null)
  if [ -n "$workspaces" ] && [ "$workspaces" != "null" ]; then
    echo "  * Monorepo (workspaces)"
  fi
fi

count_files() {
  find "$PROJECT_DIR" -type f -name "$1" \
    -not -path "*/node_modules/*" -not -path "*/.next/*" \
    -not -path "*/dist/*" -not -path "*/.git/*" \
    -not -path "*/.venv/*" -not -path "*/venv/*" \
    2>/dev/null | wc -l | tr -d ' '
}

echo "  TypeScript: $(count_files '*.ts') .ts + $(count_files '*.tsx') .tsx"
echo "  JavaScript: $(count_files '*.js') .js + $(count_files '*.jsx') .jsx"
echo "  Python: $(count_files '*.py')"
echo "  Go: $(count_files '*.go')"
echo "  Vue: $(count_files '*.vue')"
echo "  CSS/SCSS: $(count_files '*.css') .css + $(count_files '*.scss') .scss"

echo ""
echo "========================================="
echo "  检测完成"
echo "========================================="
