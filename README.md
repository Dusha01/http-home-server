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

Скрипт установит зависимости (Node.js, npm, Python), соберёт фронтенд и запустит сервер. Веб‑интерфейс будет доступен по адресу `http://localhost:8080` (или `http://<IP>:8080` с другого устройства в сети).

The script installs dependencies (Node.js, npm, Python), builds the frontend and starts the server. The web UI will be at `http://localhost:8080` (or `http://<IP>:8080` from another device on the network).

При первом запуске без настроенного `.env` скрипт не задаёт режим аутентификации — сервер спросит в консоли: **с токеном (y)** или **без (n)**. Чтобы запуск был полностью без вопросов, создайте `server/.env` и задайте `AUTH_REQUIRED=true` или `AUTH_REQUIRED=false`.

On first run without a `.env` file, the server will ask in the console: **with token (y)** or **without (n)**. For a fully non-interactive run, create `server/.env` and set `AUTH_REQUIRED=true` or `AUTH_REQUIRED=false`.

---

## Требования / Requirements

- **Node.js** 18+ и **npm**
- **Python** 3.10+

Если чего‑то не хватает, `./start.sh` подскажет команды установки для вашей ОС.

If any of these are missing, `./start.sh` will suggest install commands for your OS.

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
