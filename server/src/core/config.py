"""
Конфигурация приложения (Pydantic Settings).
Пути заданы относительно корня проекта (папка server).
"""
import socket
from typing import Set, List, Optional
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Корень проекта = родитель папки src (server/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Конфигурация приложения через Pydantic."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    base_dir: Path = Field(default_factory=lambda: _PROJECT_ROOT)
    storage_dir: Path = Field(default_factory=lambda: _PROJECT_ROOT / "storage")
    upload_dir: Path = Field(default_factory=lambda: _PROJECT_ROOT / "storage" / "uploads")

    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=8080, ge=1, le=65535)
    # URL фронтенда (страница входа). Используется в QR и в выводе в консоль.
    frontend_url: str = Field(default="http://localhost:5173", description="Frontend (login page) URL, e.g. http://localhost:5173")
    debug: bool = Field(default=False)
    language: str = Field(default="ru", description="UI/console language: ru, en (env: LANGUAGE or LANG)")

    # Если задано — не спрашивать в консоли, использовать это значение. Иначе — интерактивный выбор.
    # If set — skip console prompt and use this value. Otherwise — interactive choice.
    auth_required: Optional[bool] = Field(default=None, description="Require token auth: true/false (env: AUTH_REQUIRED)")
    # Путь к собранному фронтенду (статике). Если задан — API под /api, корень отдаёт SPA.
    # Path to built frontend (static). If set — API under /api, root serves SPA.
    static_dir: Optional[Path] = Field(default=None, description="Path to frontend build (env: STATIC_DIR)")

    secret_key: str = Field(default="your-secret-key-change-in-production")
    token_expiry_hours: int = Field(default=24, ge=1)
    allowed_extensions: Set[str] = Field(
        default={
            "txt", "pdf", "png", "jpg", "jpeg", "gif",
            "doc", "docx", "xls", "xlsx", "zip", "rar",
        },
    )
    max_file_size: int = Field(default=100 * 1024 * 1024, ge=1)  # 100MB
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

    @field_validator("base_dir", "storage_dir", "upload_dir", mode="before")
    @classmethod
    def validate_paths(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("debug", mode="before")
    @classmethod
    def validate_debug(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("auth_required", mode="before")
    @classmethod
    def validate_auth_required(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)

    @field_validator("static_dir", mode="before")
    @classmethod
    def validate_static_dir(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("max_file_size", mode="before")
    @classmethod
    def validate_max_file_size(cls, v):
        if isinstance(v, str):
            v = v.strip().upper()
            multipliers = {
                "KB": 1024,
                "MB": 1024 * 1024,
                "GB": 1024 * 1024 * 1024,
            }
            for suffix, multiplier in multipliers.items():
                if v.endswith(suffix):
                    size = float(v[: -len(suffix)].strip())
                    return int(size * multiplier)
            return int(v)
        return v

    def init_directories(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    @property
    def allowed_extensions_list(self) -> List[str]:
        return list(self.allowed_extensions)

    def _get_local_ip(self) -> str:
        """Определяет LAN IP при бинде на 0.0.0.0."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            return "localhost"

    @property
    def effective_frontend_url(self) -> str:
        """
        URL веб-интерфейса для QR и ссылок в консоли.
        Если STATIC_DIR задан и папка существует — фронт раздаётся с сервера.
        При server_host=0.0.0.0 используется LAN IP (для QR с телефона) или localhost.
        Иначе — отдельный фронт (dev) → frontend_url (например localhost:5173).
        """
        if self.static_dir:
            resolved = self.static_dir.resolve()
            if resolved.is_dir():
                host = self._get_local_ip() if self.server_host == "0.0.0.0" else self.server_host
                return f"http://{host}:{self.server_port}"
        return self.frontend_url.rstrip("/")

    def to_dict(self):
        return self.model_dump()


config = Settings()
config.init_directories()
