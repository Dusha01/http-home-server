"""
Middleware для аутентификации
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from src.modules.auth.service.auth_service import AuthService


class TokenAuth(HTTPBearer):
    """Аутентификация по токену"""
    
    def __init__(
        self, 
        auth_service: AuthService = None,
        auto_error: bool = True,
        require_active: bool = True
    ):
        super().__init__(auto_error=auto_error)
        self.auth_service = auth_service or AuthService()
        self.require_active = require_active
    
    
    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            return None
        
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer'"
            )
        
        token = credentials.credentials
        
        validation_result = self.auth_service.validate_token(token)
        
        if not validation_result.valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {validation_result.message}"
            )
        
        if self.require_active and validation_result.token_data:
            if not validation_result.token_data.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token revoked"
                )
        
        return token


class OptionalTokenAuth(TokenAuth):
    """Опциональная аутентификация (для публичных эндпоинтов)"""
    
    def __init__(self, auth_service: AuthService = None):
        super().__init__(auth_service, auto_error=False, require_active=False)