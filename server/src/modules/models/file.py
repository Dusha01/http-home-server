"""
Модели для работы с файлами
"""
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel



class FileInfo(BaseModel):
    """Информация о файле"""
    filename: str
    size: int  # в байтах
    upload_date: datetime
    mime_type: Optional[str] = None
    extension: Optional[str] = None
    

    @property
    def size_human(self) -> str:
        """Человекочитаемый размер файла"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024.0:
                return f"{self.size:.2f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.2f} TB"
    

    @classmethod
    def from_path(cls, filepath: Path) -> 'FileInfo':
        """Создает FileInfo из пути к файлу"""
        stat = filepath.stat()
        return cls(
            filename=filepath.name,
            size=stat.st_size,
            upload_date=datetime.fromtimestamp(stat.st_mtime),
            extension=filepath.suffix.lower()[1:] if filepath.suffix else None
        )


class FileListResponse(BaseModel):
    """Ответ со списком файлов"""
    files: list[FileInfo]
    total_count: int
    total_size: int


class UploadRequest(BaseModel):
    """Запрос на загрузку файла"""
    token: str
    overwrite: bool = False