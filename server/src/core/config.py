"""
Конфигурация приложения (Pydantic Settings).
Пути заданы относительно корня проекта (папка server).
"""
from typing import Set, List
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
    debug: bool = Field(default=False)
    language: str = Field(default="ru", description="UI/console language: ru, en (env: LANGUAGE or LANG)")

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

    def to_dict(self):
        return self.model_dump()


config = Settings()
config.init_directories()
