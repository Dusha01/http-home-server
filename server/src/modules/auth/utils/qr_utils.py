"""
Утилиты для генерации QR-кодов
"""
import qrcode
import base64
from io import BytesIO
from typing import Optional
from pathlib import Path


class QRUtils:
    """Генератор QR-кодов для токенов"""
    
    @staticmethod
    def generate_qr_code(
        data: str, 
        size: int = 10,
        border: int = 4,
        as_base64: bool = True
    ) -> str:
        """
        Генерация QR-кода
        
        Args:
            data: Данные для кодирования
            size: Размер QR-кода
            border: Ширина границы
            as_base64: Вернуть как base64 строку (иначе как bytes)
            
        Returns:
            str: QR-код в формате base64 или bytes
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем в BytesIO
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        
        if as_base64:
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        else:
            return buffered.getvalue()
    

    @staticmethod
    def generate_auth_url(token: str, server_url: Optional[str] = None) -> str:
        """
        Генерация URL для аутентификации
        
        Args:
            token: Токен доступа
            server_url: URL сервера (например, http://192.168.1.100:8080)
            
        Returns:
            str: URL для аутентификации
        """
        if not server_url:
            return f"/auth/login?token={token}"
        
        server_url = server_url.rstrip('/')
        return f"{server_url}/auth/login?token={token}"