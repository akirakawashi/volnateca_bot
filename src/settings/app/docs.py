from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class DocsSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
    )

    OPENAPI_URL: str | None = "/openapi.json"
