"""
Роуты для работы с общими файлами и директориями.
Сервисы и аутентификация через Depends.
"""
import json
import os
import string
from pathlib import Path
from typing import Optional, List

import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, BackgroundTasks, Request
from fastapi.responses import FileResponse, PlainTextResponse

from src.core.config import config
from src.core.dependencies import (
    get_directory_service,
    get_file_service,
    get_download_service,
    get_token_if_required,
    get_optional_token,
)
from src.modules.share.services.directory_service import DirectoryService
from src.modules.share.services.file_service import FileService
from src.modules.share.services.download_service import DownloadService
from src.modules.share.models.file_models import (
    ShareRequest,
    ShareResponse,
    SharedDirectory,
    DirectoryContent,
    FileInfo,
    FileOperationResponse,
    UploadResponse,
    CreateDirectoryRequest,
    RenameRequest,
    DeleteRequest,
    ExplorerRootItem,
    ExplorerDirItem,
    ExplorerListResponse,
    TransmitterRootResponse,
    TransmitterRootRequest,
)
from src.modules.share.utils.file_utils import FileUtils


def create_share_router() -> APIRouter:
    """Роутер файлового обмена (сервисы и токен через Depends)."""
    router = APIRouter(prefix="/share", tags=["files"])

    # ============= УПРАВЛЕНИЕ ОБЩИМИ ПАПКАМИ =============

    @router.post("/directories", response_model=ShareResponse)
    async def add_shared_directory(
        request: ShareRequest,
        directory_service: DirectoryService = Depends(get_directory_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        try:
            directory = directory_service.add_directory(request)
            return ShareResponse(
                success=True,
                message="Directory added successfully",
                directory=directory,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

    @router.get("/directories", response_model=List[SharedDirectory])
    async def list_shared_directories(
        include_inactive: bool = False,
        directory_service: DirectoryService = Depends(get_directory_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        return directory_service.list_directories(include_inactive)

    @router.get("/directories/{dir_id}", response_model=SharedDirectory)
    async def get_shared_directory(
        dir_id: str,
        directory_service: DirectoryService = Depends(get_directory_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        directory = directory_service.get_directory(dir_id)
        if not directory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Directory not found",
            )
        return directory

    @router.delete("/directories/{dir_id}")
    async def remove_shared_directory(
        dir_id: str,
        directory_service: DirectoryService = Depends(get_directory_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        if directory_service.remove_directory(dir_id):
            return {"success": True, "message": "Directory removed"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Directory not found",
        )

    @router.patch("/directories/{dir_id}")
    async def update_shared_directory(
        dir_id: str,
        directory_service: DirectoryService = Depends(get_directory_service),
        is_active: Optional[bool] = None,
        allow_upload: Optional[bool] = None,
        allow_delete: Optional[bool] = None,
        allow_rename: Optional[bool] = None,
        description: Optional[str] = None,
        _: Optional[str] = Depends(get_token_if_required),
    ):
        kwargs = {}
        if is_active is not None:
            kwargs["is_active"] = is_active
        if allow_upload is not None:
            kwargs["allow_upload"] = allow_upload
        if allow_delete is not None:
            kwargs["allow_delete"] = allow_delete
        if allow_rename is not None:
            kwargs["allow_rename"] = allow_rename
        if description is not None:
            kwargs["description"] = description
        updated = directory_service.update_directory(dir_id, **kwargs)
        if updated:
            return updated
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Directory not found",
        )

    # ============= РАБОТА С ФАЙЛАМИ =============

    @router.get("/browse", response_model=DirectoryContent)
    async def browse_directory(
        path: str = Query("/", description="Путь к директории"),
        show_hidden: bool = Query(False, description="Показывать скрытые файлы"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        return await file_service.get_directory_content(path, show_hidden)

    @router.get("/info", response_model=FileInfo)
    async def get_file_info(
        path: str = Query(..., description="Путь к файлу/директории"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        return await file_service.get_file_info(path)

    @router.get("/download")
    async def download_file(
        background_tasks: BackgroundTasks,
        path: str = Query(..., description="Путь к файлу или папке"),
        as_attachment: bool = Query(True, description="Скачать как вложение"),
        download_service: DownloadService = Depends(get_download_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        result = download_service.prepare_download(path)
        if result.cleanup_after_send:
            background_tasks.add_task(os.unlink, str(result.path))
        if as_attachment:
            return FileResponse(
                path=result.path,
                media_type=result.mime_type,
                filename=result.filename,
            )
        return FileResponse(path=result.path, media_type=result.mime_type)

    @router.get("/preview", response_class=PlainTextResponse)
    async def preview_file(
        path: str = Query(..., description="Путь к текстовому файлу"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        """Превью содержимого текстового файла (txt, конфиги, .env и т.д.)."""
        content = await file_service.get_file_content_as_text(path)
        return PlainTextResponse(content)

    @router.post("/update")
    async def update_file(
        request: Request,
        path: str = Query(..., description="Путь к текстовому файлу"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        """Обновление содержимого текстового файла (редактирование)."""
        body = await request.body()
        content = body.decode("utf-8", errors="replace")
        await file_service.update_file_content(path, content)
        return {"success": True}

    @router.post("/upload", response_model=UploadResponse)
    async def upload_file(
        directory: str = Query(..., description="Путь к директории для загрузки"),
        file: UploadFile = File(...),
        overwrite: bool = Query(False, description="Перезаписывать существующий файл"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        result = await file_service.upload_file(directory, file, overwrite)
        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            filename=result["filename"],
            size=result["size"],
            path=result["path"],
        )

    @router.post("/directory")
    async def create_directory(
        request: CreateDirectoryRequest,
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        file_info = await file_service.create_directory(
            request.path,
            request.name,
        )
        return FileOperationResponse(
            success=True,
            message="Directory created successfully",
            data={"file_info": file_info},
        )

    @router.put("/rename")
    async def rename_path(
        request: RenameRequest,
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        file_info = await file_service.rename_path(
            request.old_path,
            request.new_name,
        )
        return FileOperationResponse(
            success=True,
            message="Renamed successfully",
            data={"file_info": file_info},
        )

    @router.delete("/delete")
    async def delete_path(
        request: DeleteRequest,
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        result = await file_service.delete_path(
            request.path,
            request.recursive,
        )
        return FileOperationResponse(
            success=True,
            message="Deleted successfully",
            data=result,
        )

    @router.get("/search")
    async def search_files(
        q: str = Query(..., min_length=2, description="Поисковый запрос"),
        directory_id: Optional[str] = Query(None, description="ID директории для поиска"),
        max_results: int = Query(50, le=200, description="Максимум результатов"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        results = await file_service.search_files(q, directory_id, max_results)
        return {"query": q, "count": len(results), "results": results}

    # ============= ПУБЛИЧНЫЕ ЭНДПОИНТЫ =============

    @router.get("/public/browse", response_model=DirectoryContent)
    async def public_browse_directory(
        path: str = Query("/", description="Путь к директории"),
        show_hidden: bool = Query(False, description="Показывать скрытые файлы"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_optional_token),
    ):
        return await file_service.get_directory_content(path, show_hidden)

    @router.get("/public/download")
    async def public_download_file(
        background_tasks: BackgroundTasks,
        path: str = Query(..., description="Путь к файлу или папке"),
        as_attachment: bool = Query(True, description="Скачать как вложение"),
        download_service: DownloadService = Depends(get_download_service),
        _: Optional[str] = Depends(get_optional_token),
    ):
        result = download_service.prepare_download(path)
        if result.cleanup_after_send:
            background_tasks.add_task(os.unlink, str(result.path))
        return FileResponse(
            path=result.path,
            media_type=result.mime_type,
            filename=result.filename if as_attachment else None,
        )

    @router.get("/public/preview", response_class=PlainTextResponse)
    async def public_preview_file(
        path: str = Query(..., description="Путь к текстовому файлу"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_optional_token),
    ):
        """Превью текстового файла (без обязательной авторизации)."""
        content = await file_service.get_file_content_as_text(path)
        return PlainTextResponse(content)

    @router.post("/public/update")
    async def public_update_file(
        request: Request,
        path: str = Query(..., description="Путь к текстовому файлу"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_optional_token),
    ):
        """Обновление содержимого текстового файла (редактирование, публичный доступ)."""
        body = await request.body()
        content = body.decode("utf-8", errors="replace")
        await file_service.update_file_content(path, content)
        return {"success": True}

    @router.post("/public/upload", response_model=UploadResponse)
    async def public_upload_file(
        directory: str = Query(..., description="Путь к директории для загрузки"),
        file: UploadFile = File(...),
        overwrite: bool = Query(False, description="Перезаписывать существующий файл"),
        file_service: FileService = Depends(get_file_service),
        _: Optional[str] = Depends(get_optional_token),
    ):
        """Загрузка файла в общую директорию (публичный доступ без токена)."""
        result = await file_service.upload_file(directory, file, overwrite)
        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            filename=result["filename"],
            size=result["size"],
            path=result["path"],
        )

    # ============= ПРОВОДНИК (ФАЙЛОВАЯ СИСТЕМА ПК) =============

    @router.get("/explorer/roots", response_model=List[ExplorerRootItem])
    async def explorer_roots(
        _: Optional[str] = Depends(get_token_if_required),
    ):
        """Корневые пункты для выбора папки: диски (Windows) или корень/домашняя папка (Linux)."""
        roots: List[ExplorerRootItem] = []
        if os.name == "nt":
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    roots.append(ExplorerRootItem(path=drive, name=f"Локальный диск ({letter}:)"))
        else:
            roots.append(ExplorerRootItem(path="/", name="Корень системы"))
            try:
                home = str(Path.home())
                if home != "/":
                    roots.append(ExplorerRootItem(path=home, name="Домашняя папка"))
            except RuntimeError:
                pass
        return roots

    @router.get("/explorer/list", response_model=ExplorerListResponse)
    async def explorer_list(
        path: str = Query(..., description="Абсолютный путь к папке на сервере"),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        """Список подпапок по абсолютному пути (файловая система ПК, где запущен сервер)."""
        resolved = Path(path).expanduser().resolve()
        if not resolved.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
        if not resolved.is_dir():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not a directory")
        parent_path: Optional[str] = None
        if resolved.parent != resolved:
            parent_path = str(resolved.parent)
        directories: List[ExplorerDirItem] = []
        try:
            for item in sorted(resolved.iterdir(), key=lambda p: p.name.lower()):
                if item.is_dir():
                    directories.append(ExplorerDirItem(path=str(item), name=item.name))
        except PermissionError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return ExplorerListResponse(
            path=str(resolved),
            parent_path=parent_path,
            directories=directories,
        )

    # ============= ПАПКА ТРАНСЛЯТОРА (ОБЩИЙ КОРЕНЬ ДЛЯ ВСЕХ В СЕТИ) =============

    _transmitter_root_file = config.storage_dir / "transmitter_root_path.json"

    def _read_transmitter_root() -> str:
        if _transmitter_root_file.exists():
            try:
                with open(_transmitter_root_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return (data.get("path") or "/").strip() or "/"
            except (json.JSONDecodeError, OSError):
                pass
        return "/"

    def _write_transmitter_root(path: str) -> None:
        path = (path or "/").strip() or "/"
        with open(_transmitter_root_file, "w", encoding="utf-8") as f:
            json.dump({"path": path}, f, ensure_ascii=False)

    @router.get("/root-path", response_model=TransmitterRootResponse)
    async def get_transmitter_root(
        _: Optional[str] = Depends(get_optional_token),
    ):
        """Путь папки транслятора — доступен всем в сети (с токеном или без)."""
        return TransmitterRootResponse(path=_read_transmitter_root())

    @router.post("/root-path", response_model=TransmitterRootResponse)
    async def set_transmitter_root(
        request: TransmitterRootRequest,
        _: Optional[str] = Depends(get_token_if_required),
    ):
        """Установить папку транслятора (только с авторизацией, обычно с основного сервера)."""
        path = (request.path or "").strip().replace("\\", "/").rstrip("/") or "/"
        if path != "/":
            resolved = Path(path).expanduser().resolve()
            if not resolved.exists():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Path does not exist: {resolved}",
                )
            if not resolved.is_dir():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Path is not a directory",
                )
            path = str(resolved)
        _write_transmitter_root(path)
        return TransmitterRootResponse(path=path)

    # ============= СТАТИСТИКА И КОНФИГУРАЦИЯ =============

    @router.get("/stats")
    async def get_share_stats(
        directory_service: DirectoryService = Depends(get_directory_service),
        _: Optional[str] = Depends(get_token_if_required),
    ):
        dir_stats = directory_service.get_stats()
        if config.storage_dir.exists():
            stat = os.statvfs(str(config.storage_dir))
            free_space = stat.f_frsize * stat.f_bavail
            total_space = stat.f_frsize * stat.f_blocks
            dir_stats["disk"] = {
                "total": total_space,
                "free": free_space,
                "used": total_space - free_space,
                "free_human": FileUtils.format_size(free_space),
                "total_human": FileUtils.format_size(total_space),
            }
        return dir_stats

    @router.get("/config")
    async def get_share_config(
        _: Optional[str] = Depends(get_token_if_required),
    ):
        return {
            "max_upload_size": config.max_file_size,
            "allowed_extensions": config.allowed_extensions_list,
            "preview_supported": list(FileUtils.PREVIEW_EXTENSIONS),
            "image_preview_supported": list(FileUtils.IMAGE_EXTENSIONS),
            "chunk_size": 64 * 1024,
        }

    return router
