"""
Модели для информации о сервере
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from src.version import __version__, __author__, __description__


class ServerStatus(BaseModel):
    """Статус сервера"""
    status: str = "running"
    version: str = __version__
    uptime: Optional[float] = None  # в секундах
    start_time: datetime = Field(default_factory=datetime.now)
    
    
    @property
    def uptime_human(self) -> Optional[str]:
        """Человекочитаемое время работы"""
        if not self.uptime:
            return None
        
        hours = int(self.uptime // 3600)
        minutes = int((self.uptime % 3600) // 60)
        seconds = int(self.uptime % 60)
        
        return f"{hours}h {minutes}m {seconds}s"


class ServerInfo(BaseModel):
    """Информация о сервере"""
    name: str = "Home File Server"
    description: str = __description__
    author: str = __author__
    version: str = __version__
    host: str
    port: int
    max_file_size: int
    allowed_extensions: list[str]
    storage_path: str