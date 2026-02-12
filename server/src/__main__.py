"""
Запуск сервера: python -m src
Если задан AUTH_REQUIRED в .env — использует его; иначе спрашивает в консоли.
"""
from src.app import create_app, _run_with_prompt
from src.core.config import config
import uvicorn

if __name__ == "__main__":
    if config.auth_required is not None:
        app = create_app(auth_required=config.auth_required)
    else:
        app = _run_with_prompt()
    uvicorn.run(
        app,
        host=config.server_host,
        port=config.server_port,
        reload=config.debug,
        log_level="debug" if config.debug else "info",
        access_log=config.debug,
        use_colors=True,
    )
