import os
import stat
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Set
import humanize

from src.modules.share.models.file_models import FileInfo, FileType


class FileUtils:
    """Утилиты для работы с файлами"""
    
    PREVIEW_EXTENSIONS: Set[str] = {
        '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yml',
        '.ini', '.cfg', '.conf', '.log', '.csv', '.tsv', '.sql', '.sh', '.bat',
        '.ps1', '.rst', '.tex', '.latex', '.c', '.cpp', '.h', '.java', '.php',
        '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.toml', '.yaml',
        '.env', '.example', '.config', '.gitignore', '.dockerignore',
    }

    # Имена файлов без расширения или с точкой в начале (превью как текст)
    TEXT_PREVIEW_NAMES: Set[str] = {
        '.env', '.env.example', '.env.local', '.env.sample',
        '.config', '.gitignore', '.dockerignore', '.editorconfig',
    }
    
    IMAGE_EXTENSIONS: Set[str] = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'
    }
    
    @staticmethod
    def get_file_info(file_path: Path, base_path: Path) -> Optional[FileInfo]:
        """
        Получение информации о файле
        Относительный путь вычисляется относительно base_path
        """
        try:
            stat_info = file_path.stat()
            
            # Определяем тип файла
            if file_path.is_dir():
                file_type = FileType.DIRECTORY
            elif file_path.is_symlink():
                file_type = FileType.SYMLINK
            elif file_path.is_file():
                file_type = FileType.FILE
            else:
                file_type = FileType.OTHER
            
            # Вычисляем относительный путь
            try:
                relative_path = str(file_path.relative_to(base_path))
            except ValueError:
                relative_path = str(file_path)
            
            # Получаем расширение
            extension = file_path.suffix.lower() if file_path.suffix else None
            
            return FileInfo(
                name=file_path.name,
                path=relative_path,
                type=file_type,
                size=stat_info.st_size if file_type != FileType.DIRECTORY else None,
                modified=datetime.fromtimestamp(stat_info.st_mtime),
                created=datetime.fromtimestamp(stat_info.st_ctime),
                extension=extension,
                is_hidden=file_path.name.startswith('.'),
                is_readable=os.access(file_path, os.R_OK),
                is_writable=os.access(file_path, os.W_OK)
            )
        except (OSError, IOError, PermissionError):
            return None
    

    @staticmethod
    def get_directory_content(path: Path, base_path: Path, show_hidden: bool = False) -> tuple:
        """
        Получение содержимого директории
        Возвращает (список директорий, список файлов)
        """
        directories = []
        files = []
        
        try:
            for item in sorted(path.iterdir(), key=lambda p: p.name.lower()):
                # Пропускаем скрытые файлы если не нужно их показывать
                if not show_hidden and item.name.startswith('.'):
                    continue
                
                file_info = FileUtils.get_file_info(item, base_path)
                if file_info:
                    if file_info.type == FileType.DIRECTORY:
                        directories.append(file_info)
                    else:
                        files.append(file_info)
        except (PermissionError, OSError):
            pass
        
        # Сортируем: директории сверху, потом файлы, все по алфавиту
        directories.sort(key=lambda x: x.name.lower())
        files.sort(key=lambda x: x.name.lower())
        
        return directories, files
    

    @staticmethod
    def is_path_safe(requested_path: Path, base_path: Path) -> bool:
        """
        Проверка, что запрошенный путь находится внутри разрешенной директории
        Защита от path traversal атак
        """
        try:
            # Разрешаем символические ссылки
            requested_path = requested_path.resolve()
            base_path = base_path.resolve()
            
            # Проверяем, что запрошенный путь является потомком base_path
            return base_path in requested_path.parents or base_path == requested_path
        except (OSError, RuntimeError):
            return False
    

    @staticmethod
    def get_mime_type(file_path: Path) -> str:
        """Получение MIME-типа файла"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'application/octet-stream'
    

    @staticmethod
    def format_size(size: int) -> str:
        """Форматирование размера файла в человекочитаемый вид"""
        return humanize.naturalsize(size, binary=True)
    

    @staticmethod
    def can_preview(file_path: Path) -> bool:
        """Можно ли показать предпросмотр файла"""
        extension = file_path.suffix.lower()
        return (extension in FileUtils.PREVIEW_EXTENSIONS or
                extension in FileUtils.IMAGE_EXTENSIONS)

    @staticmethod
    def is_text_previewable(file_path: Path) -> bool:
        """Подходит ли файл для текстового превью (в т.ч. .env, .config)."""
        name = file_path.name.lower()
        ext = file_path.suffix.lower()
        if ext in FileUtils.PREVIEW_EXTENSIONS:
            return True
        if name in FileUtils.TEXT_PREVIEW_NAMES:
            return True
        if name.startswith('.env') or name.endswith('.example'):
            return True
        return False
    

    @staticmethod
    def is_image(file_path: Path) -> bool:
        """Является ли файл изображением"""
        return file_path.suffix.lower() in FileUtils.IMAGE_EXTENSIONS
    

    @staticmethod
    def safe_filename(filename: str) -> str:
        """Очистка имени файла от небезопасных символов"""
        import re
        # Удаляем все не-ASCII и специальные символы, оставляем буквы, цифры, точки, дефисы, подчеркивания и пробелы
        filename = re.sub(r'[^\w\s\.\-]', '', filename)
        # Удаляем лишние пробелы
        filename = re.sub(r'\s+', ' ', filename)
        # Удаляем точки в начале и конце
        filename = filename.strip('. ')
        return filename or 'unnamed'
    
    
    @staticmethod
    def get_unique_filename(directory: Path, filename: str) -> Path:
        """
        Получение уникального имени файла в директории
        Если файл существует, добавляет (1), (2) и т.д.
        """
        filepath = directory / filename
        
        if not filepath.exists():
            return filepath
        
        name = filepath.stem
        extension = filepath.suffix
        counter = 1
        
        while True:
            new_filename = f"{name} ({counter}){extension}"
            new_path = directory / new_filename
            if not new_path.exists():
                return new_path
            counter += 1