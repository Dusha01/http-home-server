#!/usr/bin/env bash
# Сборка фронтенда и копирование в server/static.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

cd "$ROOT/frontend"
[ -f "package-lock.json" ] && npm ci --no-audit --no-fund || npm install --no-audit --no-fund
npm run build
cd "$ROOT"
rm -rf "$ROOT/server/static"
cp -r "$ROOT/frontend/build" "$ROOT/server/static"
print_success "Фронтенд собран и скопирован в server/static"
