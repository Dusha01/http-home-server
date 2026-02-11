"""
Модели для аутентификации
"""
from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class TokenData(BaseModel):
    """Данные токена"""
    token: str
    created_at: datetime
    description: Optional[str] = None
    is_active: bool = True
    last_used: Optional[datetime] = None
    
    @property
    def is_expired(self) -> bool:
        """Токены не имеют срока действия"""
        return False


class TokenRequest(BaseModel):
    """Запрос на генерацию токена"""
    description: Optional[str] = None


class TokenResponse(BaseModel):
    """Ответ с токеном"""
    success: bool = True
    token: str
    description: Optional[str] = None
    message: str = "Token generated successfully"


class ValidateTokenResponse(BaseModel):
    """Ответ на проверку токена"""
    valid: bool
    token_data: Optional[TokenData] = None
    message: Optional[str] = None


class RevokeTokenRequest(BaseModel):
    """Запрос на отзыв токена"""
    token: str


class TokenListResponse(BaseModel):
    """Список токенов"""
    tokens: Dict[str, TokenData]
    active_count: int
    expired_count: int = 0
    total_count: int