from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class CorsSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="CORS_")

    ALLOW_ORIGINS: list[str] = ["*"]
    ALLOW_METHODS: list[str] = ["*"]
    ALLOW_HEADERS: list[str] = ["*"]
    ALLOW_CREDENTIALS: bool = False
