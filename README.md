# Home Server

Локальный HTTP‑сервер для обмена файлами в домашней сети: веб‑интерфейс, загрузка/скачивание, превью, токены и QR‑вход.

A local HTTP server for file sharing on your home network: web UI, upload/download, preview, token auth and QR login.

---

## Быстрый старт / Quick start

После клонирования репозитория запуск одной командой:

After cloning, run with a single command:

```bash
./start.sh
```

или через Makefile / or via Makefile:

```bash
make run
```

Скрипт при отсутствии системных зависимостей предложит установить их (yes/no). При согласии зависимости (Python, Node.js) устанавливаются автоматически через пакетный менеджер (apt, dnf, pacman, brew). Затем устанавливаются зависимости проекта, собирается фронтенд и запускается сервер. Веб‑интерфейс: `http://localhost:8080` (или `http://<IP>:8080` с другого устройства в сети).

The script will prompt to install missing system dependencies (yes/no). If agreed, Python and Node.js are installed via the system package manager. Then project dependencies are installed, frontend is built and the server starts. Web UI: `http://localhost:8080` (or `http://<IP>:8080` from another device).

При первом запуске без настроенного `.env` скрипт не задаёт режим аутентификации — сервер спросит в консоли: **с токеном (y)** или **без (n)**. Чтобы запуск был полностью без вопросов, создайте `server/.env` и задайте `AUTH_REQUIRED=true` или `AUTH_REQUIRED=false`.

On first run without a `.env` file, the server will ask in the console: **with token (y)** or **without (n)**. For a fully non-interactive run, create `server/.env` and set `AUTH_REQUIRED=true` or `AUTH_REQUIRED=false`.

---

## Требования / Requirements

- **Node.js** 18+ и **npm**
- **Python** 3.10+

Если чего‑то не хватает, при запуске `./start.sh` или `make run` появится предложение установить зависимости (yes/no). Отдельно проверить и установить только системные зависимости: `make install-deps`.

If any are missing, `./start.sh` or `make run` will prompt to install them (yes/no). To only check/install system deps: `make install-deps`.

---

## Makefile и CLI / Makefile and CLI

| Команда / Command | Описание / Description |
|-------------------|------------------------|
| `make run` | Быстрый запуск (если уже установлено — только сервер; иначе полная установка и запуск). |
| `make run-full` | Полный цикл как `./start.sh`. |
| `make run-server` | Только запуск сервера (venv и статика должны быть уже готовы). |
| `make install` | Установка зависимостей проекта (после `install-deps`: venv, npm, сборка). |
| `make install-deps` | Проверка Python и Node.js; при отсутствии — предложение установить (yes/no). |
| `make build` | Сборка фронтенда и копирование в `server/static`. |
| `make dev` | Режим разработки (сервер с reload). |
| `make clean` | Удалить venv, node_modules, server/static. |
| `make install-cli` | Один раз установить команду `home-server` в PATH (~/.local/bin). |
| `make uninstall-cli` | Удалить команду `home-server` из PATH. |

**Запуск из любой директории (CLI):** один раз выполните `make install-cli`. После этого команда `home-server` будет доступна из любого места и запустит сервер (из корня репозитория). Убедитесь, что `~/.local/bin` в вашем PATH.

**Run from anywhere (CLI):** run `make install-cli` once. Then the `home-server` command will be available from any directory. Ensure `~/.local/bin` is in your PATH.

---

## Windows

На Windows используйте PowerShell:

**Run on Windows (PowerShell):**

```powershell
.\start.ps1
```

Скрипт проверяет наличие **Python 3.10+** и **Node.js 18+**. Если чего-то не хватает — предложит установить (yes/no). При согласии установка выполняется через **winget** (встроен в Windows 10/11). После установки зависимостей перезапустите терминал и снова выполните `.\start.ps1`.

The script checks for Python 3.10+ and Node.js 18+. If something is missing, it will prompt to install (yes/no). If agreed, it uses **winget**. Restart the terminal after installation, then run `.\start.ps1` again.

- Только проверить/установить системные зависимости: `.\scripts\install-deps.ps1`  
- Полная переустановка (venv, node_modules, static): `.\start.ps1 --clean`  
- Установить запуск из любой папки: `.\scripts\install-cli.ps1` — затем можно вызывать `home-server.ps1` из любого места. Удаление: `.\scripts\install-cli.ps1 --uninstall`

---

## Вход по QR и камера / QR login and camera

Страница входа позволяет отсканировать QR‑код с токеном камерой устройства. **Браузер даёт доступ к камере только в безопасном контексте:**

The login page can scan a QR code with the device camera. **Browsers allow camera access only in a secure context:**

- по **HTTPS** (например `https://ваш-сервер:8080`), или  
- с **http://localhost** / **http://127.0.0.1** (доступ с того же компьютера, где запущен сервер).

- over **HTTPS** (e.g. `https://your-server:8080`), or  
- from **http://localhost** / **http://127.0.0.1** (when opening from the same machine where the server runs).

При заходе по **http://IP** (например `http://192.168.1.5:8080`) с телефона или другого ПК камера в браузере недоступна — это ограничение безопасности браузера. В этом случае введите токен вручную в поле на странице входа.

When opening **http://IP** (e.g. `http://192.168.1.5:8080`) from a phone or another PC, the browser will not allow camera access — this is a browser security restriction. In that case, enter the token manually on the login page.

---

## Переменные окружения / Environment variables

Примеры и полное описание: **[server/.env.example](server/.env.example)**.

| Переменная / Variable | Описание / Description |
|------------------------|------------------------|
| `AUTH_REQUIRED` | `true` — доступ по токену, `false` — без авторизации. Если не задано — вопрос в консоли при запуске. |
| `STATIC_DIR` | Путь к папке со сборкой фронта (например `./frontend/build`). Задаётся автоматически в `start.sh`. |
| `SERVER_HOST` | Хост (по умолчанию `0.0.0.0`). |
| `SERVER_PORT` | Порт (по умолчанию `8080`). |
| `LANGUAGE` | Язык консоли: `ru` или `en`. |
| `DEBUG` | `true` — перезагрузка при изменении кода и подробные логи. |
| `SECRET_KEY` | Секретный ключ (обязательно смените в production). |
| `MAX_FILE_SIZE` | Максимальный размер загрузки (например `100MB`). |

Копирование примера в рабочий файл:

Copy the example to your env file:

```bash
cp server/.env.example server/.env
# отредактируйте server/.env при необходимости / edit server/.env if needed
```

---

## Сборка для релиза / Build for release

1. **Только фронтенд** (для разработки с отдельным сервером):

   Frontend only (for development with a separate server):

   ```bash
   cd frontend && npm ci && npm run build
   ```

   Сборка окажется в `frontend/build/`.

2. **Полный запуск (фронт + бэкенд с одной точки):**

   Full run (frontend + backend from one process):

   ```bash
   ./start.sh
   ```

   Либо вручную: собрать фронт (п. 1), затем в `server/.env` задать `STATIC_DIR` (абсолютный путь к `frontend/build`) и `AUTH_REQUIRED`, после чего запустить `python -m src` из папки `server`.

   Or manually: build frontend (step 1), then set `STATIC_DIR` (absolute path to `frontend/build`) and `AUTH_REQUIRED` in `server/.env`, and run `python -m src` from the `server` directory.

---

## Документация / Documentation

- [server/docs/ARCHITECTURE.md](server/docs/ARCHITECTURE.md) — архитектура бэкенда (RU)
- [docs/DEPLOY.ru.md](docs/DEPLOY.ru.md) — сборка и запуск для релиза (RU)
- [docs/DEPLOY.en.md](docs/DEPLOY.en.md) — build and run for release (EN)

---

## Лицензия / License

См. [LICENSE](LICENSE).
