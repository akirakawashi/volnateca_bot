from pydantic_settings import SettingsConfigDict

from settings.base import Settings


class DBSettings(Settings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    HOST: str
    PORT: int
    NAME: str
    USERNAME: str
    PASSWORD: str
    POOL_SIZE: int = 6
    MAX_OVERFLOW: int = 20
    POOL_RECYCLE_SECONDS: int = 3000

    def dsn(self) -> str:
        return f"postgresql+asyncpg://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"
