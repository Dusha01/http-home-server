"""
Модели для работы с файлами и директориями
"""
from datetime import datetime
from pathlib import Path
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class FileType(str, Enum):
    """Тип файла"""
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    OTHER = "other"


class FileInfo(BaseModel):
    """Информация о файле/директории"""
    name: str
    path: str
    type: FileType
    size: Optional[int] = None
    modified: Optional[datetime] = None
    created: Optional[datetime] = None
    extension: Optional[str] = None
    is_hidden: bool = False
    is_readable: bool = True
    is_writable: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DirectoryContent(BaseModel):
    """Содержимое директории"""
    current_path: str
    parent_path: Optional[str] = None
    directories: List[FileInfo] = []
    files: List[FileInfo] = []
    total_items: int = 0
    
    @classmethod
    def from_lists(cls, path: str, dirs: List[FileInfo], files: List[FileInfo]):
        """Создание объекта из списков директорий и файлов"""
        parent = str(Path(path).parent) if path != "/" else None
        return cls(
            current_path=path,
            parent_path=parent,
            directories=dirs,
            files=files,
            total_items=len(dirs) + len(files)
        )


class SharedDirectory(BaseModel):
    """Общая директория"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    path: str
    added_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    description: Optional[str] = None
    allow_upload: bool = True
    allow_delete: bool = False
    allow_rename: bool = True


class ShareRequest(BaseModel):
    """Запрос на добавление общей папки"""
    path: str
    description: Optional[str] = None
    allow_upload: bool = True
    allow_delete: bool = False
    allow_rename: bool = True


class ShareResponse(BaseModel):
    """Ответ при добавлении общей папки"""
    success: bool = True
    message: str
    directory: Optional[SharedDirectory] = None


class FileOperationResponse(BaseModel):
    """Ответ на операцию с файлом"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class DownloadRequest(BaseModel):
    """Запрос на скачивание файла"""
    path: str
    as_attachment: bool = True


class UploadResponse(BaseModel):
    """Ответ на загрузку файла"""
    success: bool
    message: str
    filename: str
    size: int
    path: str


class CreateDirectoryRequest(BaseModel):
    """Запрос на создание директории"""
    path: str
    name: str


class RenameRequest(BaseModel):
    """Запрос на переименование"""
    old_path: str
    new_name: str


class DeleteRequest(BaseModel):
    """Запрос на удаление"""
    path: str
    recursive: bool = False