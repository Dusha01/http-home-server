"""
Роуты для работы с общими файлами и директориями
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from typing import Optional, List
import os

from src.config import config
from src.modules.share.services.directory_service import DirectoryService
from src.modules.share.services.file_service import FileService
from src.modules.share.models.file_models import (
    ShareRequest, ShareResponse, SharedDirectory,
    DirectoryContent, FileInfo, FileOperationResponse,
    UploadResponse, CreateDirectoryRequest, RenameRequest,
    DeleteRequest
)
from src.modules.auth.middleware import TokenAuth
from src.modules.share.utils.file_utils import FileUtils



def create_share_router(
    directory_service: DirectoryService = None,
    file_service: FileService = None
) -> APIRouter:
    """
    Создание роутера для работы с файлами
    
    Args:
        directory_service: Сервис управления общими папками
        file_service: Сервис работы с файлами
    """
    router = APIRouter(prefix="/share", tags=["files"])
    
    # Инициализация сервисов
    if directory_service is None:
        directory_service = DirectoryService(
            storage_file=config.storage_dir / "shared_directories.json"
        )
    
    if file_service is None:
        file_service = FileService(directory_service)
    
    token_auth = TokenAuth(require_active=True)
    optional_token_auth = TokenAuth(auto_error=False, require_active=False)
    

    # ============= УПРАВЛЕНИЕ ОБЩИМИ ПАПКАМИ =============
    

    @router.post("/directories", response_model=ShareResponse)
    async def add_shared_directory(
        request: ShareRequest,
        _=Depends(token_auth)
    ):
        """Добавление новой общей директории"""
        try:
            directory = directory_service.add_directory(request)
            return ShareResponse(
                success=True,
                message="Directory added successfully",
                directory=directory
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    

    @router.get("/directories", response_model=List[SharedDirectory])
    async def list_shared_directories(
        include_inactive: bool = False,
        _=Depends(token_auth)
    ):
        """Получение списка общих директорий"""
        return directory_service.list_directories(include_inactive)
    

    @router.get("/directories/{dir_id}", response_model=SharedDirectory)
    async def get_shared_directory(
        dir_id: str,
        _=Depends(token_auth)
    ):
        """Получение информации об общей директории"""
        directory = directory_service.get_directory(dir_id)
        if not directory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Directory not found"
            )
        return directory
    

    @router.delete("/directories/{dir_id}")
    async def remove_shared_directory(
        dir_id: str,
        _=Depends(token_auth)
    ):
        """Удаление общей директории из списка"""
        if directory_service.remove_directory(dir_id):
            return {"success": True, "message": "Directory removed"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Directory not found"
            )
    

    @router.patch("/directories/{dir_id}")
    async def update_shared_directory(
        dir_id: str,
        is_active: Optional[bool] = None,
        allow_upload: Optional[bool] = None,
        allow_delete: Optional[bool] = None,
        allow_rename: Optional[bool] = None,
        description: Optional[str] = None,
        _=Depends(token_auth)
    ):
        """Обновление параметров общей директории"""
        kwargs = {}
        if is_active is not None:
            kwargs['is_active'] = is_active
        if allow_upload is not None:
            kwargs['allow_upload'] = allow_upload
        if allow_delete is not None:
            kwargs['allow_delete'] = allow_delete
        if allow_rename is not None:
            kwargs['allow_rename'] = allow_rename
        if description is not None:
            kwargs['description'] = description
        
        updated = directory_service.update_directory(dir_id, **kwargs)
        if updated:
            return updated
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Directory not found"
            )
    

    # ============= РАБОТА С ФАЙЛАМИ =============
    

    @router.get("/browse", response_model=DirectoryContent)
    async def browse_directory(
        path: str = Query("/", description="Путь к директории"),
        show_hidden: bool = Query(False, description="Показывать скрытые файлы"),
        _=Depends(token_auth)  # Обязательная аутентификация
    ):
        """Просмотр содержимого директории"""
        return await file_service.get_directory_content(path, show_hidden)
    

    @router.get("/info", response_model=FileInfo)
    async def get_file_info(
        path: str = Query(..., description="Путь к файлу/директории"),
        _=Depends(token_auth)
    ):
        """Получение информации о файле или директории"""
        return await file_service.get_file_info(path)
    

    @router.get("/download")
    async def download_file(
        path: str = Query(..., description="Путь к файлу"),
        as_attachment: bool = Query(True, description="Скачать как вложение"),
        _=Depends(token_auth)
    ):
        """Скачивание файла"""
        file_path, mime_type, filename = await file_service.download_file(path)
        
        if as_attachment:
            return FileResponse(
                path=file_path,
                media_type=mime_type,
                filename=filename
            )
        else:
            # Для предпросмотра в браузере
            return FileResponse(
                path=file_path,
                media_type=mime_type
            )
    

    @router.post("/upload", response_model=UploadResponse)
    async def upload_file(
        directory: str = Query(..., description="Путь к директории для загрузки"),
        file: UploadFile = File(...),
        overwrite: bool = Query(False, description="Перезаписывать существующий файл"),
        _=Depends(token_auth)
    ):
        """Загрузка файла на сервер"""
        result = await file_service.upload_file(directory, file, overwrite)
        
        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            filename=result["filename"],
            size=result["size"],
            path=result["path"]
        )
    

    @router.post("/directory")
    async def create_directory(
        request: CreateDirectoryRequest,
        _=Depends(token_auth)
    ):
        """Создание новой директории"""
        file_info = await file_service.create_directory(
            request.path, 
            request.name
        )
        
        return FileOperationResponse(
            success=True,
            message="Directory created successfully",
            data={"file_info": file_info}
        )
    

    @router.put("/rename")
    async def rename_path(
        request: RenameRequest,
        _=Depends(token_auth)
    ):
        """Переименование файла или директории"""
        file_info = await file_service.rename_path(
            request.old_path,
            request.new_name
        )
        
        return FileOperationResponse(
            success=True,
            message="Renamed successfully",
            data={"file_info": file_info}
        )
    

    @router.delete("/delete")
    async def delete_path(
        request: DeleteRequest,
        _=Depends(token_auth)
    ):
        """Удаление файла или директории"""
        result = await file_service.delete_path(
            request.path,
            request.recursive
        )
        
        return FileOperationResponse(
            success=True,
            message="Deleted successfully",
            data=result
        )
    

    @router.get("/search")
    async def search_files(
        q: str = Query(..., min_length=2, description="Поисковый запрос"),
        directory_id: Optional[str] = Query(None, description="ID директории для поиска"),
        max_results: int = Query(50, le=200, description="Максимум результатов"),
        _=Depends(token_auth)
    ):
        """Поиск файлов по имени"""
        results = await file_service.search_files(q, directory_id, max_results)
        
        return {
            "query": q,
            "count": len(results),
            "results": results
        }
    

    # ============= ПУБЛИЧНЫЕ ЭНДПОИНТЫ (ОПЦИОНАЛЬНАЯ АУТЕНТИФИКАЦИЯ) =============
    

    @router.get("/public/browse", response_model=DirectoryContent)
    async def public_browse_directory(
        path: str = Query("/", description="Путь к директории"),
        show_hidden: bool = Query(False, description="Показывать скрытые файлы"),
        _=Depends(optional_token_auth)
    ):
        """
        Публичный просмотр содержимого директории
        (с опциональной аутентификацией для гостевого доступа)
        """
        return await file_service.get_directory_content(path, show_hidden)
    

    @router.get("/public/download")
    async def public_download_file(
        path: str = Query(..., description="Путь к файлу"),
        as_attachment: bool = Query(True, description="Скачать как вложение"),
        _=Depends(optional_token_auth)
    ):
        """
        Публичное скачивание файла
        (с опциональной аутентификацией для гостевого доступа)
        """
        file_path, mime_type, filename = await file_service.download_file(path)
        
        return FileResponse(
            path=file_path,
            media_type=mime_type,
            filename=filename if as_attachment else None
        )
    

    # ============= СТАТИСТИКА И КОНФИГУРАЦИЯ =============
    

    @router.get("/stats")
    async def get_share_stats(_=Depends(token_auth)):
        """Получение статистики по общим папкам и файлам"""
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
                "total_human": FileUtils.format_size(total_space)
            }
        
        return dir_stats
    
    @router.get("/config")
    async def get_share_config(_=Depends(token_auth)):
        """Получение конфигурации модуля"""
        return {
            "max_upload_size": config.MAX_FILE_SIZE,
            "allowed_extensions": list(config.ALLOWED_EXTENSIONS),
            "preview_supported": list(FileUtils.PREVIEW_EXTENSIONS),
            "image_preview_supported": list(FileUtils.IMAGE_EXTENSIONS),
            "chunk_size": 64 * 1024  # 64KB
        }
    
    return router