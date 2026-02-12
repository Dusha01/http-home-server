#!/usr/bin/env bash
# Home Server — один скрипт для сборки и запуска после клонирования
# One-command build and run after cloning the repo

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Home Server — проверка окружения / checking environment..."
command -v node >/dev/null 2>&1 || { echo "Ошибка: нужен Node.js (Error: Node.js required)"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "Ошибка: нужен npm (Error: npm required)"; exit 1; }
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || { echo "Ошибка: нужен Python 3 (Error: Python 3 required)"; exit 1; }
PYTHON="$(command -v python3 2>/dev/null || command -v python)"

echo "Установка зависимостей фронтенда / Installing frontend dependencies..."
cd "$ROOT/frontend"
npm ci
echo "Сборка фронтенда / Building frontend..."
npm run build

echo "Установка зависимостей сервера / Installing server dependencies..."
cd "$ROOT/server"
"$PYTHON" -m pip install -q -r requirements.txt

# Режим релиза: раздаём SPA с того же порта
export STATIC_DIR="$ROOT/frontend/build"
# Подгружаем .env из корня и server (AUTH_REQUIRED и др.)
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
[ -f "$ROOT/server/.env" ] && set -a && . "$ROOT/server/.env" && set +a
# Чтобы не спрашивать в консоли, задайте AUTH_REQUIRED в .env (true/false)
# To skip console prompt, set AUTH_REQUIRED in .env (true/false)

echo "Запуск сервера / Starting server..."
exec "$PYTHON" -m src
