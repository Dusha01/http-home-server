"""
Основное приложение
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import psutil
import qrcode
from io import StringIO

from src.config import config
from src.version import __version__
from src.modules.auth.service.auth_service import AuthService
from src.modules.auth.routes.routes import create_auth_router 
from src.modules.share.routes.routes import create_share_router
from src.modules.share.services.directory_service import DirectoryService
from src.modules.share.services.file_service import FileService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст жизненного цикла приложения"""
    # Startup
    print(f"\n{'='*60}")
    print(f"🚀 Home File Server v{__version__}")
    print(f"{'='*60}")
    print(f"📡 Сервер запущен: http://{config.server_host}:{config.server_port}")
    print(f"💾 Директория хранилища: {config.storage_dir}")
    print(f"📁 Директория загрузок: {config.upload_dir}")
    print(f"{'='*60}\n")
    
    try:
        auth_service = AuthService(
            server_url=f"http://{config.server_host}:{config.server_port}"
        )
        
        dir_service = DirectoryService(
            storage_file=config.storage_dir / "shared_directories.json"
        )
        
        app.state.auth_service = auth_service
        app.state.directory_service = dir_service
        app.state.file_service = FileService(dir_service)
        
        token_count = len(auth_service.tokens)
        
        if token_count == 0:
            token_display = auth_service.generate_initial_token()
            
            print("\n" + "🔐"*30)
            print("🔐 АДМИН-ДОСТУП: ТОКЕН СГЕНЕРИРОВАН")
            print("🔐"*30 + "\n")
            
            print("📋 ТОКЕН (скопируйте для входа):")
            print("-" * 50)
            print(f"\033[1;32m{token_display.token}\033[0m")
            print("-" * 50)
            
            print("\n📱 QR-КОД ДЛЯ БЫСТРОГО ВХОДА:")
            print("-" * 50)
            
            try:          
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=2,
                    border=1
                )
                qr.add_data(token_display.auth_url)
                f = StringIO()
                qr.print_ascii(out=f, invert=False)
                f.seek(0)
                print(f.read())
            except ImportError:
                print(f"📲 QR-код доступен по ссылке:")
                print(f"\033[1;36m{token_display.auth_url}\033[0m")
            except Exception as e:
                print(f"📲 QR-код: {token_display.auth_url}")
            
            print("-" * 50)
            print(f"\n🌐 АДРЕС ДЛЯ ВХОДА:")
            print(f"🔗 {token_display.auth_url}")
            print(f"🏠 Локальный: http://{config.server_host}:{config.server_port}/auth/login")
            
            print("\n📱 ИНСТРУКЦИЯ:")
            for instruction in token_display.instructions:
                print(f"  {instruction}")
            
            print("\n⚠️  ВНИМАНИЕ: Токен будет показан только один раз!")
            print("   Сохраните его в надежном месте.")
            print("\n" + "🔐"*30 + "\n")
            
        else:
            try:
                token_list = auth_service.list_tokens()
                print(f"\n✅ Найдено активных токенов: {token_list.active_count}")
                print(f"📊 Всего токенов: {token_list.total_count}")
            except Exception as e:
                print(f"\n⚠️ Ошибка при загрузке токенов: {e}")
                print(f"📊 Количество токенов в хранилище: {token_count}")
            
            print(f"\n🔗 Страница входа: http://{config.server_host}:{config.server_port}/auth/login")
            print("   Используйте существующий токен или создайте новый через /auth\n")
            
    except Exception as e:
        print(f"⚠️  Предупреждение: {e}")
        print("   Сервис аутентификации временно недоступен\n")
    
    yield
    
    print("\n" + "="*60)
    print("🛑 Сервер остановлен")
    print("="*60 + "\n")


def create_app() -> FastAPI:
    """Фабрика создания приложения"""
    app = FastAPI(
        title="Home File Server",
        description="HTTP сервер для локального обмена файлами с поддержкой QR-аутентификации",
        version=__version__,
        lifespan=lifespan,
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
    
    @app.get("/")
    async def root():
        """Корневой эндпоинт"""
        return {
            "name": "Home File Server",
            "version": __version__,
            "status": "running",
            "endpoints": {
                "web_interface": f"http://{config.server_host}:{config.server_port}/auth/login",
                "documentation": f"http://{config.server_host}:{config.server_port}/docs",
                "api": {
                    "auth": "/auth",
                    "share": "/share",
                    "health": "/health"
                }
            },
            "features": [
                "🔐 Token authentication",
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
    
    return app


app = create_app()

@app.on_event("startup")
async def startup_event():
    """Дополнительные действия при старте"""
    app.include_router(create_auth_router(app.state.auth_service))
    app.include_router(create_share_router(
        app.state.directory_service,
        app.state.file_service
    ))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.server_host,
        port=config.server_port,
        reload=config.debug,
        log_level="debug" if config.debug else "info",
        access_log=config.debug,
        use_colors=True
    )