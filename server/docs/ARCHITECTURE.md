# Архитектура бэкенда (Home File Server)

## Стандарты и структура

Проект приведён к типичной для Python/FastAPI структуре: **ядро (core)**, **модули (features)**, **единая точка зависимостей**.

### Дерево пакетов

```
src/
├── __main__.py          # Точка входа: python -m src (опрос про токен + uvicorn)
├── app.py               # Фабрика приложения create_app(), lifespan, роуты
├── config.py            # Реэкспорт из core (обратная совместимость)
├── version.py
├── core/                # Ядро приложения
│   ├── __init__.py
│   ├── config.py        # Settings, пути, конфиг из .env
│   ├── dependencies.py  # FastAPI Depends: get_auth_service, get_token_if_required, ...
│   └── startup.py       # Вывод в консоль при старте (баннер, токен, QR)
└── modules/            # Доменные модули
    ├── auth/
    │   ├── models/      # Pydantic-модели (auth_models.py)
    │   ├── routes/      # Роутер /auth (create_auth_router)
    │   ├── services/    # AuthService (единое имя папки с share)
    │   └── utils/       # token_generate, token_validator, qr_utils
    └── share/
        ├── models/
        ├── routes/      # Роутер /share
        ├── services/    # DirectoryService, FileService
        └── utils/
```

## Принятые решения

1. **Единое имя слоя сервисов**  
   Везде используется папка `services/` (раньше в auth было `service/`).

2. **Зависимости через FastAPI Depends**  
   Сервисы и флаг аутентификации берутся из `app.state` через `core.dependencies`:
   - `get_auth_service`, `get_directory_service`, `get_file_service`
   - `get_token_if_required` — при включённой аутентификации проверяет Bearer, иначе пропускает
   - `get_optional_token` — для публичных эндпоинтов (токен опционален)

3. **Роутеры без аргументов фабрики**  
   `create_auth_router()` и `create_share_router()` не принимают сервисы; всё внедряется через `Depends(...)`.

4. **Конфиг в core**  
   Реальные настройки в `core.config`; `src.config` только реэкспортирует для старых импортов.

5. **Стартовая отрисовка в core.startup**  
   Вывод баннера, токена и QR вынесен из lifespan в `core.startup`, чтобы не раздувать `app.py`.

6. **Точка входа**  
   - `python -m src` — интерактивный вопрос про токен, затем uvicorn.
   - `uvicorn src.app:app` — без вопроса, с аутентификацией по умолчанию.

## Запуск

```bash
cd server
python -m src
# или
uvicorn src.app:app --host 0.0.0.0 --port 8080
```

## Дальнейшие улучшения (по желанию)

- Вынести роутеры в `api/v1/` и версионировать API.
- Добавить `pyproject.toml` и установку пакета в editable mode.
- Покрыть тестами `core.dependencies` и `core.startup` (моки app.state).
