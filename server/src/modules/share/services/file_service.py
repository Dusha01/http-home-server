"""
Сервис для операций с файлами в общих директориях
"""
import shutil
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import UploadFile, HTTPException

from src.modules.share.models.file_models import FileInfo, DirectoryContent, SharedDirectory
from src.modules.share.utils.file_utils import FileUtils
from src.modules.share.services.directory_service import DirectoryService


def _default_shared_dir(root_path: Path) -> SharedDirectory:
    """Виртуальная «общая» директория для корня по умолчанию (storage_dir)."""
    return SharedDirectory(
        id="default",
        name=root_path.name or "Storage",
        path=str(root_path.resolve()),
        description="Корневая папка хранилища по умолчанию",
    )


class FileService:
    """Операции с файлами и директориями"""

    def __init__(
        self,
        directory_service: DirectoryService,
        default_root_path: Optional[Path] = None,
    ):
        self.directory_service = directory_service
        self.file_utils = FileUtils()
        self.default_root_path = Path(default_root_path).resolve() if default_root_path else None

    def _resolve_path(self, request_path: str) -> tuple:
        """
        Разрешение запрошенного пути до конкретной общей директории и относительного пути.
        При запросе "/" и отсутствии общих папок используется default_root_path (storage).
        """
        raw = (request_path or "").strip() or "/"
        is_root_request = raw in ("/", "", ".")

        if is_root_request and self.default_root_path:
            default_path = self.default_root_path
            if not default_path.exists():
                default_path.mkdir(parents=True, exist_ok=True)
            if default_path.is_dir():
                virtual = _default_shared_dir(default_path)
                return virtual, Path(""), default_path
            # иначе ищем в обычных общих директориях ниже

        try:
            path = Path(request_path).expanduser().resolve()
        except RuntimeError:
            path = Path(request_path)

        shared_dir = self.directory_service.get_directory_by_path(path)

        # Абсолютный путь с ПК (из настроек/проводника): директория или файл внутри такой папки
        if not shared_dir and path.is_absolute() and path.exists():
            if path.is_dir():
                virtual = SharedDirectory(
                    id="absolute",
                    name=path.name or "Folder",
                    path=str(path),
                    description="Выбранная папка (абсолютный путь)",
                )
                return virtual, Path(""), path
            if path.is_file():
                parent = path.parent
                virtual = SharedDirectory(
                    id="absolute",
                    name=parent.name or "Folder",
                    path=str(parent),
                    description="Выбранная папка (абсолютный путь)",
                )
                try:
                    rel = path.relative_to(parent)
                except ValueError:
                    rel = Path(path.name)
                return virtual, rel, path

        if not shared_dir and self.default_root_path:
            if not self.default_root_path.exists():
                self.default_root_path.mkdir(parents=True, exist_ok=True)
            clean = request_path.strip("/").replace("\\", "/")
            if not clean:
                virtual = _default_shared_dir(self.default_root_path)
                return virtual, Path(""), self.default_root_path
            candidate = (self.default_root_path / clean).resolve()
            try:
                if str(candidate).startswith(str(self.default_root_path)):
                    virtual = _default_shared_dir(self.default_root_path)
                    rel = candidate.relative_to(self.default_root_path)
                    return virtual, rel, candidate
            except ValueError:
                pass

        if not shared_dir:
            raise HTTPException(
                status_code=403,
                detail="Access to this path is not allowed",
            )

        base_path = Path(shared_dir.path).resolve()

        if path == base_path:
            relative_path = Path("")
        else:
            try:
                relative_path = path.relative_to(base_path)
            except ValueError:
                relative_path = Path(str(path)[len(str(base_path)) :].lstrip("/\\"))

        return shared_dir, relative_path, path
    

    async def get_directory_content(
        self, 
        path: str, 
        show_hidden: bool = False
    ) -> DirectoryContent:
        """
        Получение содержимого директории
        
        Args:
            path: Путь к директории
            show_hidden: Показывать скрытые файлы
            
        Returns:
            DirectoryContent: Структурированное содержимое директории
        """
        shared_dir, relative_path, full_path = self._resolve_path(path)
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        base_path = Path(shared_dir.path).resolve()
        directories, files = FileUtils.get_directory_content(
            full_path, base_path, show_hidden
        )

        # Для абсолютного пути (папка из настроек) возвращаем полные пути, чтобы фронт мог переходить по подпапкам.
        # Ограничение «не подниматься выше выбранной папки» реализуется на фронте по сохранённому корню.
        if getattr(shared_dir, "id", None) == "absolute":
            path_str = str(full_path)
            parent_str = str(full_path.parent) if full_path != full_path.parent else None
            dirs_with_paths = [
                FileInfo(**(d.model_dump() | {"path": str(base_path / d.path)}))
                for d in directories
            ]
            files_with_paths = [
                FileInfo(**(f.model_dump() | {"path": str(base_path / f.path)}))
                for f in files
            ]
            return DirectoryContent(
                current_path=path_str,
                parent_path=parent_str,
                directories=dirs_with_paths,
                files=files_with_paths,
                total_items=len(dirs_with_paths) + len(files_with_paths),
            )
        
        path_display = relative_path.as_posix() if str(relative_path) and str(relative_path) != "." else "/"
        return DirectoryContent.from_lists(
            path=path_display,
            dirs=directories,
            files=files
        )
    

    async def get_file_info(self, path: str) -> FileInfo:
        """Получение информации о файле/директории"""
        shared_dir, relative_path, full_path = self._resolve_path(path)
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        base_path = Path(shared_dir.path).resolve()
        file_info = FileUtils.get_file_info(full_path, base_path)
        
        if not file_info:
            raise HTTPException(status_code=500, detail="Could not read file info")
        
        return file_info
    

    async def download_file(self, path: str, chunk_size: int = 64 * 1024):
        """
        Подготовка файла к скачиванию
        
        Args:
            path: Путь к файлу
            chunk_size: Размер чанка для чтения
            
        Returns:
            tuple: (file_path, mime_type, filename)
        """
        shared_dir, relative_path, full_path = self._resolve_path(path)
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        mime_type = FileUtils.get_mime_type(full_path)
        
        return full_path, mime_type, full_path.name

    async def get_file_content_as_text(
        self, path: str, max_size: int = 512 * 1024
    ) -> str:
        """
        Чтение файла как текст для превью (txt, конфиги, .env и т.д.).
        Ограничение размера по умолчанию 512 КБ.
        """
        shared_dir, relative_path, full_path = self._resolve_path(path)
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        if not FileUtils.is_text_previewable(full_path):
            raise HTTPException(
                status_code=400,
                detail="Text preview not supported for this file type",
            )
        size = full_path.stat().st_size
        if size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large for preview (max {max_size // 1024} KB)",
            )
        try:
            raw = full_path.read_bytes()
            return raw.decode("utf-8", errors="replace")
        except (OSError, IOError) as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def upload_file(
        self,
        directory_path: str,
        file: UploadFile,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Загрузка файла в общую директорию
        
        Args:
            directory_path: Путь к директории для загрузки
            file: Загружаемый файл
            overwrite: Перезаписывать существующий файл
            
        Returns:
            Dict: Информация о загруженном файле
        """
        shared_dir, relative_path, full_path = self._resolve_path(directory_path)
        
        if not shared_dir.allow_upload:
            raise HTTPException(
                status_code=403, 
                detail="Uploads are not allowed in this directory"
            )
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")
        
        safe_filename = FileUtils.safe_filename(file.filename)
        
        file_path = full_path / safe_filename
        
        if file_path.exists() and not overwrite:
            file_path = FileUtils.get_unique_filename(full_path, safe_filename)
        
        try:
            content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(content)
            
            base_path = Path(shared_dir.path).resolve()
            file_info = FileUtils.get_file_info(file_path, base_path)
            
            try:
                rel_path = file_path.relative_to(base_path)
            except ValueError:
                rel_path = file_path
            return {
                "filename": file_path.name,
                "path": str(rel_path),
                "size": len(content),
                "mime_type": FileUtils.get_mime_type(file_path),
                "file_info": file_info
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file: {str(e)}"
            )
    

    async def create_directory(
        self, 
        parent_path: str, 
        dir_name: str
    ) -> FileInfo:
        """
        Создание новой директории
        
        Args:
            parent_path: Путь к родительской директории
            dir_name: Имя новой директории
            
        Returns:
            FileInfo: Информация о созданной директории
        """
        shared_dir, relative_path, full_path = self._resolve_path(parent_path)
        
        if not shared_dir.allow_upload:
            raise HTTPException(
                status_code=403,
                detail="Creating directories is not allowed"
            )
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Parent directory not found")
        
        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="Parent path is not a directory")
        
        safe_name = FileUtils.safe_filename(dir_name)
        new_dir_path = full_path / safe_name
        
        if new_dir_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Directory '{safe_name}' already exists"
            )
        
        try:
            new_dir_path.mkdir(parents=True, exist_ok=False)
            
            base_path = Path(shared_dir.path).resolve()
            file_info = FileUtils.get_file_info(new_dir_path, base_path)
            
            if not file_info:
                raise HTTPException(status_code=500, detail="Could not read directory info")
            
            return file_info
        except OSError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create directory: {str(e)}"
            )
    

    async def delete_path(
        self, 
        path: str, 
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Удаление файла или директории
        
        Args:
            path: Путь к удаляемому объекту
            recursive: Рекурсивное удаление для директорий
            
        Returns:
            Dict: Результат операции
        """
        shared_dir, relative_path, full_path = self._resolve_path(path)
        
        if not shared_dir.allow_delete:
            raise HTTPException(
                status_code=403,
                detail="Deletion is not allowed in this directory"
            )
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if Path(shared_dir.path).resolve() == full_path.resolve():
            raise HTTPException(
                status_code=403,
                detail="Cannot delete the root of shared directory"
            )
        
        try:
            if full_path.is_file():
                size = full_path.stat().st_size
                full_path.unlink()
                return {
                    "deleted_path": str(relative_path),
                    "type": "file",
                    "size": size
                }
            else:
                if not recursive:
                    if any(full_path.iterdir()):
                        raise HTTPException(
                            status_code=400,
                            detail="Directory is not empty. Use recursive=True to delete."
                        )
                
                shutil.rmtree(full_path)
                return {
                    "deleted_path": str(relative_path),
                    "type": "directory",
                    "recursive": recursive
                }
        except OSError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete: {str(e)}"
            )
    

    async def rename_path(
        self, 
        old_path: str, 
        new_name: str
    ) -> FileInfo:
        """
        Переименование файла или директории
        
        Args:
            old_path: Текущий путь
            new_name: Новое имя
            
        Returns:
            FileInfo: Информация о переименованном объекте
        """
        shared_dir, relative_path, full_path = self._resolve_path(old_path)
        
        if not shared_dir.allow_rename:
            raise HTTPException(
                status_code=403,
                detail="Renaming is not allowed in this directory"
            )
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if Path(shared_dir.path).resolve() == full_path.resolve():
            raise HTTPException(
                status_code=403,
                detail="Cannot rename the root of shared directory"
            )
        
        safe_name = FileUtils.safe_filename(new_name)
        new_path = full_path.parent / safe_name
        
        if new_path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"'{safe_name}' already exists"
            )
        
        try:
            full_path.rename(new_path)
            
            base_path = Path(shared_dir.path).resolve()
            file_info = FileUtils.get_file_info(new_path, base_path)
            
            if not file_info:
                raise HTTPException(status_code=500, detail="Could not read file info")
            
            return file_info
        except OSError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to rename: {str(e)}"
            )
    

    async def search_files(
        self, 
        query: str,
        directory_id: Optional[str] = None,
        max_results: int = 100
    ) -> List[FileInfo]:
        """
        Поиск файлов по имени
        
        Args:
            query: Поисковый запрос
            directory_id: ID конкретной директории для поиска (опционально)
            max_results: Максимальное количество результатов
            
        Returns:
            List[FileInfo]: Найденные файлы
        """
        results = []
        
        if directory_id:
            directory = self.directory_service.get_directory(directory_id)
            if not directory or not directory.is_active:
                return []
            directories = [directory]
        else:
            directories = self.directory_service.list_directories(include_inactive=False)
        
        query_lower = query.lower()
        
        for directory in directories:
            base_path = Path(directory.path).resolve()
            
            for root, _, files in os.walk(base_path):
                root_path = Path(root)
                
                for file in files:
                    if len(results) >= max_results:
                        break
                    
                    if query_lower in file.lower():
                        file_path = root_path / file
                        file_info = FileUtils.get_file_info(file_path, base_path)
                        if file_info:
                            results.append(file_info)
                
                if len(results) >= max_results:
                    break
        
        return results[:max_results]