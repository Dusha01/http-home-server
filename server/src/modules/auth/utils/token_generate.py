"""
Генерация токенов
"""
import uuid
import secrets
import string


class TokenGenerator:
    """Генератор токенов"""
    
    @staticmethod
    def generate_uuid_token() -> str:
        return str(uuid.uuid4())
    
    
    @staticmethod
    def generate_random_token(length: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    

    @staticmethod
    def generate_secure_token() -> str:
        return secrets.token_urlsafe(32)