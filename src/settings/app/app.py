from settings.base import Settings


class AppSettings(Settings):
    DEBUG: bool = False
    APP_NAME: str = "volnateca-bot"
    APP_VERSION: str = "0.1.0"
