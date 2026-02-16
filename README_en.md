# Home File Server

A local HTTP server for file sharing on your home network. Browse, upload, and download files through a web interface with token-based authentication and quick QR code sign-in.

## About the project

**Home File Server** is a lightweight application for secure file sharing on a local network (LAN). Ideal for transferring files between computers and mobile devices without cloud services.

### Features

- **Web interface** — browse directories, preview images and text files, upload and download
- **Token authentication** — access only with a secret token; multiple tokens can be created
- **QR sign-in** — on startup the server displays a QR code; scan it with your phone camera for quick login
- **Shared folders** — configurable list of shared directories with enable/disable support
- **API** — REST API for integration (token generation, file operations)
- **Run modes** — built-in web UI (single port) or separate API + frontend (development mode)

### Tech stack

- **Backend:** FastAPI (Python 3.10+)
- **Frontend:** SvelteKit, Svelte 5
- **Storage:** JSON files (tokens, directory list), file system

---

## Quick start

After cloning the repository, run with a single command:

```bash
./start.sh
```

or via Makefile:

```bash
make run
```

The script will prompt to install missing system dependencies (yes/no). If agreed, Python and Node.js are installed via the system package manager (apt, dnf, pacman, brew). Then project dependencies are installed, frontend is built, and the server starts.

**Web interface:** `http://localhost:8080` (or `http://<IP>:8080` from another device on the network).

On first run without a configured `.env`, the server will ask in the console: **with token (y)** or **without (n)**. For fully non-interactive run, create `server/.env` and set `AUTH_REQUIRED=true` or `AUTH_REQUIRED=false`.

---

## Requirements

- **Node.js** 18+ and **npm**
- **Python** 3.10+

If any are missing, `./start.sh` or `make run` will prompt to install them (yes/no). To only check/install system dependencies: `make install-deps`.

---

## Project structure

```
Home-server/
├── server/              # Backend (FastAPI)
│   ├── src/
│   │   ├── app.py       # Entry point
│   │   ├── core/        # Config, startup
│   │   ├── modules/
│   │   │   ├── auth/    # Authentication, tokens, QR
│   │   │   └── share/   # Files, directories, uploads
│   │   └── i18n.py      # Localization (ru/en)
│   ├── storage/         # tokens.json, shared_directories.json
│   └── requirements.txt
├── frontend/            # SvelteKit SPA
│   ├── src/
│   │   ├── routes/      # /auth/login, /workspace
│   │   └── lib/         # Components, API
│   └── package.json
├── docs/                # Deploy documentation
├── scripts/             # Run and install scripts
├── start.sh             # Main run script
└── Makefile
```

---

## Makefile and CLI

| Command | Description |
|---------|-------------|
| `make run` | Quick start (if already installed — server only; otherwise full install and run). |
| `make run-full` | Full cycle like `./start.sh`. |
| `make run-server` | Server only (venv and static must already be ready). |
| `make install` | Install project dependencies (after `install-deps`: venv, npm, build). |
| `make install-deps` | Check Python and Node.js; prompt to install if missing (yes/no). |
| `make build` | Build frontend and copy to `server/static`. |
| `make dev` | Development mode (server with reload). |
| `make clean` | Remove venv, node_modules, server/static. |
| `make install-cli` | Install `home-server` command in PATH (~/.local/bin). |
| `make uninstall-cli` | Remove `home-server` from PATH. |

**Run from anywhere:** run `make install-cli` once. Then the `home-server` command will be available from any directory. Ensure `~/.local/bin` is in your PATH.

---

## Windows

On Windows use PowerShell:

```powershell
.\start.ps1
```

The script checks for **Python 3.10+** and **Node.js 18+**. If something is missing, it will prompt to install (yes/no). If agreed, installation uses **winget** (built into Windows 10/11). After installing dependencies, restart the terminal and run `.\start.ps1` again.

- Only check/install system dependencies: `.\scripts\install-deps.ps1`
- Full reinstall (venv, node_modules, static): `.\start.ps1 --clean`
- Install run-from-anywhere: `.\scripts\install-cli.ps1` — then you can call `home-server.ps1` from anywhere.

---

## QR sign-in and camera

The login page can scan a QR code with the device camera. **Browsers allow camera access only in a secure context:**

- over **HTTPS** (e.g. `https://your-server:8080`), or
- from **http://localhost** / **http://127.0.0.1** (when opening from the same machine where the server runs).

When opening **http://IP** (e.g. `http://192.168.1.5:8080`) from a phone or another PC, the browser will not allow camera access — this is a browser security restriction. In that case, enter the token manually on the login page.

**Note:** when running with `STATIC_DIR` (built-in web UI), console links automatically use `localhost:<port>` or `<IP>:<port>` of the server. In development mode (separate frontend), `FRONTEND_URL` is used (default `http://localhost:5173`).

---

## Environment variables

Full list: **[server/.env.example](server/.env.example)**.

| Variable | Description |
|----------|-------------|
| `AUTH_REQUIRED` | `true` — token required; `false` — no auth. If unset — console prompt on startup. |
| `STATIC_DIR` | Path to frontend build (e.g. `./frontend/build`). Set automatically by `start.sh`. When set, console links and QR point to the server (`server_host:server_port`). |
| `FRONTEND_URL` | Web UI URL when frontend runs separately (dev). Default `http://localhost:5173`. Ignored when `STATIC_DIR` is set. |
| `SERVER_HOST` | Server host (default `0.0.0.0`). |
| `SERVER_PORT` | Port (default `8080`). |
| `LANGUAGE` | Console language: `ru` or `en`. |
| `DEBUG` | `true` — reload on code change, verbose logs. |
| `SECRET_KEY` | Secret key (change in production). |
| `MAX_FILE_SIZE` | Max upload size (e.g. `100MB`). |

Create env file:

```bash
cp server/.env.example server/.env
# edit server/.env as needed
```

---

## Build for release

1. **Frontend only** (for development with a separate server):

   ```bash
   cd frontend && npm ci && npm run build
   ```

   Output: `frontend/build/`.

2. **Full run (frontend + backend from one process):**

   ```bash
   ./start.sh
   ```

   Or manually: build frontend (step 1), then set `STATIC_DIR` (absolute path to `frontend/build`) and `AUTH_REQUIRED` in `server/.env`, and run `python -m src` from the `server` directory.

---

## Usage examples

### Server start without token
![Server start without token](img/pusk_no_token.png)

### Server start with token
![Server start with token](img/pusk_with_token.png)

### Web interface of shared folder workspace
![Web interface](img/workspace_front.png)

---

## Documentation

- [docs/DEPLOY.en.md](docs/DEPLOY.en.md) — build and run for release
- [README.md](README.md) — Russian documentation

---

## License

See [LICENSE](LICENSE).
