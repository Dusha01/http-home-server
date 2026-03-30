# Build and run for release (EN)

## One-command run after cloning

From the repository root run:

```bash
./start.sh
```

The script will:

1. Check for Node.js, npm, and Python (it does **not** auto-install them via the OS package manager — if missing, it prints hints).
2. Create **`server/.venv`** if needed and install dependencies (`pip install -r server/requirements.txt`).
3. Install frontend dependencies (`npm ci` in `frontend/`, or `npm install` if there is no lockfile).
4. Build the frontend and deploy it to `server/static`.
5. Start the server and serve the web UI from the same port (`STATIC_DIR` points at `server/static`).

Web UI: **http://localhost:8080** (or `http://<your-PC-IP>:8080` from another device on the network).

If `AUTH_REQUIRED` is not set in `server/.env`, the first run will prompt in the console: **with token (y)** or **without (n)**. To run non-interactively, create `server/.env` and set, for example:

```env
AUTH_REQUIRED=true
```

---

## Environment variables (.env)

Example files:

- **Project root:** `.env.example` — short reference and link to the full list.
- **Server:** `server/.env.example` — full list of variables with comments in Russian and English.

Create your env file:

```bash
cp server/.env.example server/.env
# edit server/.env as needed
```

### Main variables (server/.env)

| Variable | Description | Default |
|----------|-------------|---------|
| **AUTH_REQUIRED** | `true` — token required; `false` — no auth. If unset — console prompt on startup. | — |
| **STATIC_DIR** | Path to the frontend build directory. When set — API is under `/api`, root serves the web UI (SPA). Set automatically by `start.sh` (`server/static`). | — |
| **SERVER_HOST** | Server host. | `0.0.0.0` |
| **SERVER_PORT** | Port. | `8080` |
| **LANGUAGE** | Console and prompt language: `ru` or `en`. | `ru` |
| **DEBUG** | `true` — reload on code change, verbose logs. | `false` |
| **SECRET_KEY** | Secret key. Change in production. | `your-secret-key-change-in-production` |
| **TOKEN_EXPIRY_HOURS** | Token validity in hours. | `24` |
| **MAX_FILE_SIZE** | Max upload size (bytes or e.g. `100MB`, `1GB`). | `104857600` (100 MB) |
| **CORS_ORIGINS** | Allowed CORS origins, comma-separated. | `*` |

Optional paths:

- **BASE_DIR** — application root (default: `server` directory).
- **STORAGE_DIR** — data storage (default: `storage` inside `server`).
- **UPLOAD_DIR** — uploads directory (default: `storage/uploads`).

---

## Manual build (without start.sh)

### 1. Python virtual environment

```bash
python3 -m venv server/.venv
. server/.venv/bin/activate
pip install -r server/requirements.txt
```

### 2. Frontend

```bash
cd frontend
npm ci
npm run build
```

Output: `frontend/build/` (index.html and assets). Copy to `server/static` or point `STATIC_DIR` at `frontend/build`.

### 3. Server serving the UI

In `server/.env` set:

```env
STATIC_DIR=/full/path/to/project/server/static
AUTH_REQUIRED=true
```

Then run from `server` with `server/.venv` activated:

```bash
cd server
python -m src
```

Or export variables:

```bash
cd server
. .venv/bin/activate
export STATIC_DIR="$(pwd)/static"
export AUTH_REQUIRED=true
python -m src
```

---

## API only (no web UI)

Do not set `STATIC_DIR` in `.env`. Start the server from `server` with `server/.venv` activated:

```bash
cd server
python -m src
```

Root `http://localhost:8080/` returns API info JSON; docs at `http://localhost:8080/docs`.

---

## CI and binary

On push to **main**, GitHub Actions runs `pytest` and PyInstaller using `server/home-file-server.spec`.

Local binary build (requires `server/requirements-dev.txt`):

```bash
. server/.venv/bin/activate
pip install -r server/requirements-dev.txt
cd server && pyinstaller home-file-server.spec
```

---

## System requirements

- **Node.js** 18+ and **npm**
- **Python** 3.10+

Python dependencies are installed into **`server/.venv`**.