#!/usr/bin/env bash
# Home Server — один скрипт для сборки и запуска после клонирования
# One-command build and run after cloning the repo

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Проверка зависимостей и подсказки по установке
# Dependency check and install suggestions
missing=()
command -v node >/dev/null 2>&1 || missing+=(node)
command -v npm  >/dev/null 2>&1 || missing+=(npm)
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || missing+=(python)

if [ ${#missing[@]} -gt 0 ]; then
	echo "Home Server — не хватает зависимостей / missing dependencies: ${missing[*]}"
	echo ""
	echo "Установите их одним из способов ниже, затем снова запустите ./start.sh"
	echo "Install them using one of the options below, then run ./start.sh again"
	echo ""
	# Node.js (включает npm на официальном установщике)
	if [[ " ${missing[*]} " =~ " node " ]] || [[ " ${missing[*]} " =~ " npm " ]]; then
		echo "  Node.js 18+ и npm:"
		if command -v apt-get >/dev/null 2>&1; then
			echo "    Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y nodejs npm"
		elif command -v dnf >/dev/null 2>&1; then
			echo "    Fedora/RHEL:    sudo dnf install -y nodejs npm"
		elif command -v brew >/dev/null 2>&1; then
			echo "    macOS (Homebrew):  brew install node"
		else
			echo "    https://nodejs.org/ — скачайте LTS и установите"
			echo "    https://nodejs.org/ — download LTS and install"
		fi
		echo ""
	fi
	if [[ " ${missing[*]} " =~ " python " ]]; then
		echo "  Python 3.10+:"
		if command -v apt-get >/dev/null 2>&1; then
			echo "    Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y python3 python3-pip"
		elif command -v dnf >/dev/null 2>&1; then
			echo "    Fedora/RHEL:    sudo dnf install -y python3 python3-pip"
		elif command -v brew >/dev/null 2>&1; then
			echo "    macOS (Homebrew):  brew install python@3"
		else
			echo "    https://www.python.org/downloads/ — установите Python 3.10 или новее"
			echo "    https://www.python.org/downloads/ — install Python 3.10 or newer"
		fi
		echo ""
	fi
	exit 1
fi

echo "Home Server — проверка окружения / checking environment..."
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
