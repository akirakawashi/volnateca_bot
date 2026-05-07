from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class VKSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="VK_",
        extra="ignore",
    )

    CONFIRMATION_CODE: str
