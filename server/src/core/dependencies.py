"""
FastAPI Depends: получение сервисов и настроек из app.state.
Роутеры используют Depends(get_*), а не аргументы фабрики.
"""
from typing import Optional

from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.modules.auth.services.auth_service import AuthService
from src.modules.share.services.directory_service import DirectoryService
from src.modules.share.services.file_service import FileService

from src.core.config import config, Settings

_bearer = HTTPBearer(auto_error=False)


def get_config() -> Settings:
    return config


async def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


async def get_directory_service(request: Request) -> DirectoryService:
    return request.app.state.directory_service


async def get_file_service(request: Request) -> FileService:
    return request.app.state.file_service


def get_auth_required(request: Request) -> bool:
    return getattr(request.app.state, "auth_required", True)


async def get_token_if_required(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """
    Если аутентификация отключена — возвращает None.
    Если включена — проверяет Bearer-токен и возвращает его или выбрасывает 401.
    """
    auth_required = getattr(request.app.state, "auth_required", True)
    if not auth_required:
        return None
    if not credentials or credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated" if not credentials else "Use 'Bearer' scheme",
        )
    auth_service: AuthService = request.app.state.auth_service
    result = auth_service.validate_token(credentials.credentials)
    if not result.valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message or "Invalid token",
        )
    if result.token_data and not result.token_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
        )
    return credentials.credentials


async def get_optional_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> Optional[str]:
    """Токен для опциональной аутентификации (публичные эндпоинты). Не выбрасывает 401."""
    if not credentials or credentials.scheme != "Bearer":
        return None
    auth_service: AuthService = request.app.state.auth_service
    result = auth_service.validate_token(credentials.credentials)
    if not result.valid or (result.token_data and not result.token_data.is_active):
        return None
    return credentials.credentials
