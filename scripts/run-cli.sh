#!/usr/bin/env bash
# Запуск home-server через CLI: сервер на 8085, фронт на 5175.
# Используется командой home-server после make install-cli.

set -euo pipefail
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ "$SOURCE" != /* ]] && SOURCE="$DIR/$SOURCE"
done
ROOT="$(cd -P "$(dirname "$SOURCE")/.." && pwd)"
cd "$ROOT"

SERVER_PORT=8082
FRONTEND_PORT=5175

# Загружаем .env
if [ -f "$ROOT/.env" ]; then
    set -a
    source "$ROOT/.env"
    set +a
fi
if [ -f "$ROOT/server/.env" ]; then
    set -a
    source "$ROOT/server/.env"
    set +a
fi

export SERVER_PORT
export FRONTEND_URL="http://localhost:$FRONTEND_PORT"
# Неинтерактивный режим: AUTH_REQUIRED из .env или n (без токена для быстрого доступа)
export AUTH_REQUIRED="${AUTH_REQUIRED:-n}"
# В dev-режиме статику отдаёт Vite — сервер без STATIC_DIR, API без /api (proxy с rewrite)
unset STATIC_DIR
mkdir -p "$ROOT/server/data" "$ROOT/server/logs"

# Проверка venv
VENV="$ROOT/server/venv"
if [ ! -d "$VENV" ] || [ ! -f "$VENV/bin/activate" ]; then
    echo "❌ Сначала выполните: make install"
    exit 1
fi

# Проверка frontend
if [ ! -d "$ROOT/frontend/node_modules" ]; then
    echo "❌ Сначала выполните: make install"
    exit 1
fi

# Запуск сервера в фоне
cd "$ROOT/server"
source "$VENV/bin/activate"
python -m src &
SERVER_PID=$!
cd "$ROOT"

cleanup() {
    kill $SERVER_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Ждём запуска сервера
sleep 2
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ Сервер не запустился"
    if command -v lsof >/dev/null 2>&1 && lsof -i ":$SERVER_PORT" -t >/dev/null 2>&1; then
        echo "   Порт $SERVER_PORT занят. Освободите: kill \$(lsof -ti:$SERVER_PORT)"
    fi
    exit 1
fi

echo "✅ Сервер: http://localhost:$SERVER_PORT"
echo "✅ Фронт:  http://localhost:$FRONTEND_PORT"
echo ""

# Запуск фронта (foreground)
cd "$ROOT/frontend"
VITE_PROXY_TARGET="http://localhost:$SERVER_PORT" npm run dev -- --port "$FRONTEND_PORT"
