"""
Сервис для управления общими директориями
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from threading import Lock

from src.modules.share.models.file_models import SharedDirectory, ShareRequest


class DirectoryService:
    """Управление общими директориями"""
    
    def __init__(self, storage_file: Path):
        """
        Инициализация сервиса
        
        Args:
            storage_file: Путь к файлу для хранения списка общих папок
        """
        self.storage_file = storage_file
        self.directories: Dict[str, SharedDirectory] = {}
        self.lock = Lock()
        self._load_directories()
    
    def _load_directories(self):
        """Загрузка списка общих папок из файла"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    for dir_id, dir_data in data.items():
                        # Конвертируем строку datetime обратно в объект
                        if 'added_at' in dir_data:
                            dir_data['added_at'] = datetime.fromisoformat(dir_data['added_at'])
                        self.directories[dir_id] = SharedDirectory(**dir_data)
            except (json.JSONDecodeError, IOError, ValueError):
                # Если файл поврежден, начинаем с пустого списка
                pass
    
    def _save_directories(self):
        """Сохранение списка общих папок в файл"""
        with self.lock:
            data = {}
            for dir_id, directory in self.directories.items():
                # Конвертируем datetime в строку для JSON
                dir_dict = directory.model_dump()
                if isinstance(dir_dict['added_at'], datetime):
                    dir_dict['added_at'] = dir_dict['added_at'].isoformat()
                data[dir_id] = dir_dict
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
    
    def add_directory(self, request: ShareRequest) -> SharedDirectory:
        """
        Добавление новой общей директории
        
        Args:
            request: Запрос на добавление папки
            
        Returns:
            SharedDirectory: Добавленная директория
            
        Raises:
            ValueError: Если путь не существует или не является директорией
        """
        path = Path(request.path).expanduser().resolve()
        
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        # Проверяем, не добавлена ли уже эта директория
        for directory in self.directories.values():
            if Path(directory.path).resolve() == path:
                raise ValueError(f"Directory already shared: {path}")
        
        directory = SharedDirectory(
            path=str(path),
            name=path.name,
            description=request.description,
            allow_upload=request.allow_upload,
            allow_delete=request.allow_delete,
            allow_rename=request.allow_rename
        )
        
        self.directories[directory.id] = directory
        self._save_directories()
        
        return directory
    
    def remove_directory(self, dir_id: str) -> bool:
        """
        Удаление общей директории из списка
        
        Args:
            dir_id: ID директории
            
        Returns:
            bool: True если удаление успешно
        """
        if dir_id in self.directories:
            del self.directories[dir_id]
            self._save_directories()
            return True
        return False
    
    def get_directory(self, dir_id: str) -> Optional[SharedDirectory]:
        """Получение информации о директории по ID"""
        return self.directories.get(dir_id)
    
    def get_directory_by_path(self, path: Path) -> Optional[SharedDirectory]:
        """
        Получение директории по пути
        Возвращает самую специфичную (глубокую) общую папку для данного пути
        """
        resolved_path = path.resolve()
        matching_dirs = []
        
        for directory in self.directories.values():
            if not directory.is_active:
                continue
            
            dir_path = Path(directory.path).resolve()
            if (dir_path == resolved_path or 
                dir_path in resolved_path.parents):
                matching_dirs.append((directory, len(dir_path.parts)))
        
        if not matching_dirs:
            return None
        
        # Возвращаем директорию с самым длинным путем (самую специфичную)
        matching_dirs.sort(key=lambda x: x[1], reverse=True)
        return matching_dirs[0][0]
    
    def list_directories(self, include_inactive: bool = False) -> List[SharedDirectory]:
        """Получение списка всех общих директорий"""
        result = []
        for directory in self.directories.values():
            if include_inactive or directory.is_active:
                result.append(directory)
        
        # Сортируем по дате добавления (сначала новые)
        result.sort(key=lambda x: x.added_at, reverse=True)
        return result
    
    def update_directory(self, dir_id: str, **kwargs) -> Optional[SharedDirectory]:
        """Обновление параметров общей директории"""
        if dir_id not in self.directories:
            return None
        
        directory = self.directories[dir_id]
        
        # Обновляем только разрешенные поля
        allowed_fields = {'name', 'description', 'is_active', 
                         'allow_upload', 'allow_delete', 'allow_rename'}
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(directory, key, value)
        
        self._save_directories()
        return directory
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики по общим папкам"""
        total = len(self.directories)
        active = sum(1 for d in self.directories.values() if d.is_active)
        
        return {
            "total_directories": total,
            "active_directories": active,
            "inactive_directories": total - active,
            "storage_file": str(self.storage_file)
        }