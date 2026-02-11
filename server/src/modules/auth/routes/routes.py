"""
Роуты для аутентификации.
Сервис внедряется через Depends(get_auth_service).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.config import config
from src.core.dependencies import get_auth_service
from src.modules.auth.services.auth_service import AuthService
from src.modules.auth.models.auth_models import (
    TokenRequest,
    TokenResponse,
    ValidateTokenRequest,
    ValidateTokenResponse,
    RevokeTokenRequest,
    TokenListResponse,
)


def create_auth_router() -> APIRouter:
    """Роутер аутентификации (без аргументов — сервис через Depends)."""
    router = APIRouter(prefix="/auth", tags=["authentication"])

    @router.post("/token", response_model=TokenResponse)
    async def generate_token(
        request: TokenRequest,
        auth_service: AuthService = Depends(get_auth_service),
    ):
        try:
            token, _ = auth_service.generate_token(description=request.description)
            return TokenResponse(token=token, description=request.description)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate token: {str(e)}",
            )

    @router.post("/token/validate", response_model=ValidateTokenResponse)
    async def validate_token(
        request: ValidateTokenRequest,
        auth_service: AuthService = Depends(get_auth_service),
    ):
        return auth_service.validate_token(request.token)

    @router.post("/token/revoke")
    async def revoke_token(
        request: RevokeTokenRequest,
        auth_service: AuthService = Depends(get_auth_service),
    ):
        if auth_service.revoke_token(request.token):
            return {"success": True, "message": "Token revoked"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )

    @router.get("/tokens", response_model=TokenListResponse)
    async def list_tokens(
        include_inactive: bool = False,
        auth_service: AuthService = Depends(get_auth_service),
    ):
        return auth_service.list_tokens(include_inactive=include_inactive)

    @router.get("/token/{token}")
    async def get_token_info(
        token: str,
        auth_service: AuthService = Depends(get_auth_service),
    ):
        token_info = auth_service.get_token_info(token)
        if token_info:
            return token_info
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )

    @router.post("/cleanup")
    async def cleanup_tokens(
        auth_service: AuthService = Depends(get_auth_service),
    ):
        auth_service.cleanup_inactive()
        return {"success": True, "message": "Inactive tokens cleaned up"}

    @router.get("/stats")
    async def get_auth_stats(
        auth_service: AuthService = Depends(get_auth_service),
    ):
        return auth_service.get_stats()

    @router.get("/config")
    async def get_auth_config():
        return {
            "max_file_size": config.max_file_size,
            "allowed_extensions": config.allowed_extensions_list,
        }

    return router
