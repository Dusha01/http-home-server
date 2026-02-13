#!/usr/bin/env bash
# Установка команды home-server в PATH (один раз). После этого можно вызывать home-server из любого места.
# Использование: ./scripts/install-cli.sh [--uninstall]
# По умолчанию создаётся симлинк в ~/.local/bin (или $HOME/bin, если .local/bin недоступен).

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WRAPPER="$ROOT/home-server"
CMD_NAME="home-server"

# Каталог для установки: ~/.local/bin или ~/bin
if [ -n "${HOME:-}" ]; then
    BIN_DIR="$HOME/.local/bin"
    [ -d "$(dirname "$BIN_DIR")" ] || BIN_DIR="$HOME/bin"
else
    BIN_DIR="/usr/local/bin"
fi
TARGET="$BIN_DIR/$CMD_NAME"

uninstall_cli() {
    if [ -L "$TARGET" ] || [ -f "$TARGET" ]; then
        rm -f "$TARGET"
        echo "Команда $CMD_NAME удалена из $TARGET"
    else
        echo "Команда $CMD_NAME не установлена в $TARGET"
    fi
}

install_cli() {
    if [ ! -f "$WRAPPER" ]; then
        echo "Ошибка: не найден скрипт $WRAPPER"
        exit 1
    fi
    [ -x "$WRAPPER" ] || chmod +x "$WRAPPER"
    mkdir -p "$BIN_DIR"
    ln -sf "$WRAPPER" "$TARGET"
    echo "Команда установлена: $TARGET -> $WRAPPER"
    if ! command -v "$CMD_NAME" >/dev/null 2>&1; then
        echo ""
        echo "Добавьте в PATH, если ещё не добавлен:"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo "Добавьте эту строку в ~/.bashrc или ~/.profile и выполните: source ~/.bashrc"
    else
        echo "Теперь можно запускать: $CMD_NAME"
    fi
}

if [ "${1:-}" = "--uninstall" ]; then
    uninstall_cli
else
    install_cli
fi
