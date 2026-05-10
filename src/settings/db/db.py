from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class DBSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        extra="ignore",
    )

    HOST: str
    PORT: int
    NAME: str
    USERNAME: str
    PASSWORD: str
    POOL_SIZE: int = 6
    MAX_OVERFLOW: int = 20
    POOL_RECYCLE_SECONDS: int = 3000

    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@"
            f"{self.HOST}:{self.PORT}/{self.NAME}"
        )
