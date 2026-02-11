import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import socket

from src.modules.auth.utils.token_generate import TokenGenerator
from src.modules.auth.utils.token_validator import TokenValidator
from src.modules.auth.utils.qr_utils import QRUtils
from src.modules.auth.models.auth_models import (
    TokenData,
    ValidateTokenResponse,
    TokenListResponse,
    TokenDisplayResponse,
    TokenWithQRResponse,
)
from src.core.config import config


class AuthService:
    """Сервис для управления аутентификацией."""

    def __init__(self, tokens_file: Path = None, server_url: Optional[str] = None):
        self.tokens_file = tokens_file or config.storage_dir / "tokens.json"
        self.tokens: Dict[str, Dict[str, Any]] = self._load_tokens()
        self.generator = TokenGenerator()
        self.validator = TokenValidator()
        self.qr_utils = QRUtils()
        self.server_url = server_url or self._detect_server_url()

    def _detect_server_url(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            port = getattr(config, "server_port", 8080)
            return f"http://{local_ip}:{port}"
        except OSError:
            return "http://localhost:8080"

    def _load_tokens(self) -> Dict[str, Dict[str, Any]]:
        if self.tokens_file.exists():
            try:
                with open(self.tokens_file, "r") as f:
                    data = json.load(f)
                    converted = {}
                    for token, token_data in data.items():
                        if isinstance(token_data, dict):
                            token_data.pop("expires_at", None)
                            if "created_at" not in token_data:
                                token_data["created_at"] = datetime.now().isoformat()
                            converted[token] = token_data
                    return converted
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_tokens(self) -> None:
        with open(self.tokens_file, "w") as f:
            json.dump(self.tokens, f, indent=2, default=str)

    def generate_token(
        self,
        description: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        token = self.generator.generate_secure_token()
        token_data = {
            "created_at": datetime.now().isoformat(),
            "description": description or "",
            "is_active": True,
            "last_used": None,
        }
        self.tokens[token] = token_data
        self._save_tokens()
        return token, token_data

    def generate_initial_token(self) -> TokenDisplayResponse:
        token, _ = self.generate_token(description="Initial server token")
        auth_url = self.qr_utils.generate_auth_url(token, self.server_url)
        qr_code = self.qr_utils.generate_qr_code(auth_url)
        return TokenDisplayResponse(
            token=token,
            qr_code=qr_code,
            auth_url=auth_url,
            server_info={
                "url": self.server_url,
                "hostname": socket.gethostname(),
                "ip": self.server_url.split("//")[1].split(":")[0]
                if "//" in self.server_url
                else "localhost",
            },
        )

    def validate_token(self, token: str) -> ValidateTokenResponse:
        if token not in self.tokens:
            return ValidateTokenResponse(valid=False, message="Token not found")
        token_data = self.tokens[token]
        is_valid, message, updated_data = self.validator.validate_token(
            token, token_data
        )
        if is_valid and updated_data:
            self.tokens[token] = updated_data
            self._save_tokens()
            updated_data_with_token = updated_data.copy()
            updated_data_with_token["token"] = token
            return ValidateTokenResponse(
                valid=True,
                token_data=TokenData(**updated_data_with_token),
                message=message,
            )
        return ValidateTokenResponse(valid=False, message=message)

    def get_token_with_qr(self, token: str) -> Optional[TokenWithQRResponse]:
        if token not in self.tokens:
            return None
        token_data = self.tokens[token]
        auth_url = self.qr_utils.generate_auth_url(token, self.server_url)
        qr_code = self.qr_utils.generate_qr_code(auth_url)
        return TokenWithQRResponse(
            token=token,
            qr_code=qr_code,
            auth_url=auth_url,
            description=token_data.get("description"),
            created_at=datetime.fromisoformat(token_data["created_at"]),
        )

    def get_token_info(self, token: str) -> Optional[TokenData]:
        if token in self.tokens:
            token_data = self.tokens[token].copy()
            token_data["token"] = token
            return TokenData(**token_data)
        return None

    def list_tokens(self, include_inactive: bool = False) -> TokenListResponse:
        active_count = 0
        filtered_tokens = {}
        for token_str, token_data in self.tokens.items():
            if not isinstance(token_data, dict):
                continue
            token_data_copy = token_data.copy()
            if "created_at" not in token_data_copy:
                token_data_copy["created_at"] = datetime.now().isoformat()
            try:
                token_obj = TokenData(token=token_str, **token_data_copy)
                if not include_inactive and not token_obj.is_active:
                    continue
                filtered_tokens[token_str] = token_obj
                if token_obj.is_active:
                    active_count += 1
            except Exception as e:
                print(f"⚠️ Пропуск поврежденного токена {token_str}: {e}")
        return TokenListResponse(
            tokens=filtered_tokens,
            active_count=active_count,
            expired_count=0,
            total_count=len(filtered_tokens),
        )

    def cleanup_inactive(self) -> None:
        to_remove = [t for t, d in self.tokens.items() if not d.get("is_active", True)]
        for token in to_remove:
            del self.tokens[token]
        self._save_tokens()

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.tokens)
        active = sum(1 for d in self.tokens.values() if d.get("is_active", True))
        return {
            "total_tokens": total,
            "active_tokens": active,
            "inactive_tokens": total - active,
            "storage_file": str(self.tokens_file),
        }

    def revoke_token(self, token: str) -> bool:
        if token in self.tokens:
            self.tokens[token]["is_active"] = False
            self._save_tokens()
            return True
        return False
