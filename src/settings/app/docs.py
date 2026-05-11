from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class DocsSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="APP_")

    OPENAPI_URL: str | None = "/openapi.json"
