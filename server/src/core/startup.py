"""
Вывод в консоль при старте и остановке сервера.
Отделён от lifespan для читаемости и тестируемости.
"""
import qrcode
from io import StringIO

from src.core.config import config
from src.i18n import t
from src.version import __version__


def print_banner(auth_required: bool) -> None:
    print(f"\n{'='*60}")
    print(f"🚀 Home File Server v{__version__}")
    print(f"{'='*60}")
    print(f"📡 {t('banner.server_started', host=config.server_host, port=config.server_port)}")
    print(f"💾 {t('banner.storage_dir', path=config.storage_dir)}")
    print(f"📁 {t('banner.upload_dir', path=config.upload_dir)}")
    auth_msg = t("banner.auth_on") if auth_required else t("banner.auth_off")
    print(f"🔐 {auth_msg}")
    print(f"{'='*60}\n")


def print_token_display(token_display) -> None:
    """Вывод токена и QR в консоль (token_display — TokenDisplayResponse)."""
    from src.i18n import get_locale
    locale = get_locale()
    instructions = locale.get_instructions_token_display()
    print("\n" + "🔐" * 30)
    print(f"🔐 {t('token_display.header')}")
    print("🔐" * 30 + "\n")
    print(f"📋 {t('token_display.token_label')}")
    print("-" * 50)
    print(f"\033[1;32m{token_display.token}\033[0m")
    print("-" * 50)
    print(f"\n📱 {t('token_display.qr_label')}")
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
    login_url = f"{config.effective_frontend_url}/auth/login"
    print(f"\n🌐 {t('token_display.address_label')}")
    print(f"🔗 {token_display.auth_url}")
    print(f"🏠 {t('token_display.local', url=login_url)}")
    print(f"\n📱 {t('token_display.instruction_title')}")
    for instruction in instructions:
        print(f"  {instruction}")
    print(f"\n⚠️  {t('token_display.warning_once')}")
    print(f"   {t('token_display.warning_save')}")
    print("\n" + "🔐" * 30 + "\n")


def print_existing_tokens(active_count: int, total_count: int) -> None:
    login_url = f"{config.effective_frontend_url}/auth/login"
    print(f"\n✅ {t('existing_tokens.found_active', count=active_count)}")
    print(f"📊 {t('existing_tokens.total', total=total_count)}")
    print(f"\n🔗 {t('existing_tokens.login_page', url=login_url)}")
    print(f"   {t('existing_tokens.use_existing')}\n")


def print_existing_token_with_qr(token_display) -> None:
    """Вывод уже сохранённого токена и QR (объект с .token, .auth_url)."""
    from src.i18n import get_locale
    instructions = get_locale().get_instructions_existing_qr()
    print("\n" + "🔐" * 30)
    print(f"🔐 {t('existing_qr.header')}")
    print("🔐" * 30 + "\n")
    print(f"📋 {t('token_display.token_label')}")
    print("-" * 50)
    print(f"\033[1;32m{token_display.token}\033[0m")
    print("-" * 50)
    print(f"\n📱 {t('token_display.qr_label')}")
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
    login_url = f"{config.effective_frontend_url}/auth/login"
    print(f"\n🌐 {t('token_display.address_label')}")
    print(f"🔗 {token_display.auth_url}")
    print(f"🏠 {t('token_display.local', url=login_url)}")
    print(f"\n📱 {t('token_display.instruction_title')}")
    for line in instructions:
        print(f"  {line}")
    print("\n" + "🔐" * 30 + "\n")


def print_no_auth_info() -> None:
    """Вывод подсказок при запуске без аутентификации."""
    frontend_url = config.effective_frontend_url
    api_url = f"http://{config.server_host}:{config.server_port}"
    print(f"\n⚠️  {t('no_auth.title')}")
    print(f"   {t('no_auth.description')}\n")
    print(f"🌐 {t('no_auth.frontend', url=frontend_url)}")
    print(f"📡 {t('no_auth.api', url=api_url)}")
    print(f"\n💡 {t('no_auth.enable_next')}\n")


def print_shutdown() -> None:
    print("\n" + "=" * 60)
    print(f"🛑 {t('shutdown.stopped')}")
    print("=" * 60 + "\n")
