"""
Роуты для аутентификации
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.modules.auth.service.auth_service import AuthService
from src.modules.auth.models.auth_models import (
    TokenRequest, 
    TokenResponse, 
    ValidateTokenResponse,
    RevokeTokenRequest,
    TokenListResponse
)
from src.config import config


def create_auth_router(auth_service: AuthService = None) -> APIRouter:
    """Создание роутера для аутентификации"""
    router = APIRouter(prefix="/auth", tags=["authentication"])
    
    if auth_service is None:
        auth_service = AuthService()
    

    @router.post("/token", response_model=TokenResponse)
    async def generate_token(request: TokenRequest):
        """Генерация нового токена доступа"""
        try:
            token, token_data = auth_service.generate_token(
                description=request.description
            )
            
            return TokenResponse(
                token=token,
                description=request.description
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate token: {str(e)}"
            )
    

    @router.post("/token/validate", response_model=ValidateTokenResponse)
    async def validate_token(token: str):
        """Проверка валидности токена"""
        return auth_service.validate_token(token)
    

    @router.post("/token/revoke")
    async def revoke_token(request: RevokeTokenRequest):
        """Отзыв токена"""
        if auth_service.revoke_token(request.token):
            return {"success": True, "message": "Token revoked"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found"
            )
    

    @router.get("/tokens", response_model=TokenListResponse)
    async def list_tokens(
        include_inactive: bool = False
    ):
        """Получение списка токенов"""
        return auth_service.list_tokens(include_inactive=include_inactive)
    

    @router.get("/token/{token}")
    async def get_token_info(token: str):
        """Получение информации о конкретном токене"""
        token_info = auth_service.get_token_info(token)
        if token_info:
            return token_info
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found"
            )
    

    @router.post("/cleanup")
    async def cleanup_tokens():
        """Очистка отозванных токенов"""
        auth_service.cleanup_inactive()
        return {"success": True, "message": "Inactive tokens cleaned up"}
    

    @router.get("/stats")
    async def get_auth_stats():
        """Получение статистики аутентификации"""
        return auth_service.get_stats()
    

    @router.get("/config")
    async def get_auth_config():
        """Получение конфигурации аутентификации"""
        return {
            "max_file_size": config.MAX_FILE_SIZE,
            "allowed_extensions": list(config.ALLOWED_EXTENSIONS)
        }
    
    return router