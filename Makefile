# Home Server — быстрый запуск и сборка
# Использование: make [цель]

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SERVER := $(ROOT)server
FRONTEND := $(ROOT)frontend
VENV := $(SERVER)/.venv
STATIC := $(SERVER)/static

.PHONY: help run run-server run-full build clean dev

# Цель по умолчанию
help:
	@echo "Home Server — доступные команды:"
	@echo ""
	@echo "  make run          — запуск (если venv и статика есть — только сервер; иначе полный цикл через start.sh)"
	@echo "  make run-server   — только запуск сервера (нужны server/.venv и server/static)"
	@echo "  make run-full     — полный цикл как ./start.sh (venv, npm, сборка фронта, запуск)"
	@echo "  make build        — сборка фронтенда и копирование в server/static"
	@echo "  make dev          — режим разработки (сервер с reload + не трогать статику)"
	@echo "  make clean        — удалить server/.venv, frontend/node_modules, server/static"
	@echo ""
	@echo "Зависимости: установите вручную Python 3.10+, Node.js 18+ и npm; затем:"
	@echo "  python3 -m venv server/.venv && . server/.venv/bin/activate && pip install -r server/requirements.txt"
	@echo "  cd frontend && npm ci"
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
