# Сборка и запуск для релиза (RU)

## Один запуск после клонирования

Из корня репозитория выполните:

```bash
./start.sh
```

Скрипт:

1. Проверяет наличие Node.js, npm и Python (без автоматической установки через пакетный менеджер ОС — при отсутствии выводятся подсказки).
2. При необходимости создаёт виртуальное окружение **`server/.venv`** и устанавливает зависимости (`pip install -r server/requirements.txt`).
3. Устанавливает зависимости фронтенда (`npm ci` в `frontend/`, при отсутствии `package-lock.json` — `npm install`).
4. Собирает фронтенд (`npm run build` → копирование в `server/static`).
5. Запускает сервер с раздачей веб‑интерфейса с того же порта (`STATIC_DIR` указывает на `server/static`).

Веб‑интерфейс: **http://localhost:8080** (или `http://<IP-вашего-ПК>:8080` с другого устройства в сети).

Если в `server/.env` не задан `AUTH_REQUIRED`, при первом запуске в консоли появится вопрос: запускать **с токеном (y)** или **без (n)**. Чтобы скрипт работал без вопросов, создайте `server/.env` и укажите, например:

```env
AUTH_REQUIRED=true
```

---

## Переменные окружения (.env)

Файлы-примеры:

- **Корень проекта:** `.env.example` — краткая справка и отсылка к полному списку.
- **Сервер:** `server/.env.example` — полный список переменных с комментариями на русском и английском.

Создание рабочего файла:

```bash
cp server/.env.example server/.env
# отредактируйте server/.env
```

### Основные переменные (server/.env)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| **AUTH_REQUIRED** | `true` — доступ по токену; `false` — без авторизации. Если не задано — при запуске спрашивается в консоли. | — |
| **STATIC_DIR** | Путь к папке со сборкой фронта. Если задан — API доступен по префиксу `/api`, корень отдаёт веб‑интерфейс (SPA). В `start.sh` задаётся автоматически (каталог `server/static`). | — |
| **SERVER_HOST** | Хост сервера. | `0.0.0.0` |
| **SERVER_PORT** | Порт. | `8080` |
| **LANGUAGE** | Язык консольных сообщений и подсказок: `ru` или `en`. | `ru` |
| **DEBUG** | `true` — перезагрузка при изменении кода, подробные логи. | `false` |
| **SECRET_KEY** | Секретный ключ. В production обязательно смените. | `your-secret-key-change-in-production` |
| **TOKEN_EXPIRY_HOURS** | Срок действия токена в часах. | `24` |
| **MAX_FILE_SIZE** | Максимальный размер загружаемого файла (в байтах или, например, `100MB`, `1GB`). | `104857600` (100 MB) |
| **CORS_ORIGINS** | Разрешённые источники для CORS через запятую. | `*` |

Пути к каталогам (при необходимости):

- **BASE_DIR** — корень приложения (по умолчанию — каталог `server`).
- **STORAGE_DIR** — хранилище данных (по умолчанию `storage` внутри `server`).
- **UPLOAD_DIR** — каталог загрузок (по умолчанию `storage/uploads`).

---

## Сборка вручную (без start.sh)

### 1. Виртуальное окружение Python

```bash
python3 -m venv server/.venv
. server/.venv/bin/activate
pip install -r server/requirements.txt
```

### 2. Фронтенд

```bash
cd frontend
npm ci
npm run build
```

Результат: папка `frontend/build/` (index.html и статика). Скопируйте её в `server/static` или укажите путь к `frontend/build` в `STATIC_DIR`.

### 3. Сервер с раздачей интерфейса

В `server/.env` задайте:

```env
STATIC_DIR=/полный/путь/к/проекту/server/static
AUTH_REQUIRED=true
```

Запуск (из каталога `server`, venv активирован):

```bash
cd server
python -m src
```

Либо экспортируйте переменные в shell:

```bash
cd server
. .venv/bin/activate
export STATIC_DIR="$(pwd)/static"
export AUTH_REQUIRED=true
python -m src
```

---

## Только API (без веб‑интерфейса)

Не задавайте `STATIC_DIR` в `.env`. Запустите сервер из `server` с активированным `server/.venv`:

```bash
cd server
python -m src
```

Корень `http://localhost:8080/` будет отдавать JSON с описанием API; документация — `http://localhost:8080/docs`.

---

## CI и бинарник

При пуше в ветку **main** в GitHub Actions выполняются `pytest` и сборка PyInstaller по `server/home-file-server.spec`.

Локальная сборка бинарника (нужны пакеты из `server/requirements-dev.txt`):

```bash
. server/.venv/bin/activate
pip install -r server/requirements-dev.txt
cd server && pyinstaller home-file-server.spec
```

---

## Требования к системе

- **Node.js** 18+ и **npm**
- **Python** 3.10+

Зависимости Python устанавливаются в **`server/.venv`**.