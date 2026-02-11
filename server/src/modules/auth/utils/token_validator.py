"""
Валидация токенов
"""
import re
from datetime import datetime
from typing import Optional, Tuple


class TokenValidator:
    """Валидатор токенов"""
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """Проверка формата токена"""
        if len(token) < 16:
            return False
        
        if re.search(r'[^a-zA-Z0-9_\-]', token):
            return False
        
        return True
    

    @classmethod
    def validate_token(
        cls, 
        token: str, 
        token_data: dict
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """Полная валидация токена (без проверки срока действия)"""
        if not cls.validate_token_format(token):
            return False, "Invalid token format", None
        
        if not token_data.get("is_active", True):
            return False, "Token revoked", None
        
        # Обновляем время последнего использования
        token_data["last_used"] = datetime.now().isoformat()
        
        return True, "Token is valid", token_data