import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from src.modules.auth.utils.token_generate import TokenGenerator
from src.modules.auth.utils.token_validator import TokenValidator
from src.modules.auth.models.auth_models import TokenData, ValidateTokenResponse, TokenListResponse
from src.config import config


class AuthService:
    """Сервис для управления аутентификацией"""
    
    def __init__(self, tokens_file: Path = None):
        self.tokens_file = tokens_file or config.STORAGE_DIR / "tokens.json"
        self.tokens: Dict[str, Dict[str, Any]] = self._load_tokens()
        self.generator = TokenGenerator()
        self.validator = TokenValidator()
    
    def _load_tokens(self) -> Dict[str, Dict[str, Any]]:
        """Загрузка токенов из файла"""
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, 'r') as f:
                    data = json.load(f)
                    return self._convert_tokens_format(data)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    

    def _convert_tokens_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация старых форматов токенов"""
        converted = {}
        for token, token_data in data.items():
            if isinstance(token_data, dict):
                # Убедимся, что нет поля expires_at
                if "expires_at" in token_data:
                    del token_data["expires_at"]
                converted[token] = token_data
        return converted
    

    def _save_tokens(self):
        """Сохранение токенов в файл"""
        with open(self.tokens_file, 'w') as f:
            json.dump(self.tokens, f, indent=2, default=str)
    

    def generate_token(
        self, 
        description: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Генерация нового токена (бессрочного)"""
        token = self.generator.generate_secure_token()
        
        token_data = {
            "created_at": datetime.now().isoformat(),
            "description": description or "",
            "is_active": True,
            "last_used": None
        }
        
        self.tokens[token] = token_data
        self._save_tokens()
        
        return token, token_data
    

    def validate_token(self, token: str) -> ValidateTokenResponse:
        """Проверка валидности токена"""
        if token not in self.tokens:
            return ValidateTokenResponse(
                valid=False,
                message="Token not found"
            )
        
        token_data = self.tokens[token]
        is_valid, message, updated_data = self.validator.validate_token(token, token_data)
        
        if is_valid and updated_data:
            # Обновление данных токена
            self.tokens[token] = updated_data
            self._save_tokens()
            
            return ValidateTokenResponse(
                valid=True,
                token_data=TokenData(**updated_data),
                message=message
            )
        else:
            return ValidateTokenResponse(
                valid=False,
                message=message
            )
    

    def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        if token in self.tokens:
            self.tokens[token]["is_active"] = False
            self.tokens[token]["revoked_at"] = datetime.now().isoformat()
            self._save_tokens()
            return True
        return False
    

    def get_token_info(self, token: str) -> Optional[TokenData]:
        """Получение информации о токене"""
        if token in self.tokens:
            return TokenData(**self.tokens[token])
        return None
    

    def list_tokens(self, include_inactive: bool = False) -> TokenListResponse:
        """Получение списка токенов"""
        active_count = 0
        filtered_tokens = {}
        
        for token_str, token_data in self.tokens.items():
            token_obj = TokenData(**token_data)
            
            if not include_inactive and not token_obj.is_active:
                continue
            
            filtered_tokens[token_str] = token_obj
            
            if token_obj.is_active:
                active_count += 1
        
        return TokenListResponse(
            tokens=filtered_tokens,
            active_count=active_count,
            expired_count=0,  # Всегда 0 для бессрочных токенов
            total_count=len(filtered_tokens)
        )
    

    def cleanup_inactive(self):
        """Очистка отозванных токенов"""
        tokens_to_remove = []
        
        for token, data in self.tokens.items():
            if not data.get("is_active", True):
                tokens_to_remove.append(token)
        
        for token in tokens_to_remove:
            del self.tokens[token]
        
        self._save_tokens()
    
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики по токенам"""
        total = len(self.tokens)
        active = sum(1 for data in self.tokens.values() 
                    if data.get("is_active", True))
        
        return {
            "total_tokens": total,
            "active_tokens": active,
            "inactive_tokens": total - active,
            "storage_file": str(self.tokens_file)
        }