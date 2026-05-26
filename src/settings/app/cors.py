from pydantic_settings import SettingsConfigDict

from settings.base import Settings

DEFAULT_CORS_METHODS = ("GET", "POST", "PUT", "DELETE", "OPTIONS")
DEFAULT_CORS_HEADERS = ("Authorization", "Content-Type")


class CorsSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="CORS_")

    ALLOW_CREDENTIALS: bool = False
    ORIGINS: str = ""

    @property
    def enabled(self) -> bool:
        return bool(self.allowed_origins)

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.ORIGINS.split(",") if item.strip()]

    @property
    def allowed_methods(self) -> list[str]:
        return list(DEFAULT_CORS_METHODS)

    @property
    def allowed_headers(self) -> list[str]:
        return list(DEFAULT_CORS_HEADERS)
