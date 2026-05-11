from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class AppSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    DEBUG: bool = False
    NAME: str = "volnateca-bot"
    VERSION: str = "0.1.0"
    TRUSTED_HOSTS: list[str] = ["*"]
