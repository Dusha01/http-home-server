# Home Server — быстрый запуск и сборка
# Использование: make [цель]

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SERVER := $(ROOT)server
FRONTEND := $(ROOT)frontend
VENV := $(SERVER)/venv
STATIC := $(SERVER)/static

.PHONY: help run install install-deps build clean run-server run-full dev uninstall-cli install-cli

# Цель по умолчанию
help:
	@echo "Home Server — доступные команды:"
	@echo ""
	@echo "  make run          — запуск (полная проверка, сборка при необходимости, сервер)"
	@echo "  make run-server   — только запуск сервера (без сборки фронта)"
	@echo "  make run-full     — полная установка и запуск (как ./start.sh)"
	@echo "  make install      — установка зависимостей проекта (venv + npm + сборка)"
	@echo "  make install-deps — проверка системных зависимостей (Python, Node.js), предложит установить"
	@echo "  make build        — сборка фронтенда и копирование в server/static"
	@echo "  make dev          — режим разработки (сервер с reload + не трогать статику)"
	@echo "  make clean        — удалить venv, node_modules, server/static"
	@echo "  make install-cli  — установить команду 'home-server' в PATH (один раз)"
	@echo "  make uninstall-cli — удалить команду 'home-server' из PATH"
	@echo ""

# Быстрый запуск: если уже установлено — только сервер; иначе полный цикл
run: ensure-dirs
	@if [ -d "$(VENV)" ] && [ -d "$(STATIC)" ]; then \
		$(MAKE) run-server; \
	else \
		$(MAKE) run-full; \
	fi

# Только запуск сервера (предполагается, что venv и статика уже есть)
run-server:
	@cd "$(SERVER)" && . $(VENV)/bin/activate && STATIC_DIR="$(STATIC)" python -m src

# Полный цикл: как start.sh
run-full:
	@./start.sh

# Установка только зависимостей проекта (venv, npm, сборка). Системные зависимости — через install-deps
install: install-deps ensure-dirs
	@./scripts/install-project.sh

# Проверка системных зависимостей (Python, Node.js); при отсутствии — предложит установить (yes/no)
install-deps:
	@./scripts/install-deps.sh

# Сборка фронтенда и копирование в server/static
build: ensure-dirs
	@./scripts/build-frontend.sh

# Режим разработки: запуск сервера с reload (статику не пересобираем)
dev: ensure-dirs
	@cd "$(SERVER)" && . $(VENV)/bin/activate && STATIC_DIR="$(STATIC)" DEBUG=true python -m src

# Создание нужных директорий
ensure-dirs:
	@mkdir -p $(SERVER)/data $(SERVER)/logs $(SERVER)/static

# Очистка
clean:
	rm -rf $(VENV) $(FRONTEND)/node_modules $(STATIC)
	@echo "Очистка завершена."

# Установка CLI: команда home-server будет доступна в любом месте
install-cli:
	@./scripts/install-cli.sh

# Удаление CLI
uninstall-cli:
	@./scripts/install-cli.sh --uninstall
