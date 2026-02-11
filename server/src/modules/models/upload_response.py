"""
Модели для ответов при загрузке файлов
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Ответ на успешную загрузку файла"""
    success: bool = True
    filename: str
    size: int
    download_url: str
    message: str = "File uploaded successfully"
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    success: bool = False
    error: str
    code: int
    timestamp: datetime = Field(default_factory=datetime.now)


class TokenResponse(BaseModel):
    """Ответ с токеном"""
    success: bool = True
    token: str
    expires_at: datetime
    message: str = "Token generated successfully"