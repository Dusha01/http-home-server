"""
Обратная совместимость: конфиг перенесён в core.
"""
from src.core.config import Settings, config

__all__ = ["Settings", "config"]
