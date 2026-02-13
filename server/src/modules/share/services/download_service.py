"""
Сервис скачивания файлов и папок.
"""
import os
import tempfile
import zipfile
from pathlib import Path
from dataclasses import dataclass

from fastapi import HTTPException

from src.modules.share.services.file_service import FileService
from src.modules.share.utils.file_utils import FileUtils


@dataclass
class DownloadResult:
    """Результат подготовки к скачиванию."""
    path: Path
    mime_type: str
    filename: str
    cleanup_after_send: bool = False


class DownloadService:
    """Сервис скачивания файлов и директорий."""

    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def prepare_download(self, path: str) -> DownloadResult:
        """
        Подготовка к скачиванию: файл или папка (zip).
        Для папок создаётся временный zip-архив.

        Args:
            path: Путь к файлу или папке

        Returns:
            DownloadResult: путь, mime_type, filename. Для папок cleanup_after_send=True.
        """
        shared_dir, relative_path, full_path = self.file_service.resolve_path(path)

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if full_path.is_file():
            mime_type = FileUtils.get_mime_type(full_path)
            return DownloadResult(
                path=full_path,
                mime_type=mime_type,
                filename=full_path.name,
                cleanup_after_send=False,
            )

        if full_path.is_dir():
            return self._prepare_folder_download(full_path)

        raise HTTPException(status_code=400, detail="Path is neither a file nor a directory")

    def _prepare_folder_download(self, folder_path: Path) -> DownloadResult:
        """Создаёт zip-архив папки во временном файле."""
        folder_name = folder_path.name or "folder"
        zip_filename = f"{folder_name}.zip"

        fd, zip_path_str = tempfile.mkstemp(suffix=".zip", prefix="download_")
        try:
            os.close(fd)
            zip_path = Path(zip_path_str)
            self._create_zip_archive(folder_path, zip_path)
            return DownloadResult(
                path=zip_path,
                mime_type="application/zip",
                filename=zip_filename,
                cleanup_after_send=True,
            )
        except Exception:
            if os.path.exists(zip_path_str):
                try:
                    os.unlink(zip_path_str)
                except OSError:
                    pass
            raise HTTPException(
                status_code=500,
                detail="Failed to create zip archive",
            )

    def _create_zip_archive(self, source_dir: Path, zip_path: Path) -> None:
        """Рекурсивно добавляет содержимое папки в zip-архив."""
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in source_dir.rglob("*"):
                if item.is_file():
                    try:
                        arcname = item.relative_to(source_dir)
                        zf.write(item, arcname=arcname)
                    except (ValueError, OSError, PermissionError):
                        continue
