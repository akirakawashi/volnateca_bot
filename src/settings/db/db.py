from settings.base import Settings


class DBSettings(Settings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_POOL_SIZE: int = 6
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3000

    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
