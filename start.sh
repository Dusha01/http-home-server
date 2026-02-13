#!/usr/bin/env bash
# Home Server — единый скрипт для установки и запуска
# One-command setup and run for Home Server

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Проверка зависимостей
check_dependencies() {
    local missing=()
    
    # Проверка Node.js
    if ! command -v node >/dev/null 2>&1; then
        missing+=("node")
    else
        node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$node_version" -lt 18 ]; then
            print_warning "Node.js версии $node_version обнаружен, рекомендуется 18+"
        fi
    fi
    
    # Проверка npm
    if ! command -v npm >/dev/null 2>&1; then
        missing+=("npm")
    fi
    
    # Проверка Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON="python"
    else
        missing+=("python")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        print_error "Отсутствуют зависимости: ${missing[*]}"
        if [ -x "$ROOT/scripts/install-deps.sh" ]; then
            "$ROOT/scripts/install-deps.sh" || exit 1
            check_dependencies
            return
        else
            show_install_instructions "${missing[@]}"
            exit 1
        fi
    fi
}

# Показ инструкций по установке
show_install_instructions() {
    echo ""
    print_info "Инструкции по установке:"
    
    if [[ " ${*[*]} " =~ " node " ]] || [[ " ${*[*]} " =~ " npm " ]]; then
        echo ""
        echo "  Node.js 18+ и npm:"
        if command -v apt-get >/dev/null 2>&1; then
            echo "    Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y nodejs npm"
        elif command -v dnf >/dev/null 2>&1; then
            echo "    Fedora/RHEL:    sudo dnf install -y nodejs npm"
        elif command -v brew >/dev/null 2>&1; then
            echo "    macOS (Homebrew):  brew install node"
        elif command -v pacman >/dev/null 2>&1; then
            echo "    Arch Linux:     sudo pacman -S nodejs npm"
        else
            echo "    https://nodejs.org/ — скачайте LTS версию"
        fi
    fi
    
    if [[ " ${*[*]} " =~ " python " ]]; then
        echo ""
        echo "  Python 3.10+:"
        if command -v apt-get >/dev/null 2>&1; then
            echo "    Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv"
        elif command -v dnf >/dev/null 2>&1; then
            echo "    Fedora/RHEL:    sudo dnf install -y python3 python3-pip"
        elif command -v brew >/dev/null 2>&1; then
            echo "    macOS (Homebrew):  brew install python@3.11"
        elif command -v pacman >/dev/null 2>&1; then
            echo "    Arch Linux:     sudo pacman -S python python-pip"
        else
            echo "    https://www.python.org/downloads/ — установите Python 3.10 или новее"
        fi
    fi
    echo ""
}

# Создание/активация виртуального окружения Python
setup_python_venv() {
    print_info "Настройка виртуального окружения Python..."
    
    VENV_DIR="$ROOT/server/venv"
    
    if [ ! -d "$VENV_DIR" ]; then
        print_info "Создание виртуального окружения..."
        "$PYTHON" -m venv "$VENV_DIR"
    fi
    
    # Активируем виртуальное окружение
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    else
        print_error "Не удалось создать виртуальное окружение"
        exit 1
    fi
    
    # Обновляем pip
    print_info "Обновление pip..."
    pip install --upgrade pip
    
    # Установка зависимостей
    if [ -f "$ROOT/server/requirements.txt" ]; then
        print_info "Установка Python зависимостей..."
        pip install -q -r "$ROOT/server/requirements.txt"
    else
        print_warning "requirements.txt не найден"
    fi
}

# Настройка фронтенда с изоляцией
setup_frontend() {
    print_info "Настройка фронтенда..."
    
    cd "$ROOT/frontend"
    
    # Используем npm ci для точного воспроизведения зависимостей
    if [ -f "package-lock.json" ]; then
        print_info "Установка точных зависимостей из package-lock.json..."
        npm ci --no-audit --no-fund
    else
        print_info "Установка зависимостей из package.json..."
        npm install --no-audit --no-fund
    fi
    
    # Сборка
    print_info "Сборка фронтенда..."
    npm run build
    
    cd "$ROOT"
}

# Копирование собранного фронтенда в статику сервера
deploy_frontend() {
    print_info "Развертывание фронтенда..."
    
    BUILD_DIR="$ROOT/frontend/build"
    STATIC_DIR="$ROOT/server/static"
    
    if [ -d "$BUILD_DIR" ]; then
        # Очищаем старую статику
        rm -rf "$STATIC_DIR"
        # Копируем новую
        cp -r "$BUILD_DIR" "$STATIC_DIR"
        print_success "Фронтенд скопирован в $STATIC_DIR"
    else
        print_error "Директория сборки не найдена: $BUILD_DIR"
        exit 1
    fi
}

# Загрузка переменных окружения
load_env() {
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
}

# Проверка и создание необходимых директорий
ensure_directories() {
    mkdir -p "$ROOT/server/data"
    mkdir -p "$ROOT/server/logs"
    mkdir -p "$ROOT/server/static"
}

# Очистка старых установок (опционально)
clean_install() {
    if [ "${1:-}" = "--clean" ]; then
        print_warning "Полная переустановка..."
        rm -rf "$ROOT/server/venv"
        rm -rf "$ROOT/frontend/node_modules"
        rm -rf "$ROOT/server/static"
        print_success "Очистка завершена"
    fi
}

# Основная функция
main() {
    echo "====================================="
    echo "   Home Server — установка и запуск  "
    echo "====================================="
    echo ""
    
    # Обработка флагов
    clean_install "${1:-}"
    
    # Проверка зависимостей
    check_dependencies
    
    # Создание директорий
    ensure_directories
    
    # Настройка Python окружения
    setup_python_venv
    
    # Настройка фронтенда
    setup_frontend
    
    # Копирование статики
    deploy_frontend
    
    # Загрузка .env
    load_env
    
    # Запуск сервера
    print_success "Все готово! Запуск сервера..."
    echo ""
    
    cd "$ROOT/server"
    export STATIC_DIR="$ROOT/server/static"
    
    # Запуск сервера
    exec python -m src
}

# Запуск
main "$@"