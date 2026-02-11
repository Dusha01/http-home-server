from typing import Set, List
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    """Конфигурация приложения через Pydantic"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Базовые пути
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    storage_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "storage")
    upload_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent / "storage" / "uploads")
    
    # Настройки сервера
    server_host: str = Field(default="0.0.0.0")
    server_port: int = Field(default=8080, ge=1, le=65535)
    debug: bool = Field(default=False)
    
    # Настройки безопасности
    secret_key: str = Field(default="your-secret-key-change-in-production")
    token_expiry_hours: int = Field(default=24, ge=1)
    allowed_extensions: Set[str] = Field(
        default={
            'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
            'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'
        }
    )
    max_file_size: int = Field(default=100 * 1024 * 1024, ge=1)  # 100MB
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    

    @field_validator("base_dir", "storage_dir", "upload_dir", mode="before")
    @classmethod
    def validate_paths(cls, v):
        """Валидация и преобразование путей"""
        if isinstance(v, str):
            return Path(v)
        return v
    

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, v):
        """Преобразование строки CORS origins в список"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    

    @field_validator("debug", mode="before")
    @classmethod
    def validate_debug(cls, v):
        """Преобразование строки в булево значение для debug"""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    

    @field_validator("max_file_size", mode="before")
    @classmethod
    def validate_max_file_size(cls, v):
        """Преобразование строки с суффиксами размера файла"""
        if isinstance(v, str):
            v = v.strip().upper()
            multipliers = {
                "KB": 1024,
                "MB": 1024 * 1024,
                "GB": 1024 * 1024 * 1024,
            }
            
            for suffix, multiplier in multipliers.items():
                if v.endswith(suffix):
                    size = float(v[:-len(suffix)].strip())
                    return int(size * multiplier)
            
            return int(v)
        return v
    

    def init_directories(self):
        """Создание необходимых директорий"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(exist_ok=True)
    

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Возвращает список разрешенных расширений для удобства"""
        return list(self.allowed_extensions)
    

    def to_dict(self):
        """Возвращает конфигурацию в виде словаря"""
        return self.model_dump()



# Создание глобального экземпляра настроек
config = Settings()

# Инициализация директорий при загрузке модуля
config.init_directories()