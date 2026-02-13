#!/usr/bin/env bash
# Установка зависимостей проекта: venv, pip, npm, сборка фронта, копирование в server/static.
# Вызывается после install-deps (предполагается, что Python и Node уже есть).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    print_error "Python не найден. Сначала выполните: make install-deps"
    exit 1
fi

VENV_DIR="$ROOT/server/venv"
if [ ! -d "$VENV_DIR" ]; then
    print_info "Создание виртуального окружения Python..."
    "$PYTHON" -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
print_info "Обновление pip..."
pip install -q --upgrade pip
if [ -f "$ROOT/server/requirements.txt" ]; then
    print_info "Установка Python зависимостей..."
    pip install -q -r "$ROOT/server/requirements.txt"
else
    print_warning "server/requirements.txt не найден"
fi

print_info "Установка зависимостей фронтенда..."
cd "$ROOT/frontend"
if [ -f "package-lock.json" ]; then
    npm ci --no-audit --no-fund
else
    npm install --no-audit --no-fund
fi
print_info "Сборка фронтенда..."
npm run build
cd "$ROOT"

BUILD_DIR="$ROOT/frontend/build"
STATIC_DIR="$ROOT/server/static"
rm -rf "$STATIC_DIR"
cp -r "$BUILD_DIR" "$STATIC_DIR"
print_success "Фронтенд скопирован в $STATIC_DIR"
print_success "Установка проекта завершена. Запуск: make run или ./start.sh"
