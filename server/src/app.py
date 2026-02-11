"""
Основное приложение
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from src.config import config
from src.version import __version__

from src.modules.auth.routes.routes import create_auth_router 
#from src.modules.share.routes.share_routes import create_share_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст жизненного цикла приложения"""
    # Startup
    print(f"Starting Home File Server v{__version__}")
    print(f"Server running on http://{config.server_host}:{config.server_port}")
    print(f"Storage directory: {config.storage_dir}")
    print(f"Upload directory: {config.upload_dir}")
    yield
    # Shutdown
    print("Shutting down...")


# Создание приложения
app = FastAPI(
    title="Home File Server",
    description="HTTP сервер для локального обмена файлами",
    version=__version__,
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(create_auth_router())
#app.include_router(create_share_router())


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Home File Server",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth",
            "shares": "/shares",
            "upload": "/upload"
        }
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервера"""
    return {
        "status": "healthy",
        "version": __version__,
        "storage_accessible": config.storage_dir.exists()
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.server_host,
        port=config.server_port,
        reload=config.debug,
        log_level="info" if config.debug else "warning"
    )