"""
Вывод в консоль при старте и остановке сервера.
Отделён от lifespan для читаемости и тестируемости.
"""
import qrcode
from io import StringIO

from src.core.config import config
from src.version import __version__


def print_banner(auth_required: bool) -> None:
    print(f"\n{'='*60}")
    print(f"🚀 Home File Server v{__version__}")
    print(f"{'='*60}")
    print(f"📡 Сервер запущен: http://{config.server_host}:{config.server_port}")
    print(f"💾 Директория хранилища: {config.storage_dir}")
    print(f"📁 Директория загрузок: {config.upload_dir}")
    print(f"🔐 Аутентификация: {'включена' if auth_required else 'отключена'}")
    print(f"{'='*60}\n")


def print_token_display(token_display) -> None:
    """Вывод токена и QR в консоль (token_display — TokenDisplayResponse)."""
    print("\n" + "🔐" * 30)
    print("🔐 АДМИН-ДОСТУП: ТОКЕН СГЕНЕРИРОВАН")
    print("🔐" * 30 + "\n")
    print("📋 ТОКЕН (скопируйте для входа):")
    print("-" * 50)
    print(f"\033[1;32m{token_display.token}\033[0m")
    print("-" * 50)
    print("\n📱 QR-КОД ДЛЯ БЫСТРОГО ВХОДА:")
    print("-" * 50)
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(token_display.auth_url)
        f = StringIO()
        qr.print_ascii(out=f, invert=False)
        f.seek(0)
        print(f.read())
    except Exception:
        print(f"📲 QR: \033[1;36m{token_display.auth_url}\033[0m")
    print("-" * 50)
    print(f"\n🌐 АДРЕС ДЛЯ ВХОДА:")
    print(f"🔗 {token_display.auth_url}")
    print(f"🏠 Локальный: http://{config.server_host}:{config.server_port}/auth/login")
    print("\n📱 ИНСТРУКЦИЯ:")
    for instruction in token_display.instructions:
        print(f"  {instruction}")
    print("\n⚠️  ВНИМАНИЕ: Токен будет показан только один раз!")
    print("   Сохраните его в надежном месте.")
    print("\n" + "🔐" * 30 + "\n")


def print_existing_tokens(active_count: int, total_count: int) -> None:
    print(f"\n✅ Найдено активных токенов: {active_count}")
    print(f"📊 Всего токенов: {total_count}")
    print(f"\n🔗 Страница входа: http://{config.server_host}:{config.server_port}/auth/login")
    print("   Используйте существующий токен или создайте новый через /auth\n")


def print_existing_token_with_qr(token_display) -> None:
    """Вывод уже сохранённого токена и QR (объект с .token, .auth_url)."""
    instructions = [
        "1. Отсканируйте QR-код камерой телефона",
        "2. Или введите токен вручную в веб-интерфейсе",
        "3. Токен уже сохранён на сервере, показывается при каждом запуске",
    ]
    print("\n" + "🔐" * 30)
    print("🔐 ТОКЕН ДОСТУПА (существующий)")
    print("🔐" * 30 + "\n")
    print("📋 ТОКЕН (скопируйте для входа):")
    print("-" * 50)
    print(f"\033[1;32m{token_display.token}\033[0m")
    print("-" * 50)
    print("\n📱 QR-КОД ДЛЯ БЫСТРОГО ВХОДА:")
    print("-" * 50)
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(token_display.auth_url)
        f = StringIO()
        qr.print_ascii(out=f, invert=False)
        f.seek(0)
        print(f.read())
    except Exception:
        print(f"📲 QR: \033[1;36m{token_display.auth_url}\033[0m")
    print("-" * 50)
    print(f"\n🌐 АДРЕС ДЛЯ ВХОДА:")
    print(f"🔗 {token_display.auth_url}")
    print(f"🏠 Локальный: http://{config.server_host}:{config.server_port}/auth/login")
    print("\n📱 ИНСТРУКЦИЯ:")
    for line in instructions:
        print(f"  {line}")
    print("\n" + "🔐" * 30 + "\n")


def print_shutdown() -> None:
    print("\n" + "=" * 60)
    print("🛑 Сервер остановлен")
    print("=" * 60 + "\n")
