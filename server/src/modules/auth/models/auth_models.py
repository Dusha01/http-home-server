"""
Модели для аутентификации
"""
from datetime import datetime
from typing import Optional, Dict, List
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
    
    # Новые поля для QR
    qr_code: Optional[str] = None
    auth_url: Optional[str] = None


class TokenWithQRResponse(BaseModel):
    """Ответ с токеном и QR-кодом"""
    token: str
    qr_code: str
    auth_url: str
    description: Optional[str] = None
    created_at: datetime


class ValidateTokenResponse(BaseModel):
    """Ответ на проверку токена"""
    valid: bool
    token_data: Optional[TokenData] = None
    message: Optional[str] = None


class ValidateTokenRequest(BaseModel):
    """Запрос на проверку токена"""
    token: str


class RevokeTokenRequest(BaseModel):
    """Запрос на отзыв токена"""
    token: str


class TokenListResponse(BaseModel):
    """Список токенов"""
    tokens: Dict[str, TokenData]
    active_count: int
    expired_count: int = 0
    total_count: int


class TokenDisplayResponse(BaseModel):
    """Ответ для отображения токена при запуске"""
    token: str
    qr_code: str
    auth_url: str
    server_info: Dict[str, str]
    instructions: List[str] = [
        "1. Отсканируйте QR-код камерой телефона",
        "2. Или введите токен вручную",
        "3. Нажмите 'Войти' в веб-интерфейсе",
        "Токен бессрочный, но его можно отозвать"
    ]