#!/usr/bin/env bash
# Проверка системных зависимостей (Python 3.10+, Node.js 18+, npm).
# При отсутствии — предложение установить (yes/no) и установка через пакетный менеджер.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Собираем список недостающих зависимостей
check_dependencies() {
    local missing=()
    local need_node=0
    local need_python=0

    if ! command -v node >/dev/null 2>&1; then
        missing+=("node (Node.js 18+)")
        need_node=1
    else
        node_version=$(node -v 2>/dev/null | sed -n 's/^v\([0-9]*\).*/\1/p')
        if [ -n "$node_version" ] && [ "$node_version" -lt 18 ]; then
            print_warning "Обнаружен Node.js v$node_version, рекомендуется 18+"
        fi
    fi

    if ! command -v npm >/dev/null 2>&1; then
        missing+=("npm")
        need_node=1
    fi

    if command -v python3 >/dev/null 2>&1; then
        py_ver=$(python3 -c 'import sys; print(sys.version_info.major, sys.version_info.minor)' 2>/dev/null || echo "0 0")
        major=${py_ver%% *}; minor=${py_ver##* }
        if [ -z "$major" ] || [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "${minor:-0}" -lt 10 ]; }; then
            missing+=("python (Python 3.10+)")
            need_python=1
        fi
    elif command -v python >/dev/null 2>&1; then
        py_ver=$(python -c 'import sys; print(sys.version_info.major, sys.version_info.minor)' 2>/dev/null || echo "0 0")
        major=${py_ver%% *}; minor=${py_ver##* }
        if [ -z "$major" ] || [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "${minor:-0}" -lt 10 ]; }; then
            missing+=("python (Python 3.10+)")
            need_python=1
        fi
    else
        missing+=("python (Python 3.10+)")
        need_python=1
    fi

    if [ ${#missing[@]} -eq 0 ]; then
        print_success "Все системные зависимости установлены."
        return 0
    fi

    echo ""
    print_error "Отсутствуют зависимости: ${missing[*]}"
    echo ""
    print_info "Установить недостающие зависимости автоматически? (yes/no)"
    read -r answer
    answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
    if [[ "$answer" != "yes" && "$answer" != "y" && "$answer" != "да" && "$answer" != "д" ]]; then
        echo ""
        echo "Ручная установка:"
        show_install_instructions "$need_node" "$need_python"
        return 1
    fi

    run_install "$need_node" "$need_python"
}

show_install_instructions() {
    local need_node=$1
    local need_python=$2

    if [ "$need_node" -eq 1 ]; then
        echo "  Node.js 18+ и npm:"
        if command -v apt-get >/dev/null 2>&1; then
            echo "    Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y nodejs npm"
        elif command -v dnf >/dev/null 2>&1; then
            echo "    Fedora/RHEL:    sudo dnf install -y nodejs npm"
        elif command -v brew >/dev/null 2>&1; then
            echo "    macOS:          brew install node"
        elif command -v pacman >/dev/null 2>&1; then
            echo "    Arch:           sudo pacman -S nodejs npm"
        else
            echo "    https://nodejs.org/ — скачайте LTS"
        fi
        echo ""
    fi

    if [ "$need_python" -eq 1 ]; then
        echo "  Python 3.10+:"
        if command -v apt-get >/dev/null 2>&1; then
            echo "    Debian/Ubuntu:  sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv"
        elif command -v dnf >/dev/null 2>&1; then
            echo "    Fedora/RHEL:    sudo dnf install -y python3 python3-pip"
        elif command -v brew >/dev/null 2>&1; then
            echo "    macOS:          brew install python@3.11"
        elif command -v pacman >/dev/null 2>&1; then
            echo "    Arch:           sudo pacman -S python python-pip"
        else
            echo "    https://www.python.org/downloads/"
        fi
        echo ""
    fi
}

run_install() {
    local need_node=$1
    local need_python=$2

    if command -v apt-get >/dev/null 2>&1; then
        print_info "Обнаружен apt (Debian/Ubuntu). Установка..."
        sudo apt-get update
        [ "$need_python" -eq 1 ] && sudo apt-get install -y python3 python3-pip python3-venv
        [ "$need_node" -eq 1 ] && sudo apt-get install -y nodejs npm
    elif command -v dnf >/dev/null 2>&1; then
        print_info "Обнаружен dnf (Fedora/RHEL). Установка..."
        [ "$need_python" -eq 1 ] && sudo dnf install -y python3 python3-pip
        [ "$need_node" -eq 1 ] && sudo dnf install -y nodejs npm
    elif command -v brew >/dev/null 2>&1; then
        print_info "Обнаружен Homebrew (macOS). Установка..."
        [ "$need_python" -eq 1 ] && brew install python@3.11
        [ "$need_node" -eq 1 ] && brew install node
    elif command -v pacman >/dev/null 2>&1; then
        print_info "Обнаружен pacman (Arch). Установка..."
        [ "$need_python" -eq 1 ] && sudo pacman -S --noconfirm python python-pip
        [ "$need_node" -eq 1 ] && sudo pacman -S --noconfirm nodejs npm
    else
        print_error "Не удалось определить пакетный менеджер. Установите зависимости вручную:"
        show_install_instructions "$need_node" "$need_python"
        return 1
    fi

    print_success "Системные зависимости установлены."
    return 0
}

check_dependencies
