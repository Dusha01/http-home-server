"""
Язык задаётся через LANGUAGE или LANG (ru/en), по умолчанию ru.
"""
from typing import Dict, Any

SUPPORTED_LANGUAGES = ("ru", "en")
DEFAULT_LANGUAGE = "ru"


def _translations() -> Dict[str, Dict[str, str]]:
    return {
        "ru": {
            # Баннер при старте
            "banner.server_started": "Сервер запущен: http://{host}:{port}",
            "banner.storage_dir": "Директория хранилища: {path}",
            "banner.upload_dir": "Директория загрузок: {path}",
            "banner.auth_on": "Аутентификация: включена",
            "banner.auth_off": "Аутентификация: отключена",
            # Вывод токена (первый запуск)
            "token_display.header": "АДМИН-ДОСТУП: ТОКЕН СГЕНЕРИРОВАН",
            "token_display.token_label": "ТОКЕН (скопируйте для входа):",
            "token_display.qr_label": "QR-КОД ДЛЯ БЫСТРОГО ВХОДА:",
            "token_display.address_label": "АДРЕС ДЛЯ ВХОДА:",
            "token_display.local": "Локальный: {url}",
            "token_display.instruction_title": "ИНСТРУКЦИЯ:",
            "token_display.instruction_1": "1. Отсканируйте QR-код камерой телефона",
            "token_display.instruction_2": "2. Или введите токен вручную в веб-интерфейсе",
            "token_display.instruction_3": "3. Нажмите 'Войти' в веб-интерфейсе",
            "token_display.warning_once": "ВНИМАНИЕ: Токен будет показан только один раз!",
            "token_display.warning_save": "Сохраните его в надежном месте.",
            # Существующие токены (краткий вывод)
            "existing_tokens.found_active": "Найдено активных токенов: {count}",
            "existing_tokens.total": "Всего токенов: {total}",
            "existing_tokens.login_page": "Страница входа: {url}",
            "existing_tokens.use_existing": "Используйте существующий токен или создайте новый через /auth",
            # Вывод существующего токена с QR
            "existing_qr.header": "ТОКЕН ДОСТУПА (существующий)",
            "existing_qr.instruction_1": "1. Отсканируйте QR-код камерой телефона",
            "existing_qr.instruction_2": "2. Или введите токен вручную в веб-интерфейсе",
            "existing_qr.instruction_3": "3. Токен уже сохранён на сервере, показывается при каждом запуске",
            # Остановка
            "shutdown.stopped": "Сервер остановлен",
            # Вопрос при запуске
            "prompt.setup": "Настройка аутентификации при запуске сервера",
            "prompt.question": "Генерировать токен аутентификации? (y/n): ",
            "prompt.invalid": "Введите y (да) или n (нет).",
            # Сообщения lifespan
            "lifespan.no_auth": "Режим без аутентификации: токен не запрашивается.",
            "no_auth.title": "Режим без аутентификации",
            "no_auth.description": "Токен не запрашивается — доступ к файлам открыт для всех.",
            "no_auth.frontend": "Веб-интерфейс: {url}",
            "no_auth.api": "API сервера: {url}",
            "no_auth.enable_next": "Чтобы включить аутентификацию, перезапустите сервер и ответьте «y» на вопрос о токене.",
            "lifespan.error_tokens": "Ошибка при загрузке токенов: {e}",
            "lifespan.tokens_in_storage": "В хранилище: {count} токен(ов)",
            "lifespan.warning": "Предупреждение: {e}",
            "lifespan.auth_unavailable": "Сервис аутентификации временно недоступен",
            # Описание начального токена (для API/логов)
            "auth.initial_token_description": "Начальный токен сервера",
        },
        "en": {
            "banner.server_started": "Server running: http://{host}:{port}",
            "banner.storage_dir": "Storage directory: {path}",
            "banner.upload_dir": "Upload directory: {path}",
            "banner.auth_on": "Authentication: enabled",
            "banner.auth_off": "Authentication: disabled",
            "token_display.header": "ADMIN ACCESS: TOKEN GENERATED",
            "token_display.token_label": "TOKEN (copy to sign in):",
            "token_display.qr_label": "QR CODE FOR QUICK SIGN-IN:",
            "token_display.address_label": "SIGN-IN URL:",
            "token_display.local": "Local: {url}",
            "token_display.instruction_title": "INSTRUCTIONS:",
            "token_display.instruction_1": "1. Scan the QR code with your phone camera",
            "token_display.instruction_2": "2. Or enter the token manually in the web interface",
            "token_display.instruction_3": "3. Click 'Sign in' in the web interface",
            "token_display.warning_once": "NOTE: The token will be shown only once!",
            "token_display.warning_save": "Save it in a secure place.",
            "existing_tokens.found_active": "Active tokens found: {count}",
            "existing_tokens.total": "Total tokens: {total}",
            "existing_tokens.login_page": "Login page: {url}",
            "existing_tokens.use_existing": "Use an existing token or create one via /auth",
            "existing_qr.header": "ACCESS TOKEN (existing)",
            "existing_qr.instruction_1": "1. Scan the QR code with your phone camera",
            "existing_qr.instruction_2": "2. Or enter the token manually in the web interface",
            "existing_qr.instruction_3": "3. Token is already stored on the server and shown on each startup",
            "shutdown.stopped": "Server stopped",
            "prompt.setup": "Authentication setup when starting the server",
            "prompt.question": "Generate authentication token? (y/n): ",
            "prompt.invalid": "Enter y (yes) or n (no).",
            "lifespan.no_auth": "No authentication mode: token is not requested.",
            "no_auth.title": "No authentication mode",
            "no_auth.description": "Token is not required — file access is open to everyone.",
            "no_auth.frontend": "Web interface: {url}",
            "no_auth.api": "Server API: {url}",
            "no_auth.enable_next": "To enable authentication, restart the server and answer «y» when asked about the token.",
            "lifespan.error_tokens": "Error loading tokens: {e}",
            "lifespan.tokens_in_storage": "In storage: {count} token(s)",
            "lifespan.warning": "Warning: {e}",
            "lifespan.auth_unavailable": "Authentication service temporarily unavailable",
            "auth.initial_token_description": "Initial server token",
        },
    }


class LocaleManager:
    """Менеджер локализации: текущий язык и перевод по ключу."""

    def __init__(self, language: str = DEFAULT_LANGUAGE):
        lang = (language or "").strip().lower()
        if lang not in SUPPORTED_LANGUAGES:
            lang = DEFAULT_LANGUAGE
        self.language = lang
        self._translations = _translations()
        self.translations = self._translations.get(self.language, self._translations[DEFAULT_LANGUAGE])

    def t(self, key: str, **kwargs: Any) -> str:
        """
        Возвращает строку перевода по ключу. Подстановки: t("key", name="World") -> "Hello, World!"
        Если ключ отсутствует, возвращается сам ключ.
        """
        s = self.translations.get(key, key)
        if kwargs:
            try:
                return s.format(**kwargs)
            except KeyError:
                return s
        return s

    def get_instructions_token_display(self) -> list:
        """Список строк инструкции для вывода нового токена (по текущему языку)."""
        return [
            self.t("token_display.instruction_1"),
            self.t("token_display.instruction_2"),
            self.t("token_display.instruction_3"),
        ]

    def get_instructions_existing_qr(self) -> list:
        """Список строк инструкции для вывода существующего токена с QR."""
        return [
            self.t("existing_qr.instruction_1"),
            self.t("existing_qr.instruction_2"),
            self.t("existing_qr.instruction_3"),
        ]


# Глобальный экземпляр; язык задаётся при старте из конфига (см. app.py / config).
_locale: LocaleManager | None = None


def get_locale() -> LocaleManager:
    """Возвращает текущий LocaleManager (инициализируется при первом обращении, если не задан)."""
    global _locale
    if _locale is None:
        _locale = LocaleManager(DEFAULT_LANGUAGE)
    return _locale


def set_locale(language: str) -> LocaleManager:
    """Устанавливает язык и возвращает обновлённый LocaleManager."""
    global _locale
    _locale = LocaleManager(language)
    return _locale


def t(key: str, **kwargs: Any) -> str:
    """Удобная обёртка: перевод по ключу для текущей локали."""
    return get_locale().t(key, **kwargs)
