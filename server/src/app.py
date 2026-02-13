"""
Точка входа приложения FastAPI.
"""
import os
from contextlib import asynccontextmanager
import uvicorn
import psutil

from src.core.config import config
from src.i18n import set_locale, t
from src.core.startup import (
    print_banner,
    print_token_display,
    print_existing_tokens,
    print_existing_token_with_qr,
    print_no_auth_info,
    print_shutdown,
)
from src.version import __version__
from src.modules.auth.services.auth_service import AuthService
from src.modules.auth.routes.routes import create_auth_router
from src.modules.share.routes.routes import create_share_router
from src.modules.share.services.directory_service import DirectoryService
from src.modules.share.services.file_service import FileService
from src.modules.share.services.download_service import DownloadService
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


@asynccontextmanager
async def lifespan(app: FastAPI, auth_required: bool = True):
    """Контекст жизненного цикла: инициализация сервисов и вывод в консоль."""
    set_locale(config.language)
    print_banner(auth_required)
    try:
        auth_service = AuthService(
            server_url=f"http://{config.server_host}:{config.server_port}",
            frontend_url=config.frontend_url,
        )
        dir_service = DirectoryService(
            storage_file=config.storage_dir / "shared_directories.json",
        )
        app.state.auth_service = auth_service
        app.state.auth_required = auth_required
        app.state.directory_service = dir_service
        file_service = FileService(
            dir_service,
            default_root_path=config.storage_dir,
        )
        app.state.file_service = file_service
        app.state.download_service = DownloadService(file_service)

        token_count = len(auth_service.tokens)
        if not auth_required:
            print_no_auth_info()
        elif token_count == 0:
            token_display = auth_service.generate_initial_token(
                description=t("auth.initial_token_description"),
            )
            print_token_display(token_display)
        else:
            try:
                token_list = auth_service.list_tokens()
                print_existing_tokens(token_list.active_count, token_list.total_count)
                first_active_token = next(
                    (tok for tok, d in auth_service.tokens.items() if d.get("is_active", True)),
                    None,
                )
                if first_active_token:
                    existing = auth_service.get_token_with_qr(first_active_token)
                    if existing:
                        print_existing_token_with_qr(existing)
            except Exception as e:
                print(f"\n⚠️ {t('lifespan.error_tokens', e=e)}")
                print(f"📊 {t('lifespan.tokens_in_storage', count=token_count)}\n")
    except Exception as e:
        print(f"⚠️  {t('lifespan.warning', e=e)}")
        print(f"   {t('lifespan.auth_unavailable')}\n")

    api_prefix = "/api" if config.static_dir else ""
    app.include_router(create_auth_router(), prefix=api_prefix)
    app.include_router(create_share_router(), prefix=api_prefix)

    yield
    print_shutdown()


def create_app(auth_required: bool = True) -> FastAPI:
    """Фабрика создания приложения. auth_required задаётся при запуске (консольный вопрос)."""
    @asynccontextmanager
    async def _lifespan(app: FastAPI):
        async with lifespan(app, auth_required):
            yield

    app = FastAPI(
        title="Home File Server",
        description="HTTP сервер для локального обмена файлами с поддержкой QR-аутентификации",
        version=__version__,
        lifespan=_lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    config.storage_dir.mkdir(parents=True, exist_ok=True)
    config.upload_dir.mkdir(parents=True, exist_ok=True)

    static_resolved = config.static_dir.resolve() if config.static_dir else None
    if not static_resolved or not static_resolved.is_dir():
        @app.get("/")
        async def root():
            """Корневой эндпоинт (доступен без токена для проверки auth_required)"""
            auth_required = getattr(app.state, "auth_required", True)
            base = f"http://{config.server_host}:{config.server_port}"
            auth_prefix = "/api" if static_resolved else ""
            login_page = f"{config.frontend_url.rstrip('/')}/auth/login" if not (static_resolved and static_resolved.is_dir()) else f"{base}{auth_prefix}/auth/login"
            return {
                "name": "Home File Server",
                "version": __version__,
                "status": "running",
                "auth_required": auth_required,
                "endpoints": {
                    "web_interface": login_page,
                    "documentation": f"{base}/docs",
                    "api": {
                        "auth": f"{auth_prefix}/auth",
                        "share": f"{auth_prefix}/share",
                        "health": "/health"
                    }
                },
                "features": [
                    "🔐 Token authentication" if auth_required else "🔓 No authentication",
                    "📱 QR code login",
                    "📁 File sharing",
                    "📤 File upload",
                    "📥 File download",
                    "📂 Directory browsing",
                    "🔍 Search files"
                ]
            }

    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервера"""
    
        process = psutil.Process(os.getpid())
        
        health_status = {
            "status": "healthy",
            "version": __version__,
            "timestamp": None,
            "services": {
                "storage": config.storage_dir.exists(),
                "auth": hasattr(app.state, 'auth_service'),
                "share": hasattr(app.state, 'directory_service')
            },
            "system": {
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "connections": len(process.connections())
            }
        }
        
        from datetime import datetime
        health_status["timestamp"] = datetime.now().isoformat()

        return health_status

    # Режим релиза: отдаём собранный фронтенд (SPA) с корня
    if static_resolved and static_resolved.is_dir():
        index_path = static_resolved / "index.html"
        if index_path.exists():
            @app.get("/{full_path:path}")
            async def serve_spa(full_path: str):
                if full_path.startswith("api/") or full_path == "api":
                    from fastapi import HTTPException
                    raise HTTPException(404)
                path = (static_resolved / full_path).resolve()
                if path.is_file() and path.exists():
                    try:
                        path.relative_to(static_resolved)
                    except ValueError:
                        from fastapi import HTTPException
                        raise HTTPException(404)
                    return FileResponse(path)
                return FileResponse(index_path)

    return app


def _run_with_prompt():
    """Запуск с вопросом в консоли: генерировать токен аутентификации или нет."""
    set_locale(config.language)
    print(f"\n🔐 {t('prompt.setup')}\n")
    while True:
        answer = input(t("prompt.question")).strip().lower()
        if answer in ("y", "yes", "д", "да"):
            auth_required = True
            break
        if answer in ("n", "no", "н", "нет"):
            auth_required = False
            break
        print(t("prompt.invalid"))
    return create_app(auth_required=auth_required)


app = create_app(auth_required=True)


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