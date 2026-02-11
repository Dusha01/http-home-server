"""
Запуск сервера: python -m src
Спрашивает в консоли про генерацию токена, затем стартует uvicorn.
"""
from src.app import _run_with_prompt
from src.core.config import config
import uvicorn

if __name__ == "__main__":
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
