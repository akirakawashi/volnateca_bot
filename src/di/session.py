from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings.db.db import DBSettings


class DBProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: DBSettings) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            config.dsn(),
            future=True,
            echo=False,
            pool_size=config.POOL_SIZE,
            pool_pre_ping=True,
            max_overflow=config.MAX_OVERFLOW,
            pool_recycle=config.POOL_RECYCLE,
        )
        yield engine
        await engine.dispose(close=True)

    @provide(scope=Scope.APP)
    def get_async_pool(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def get_session(
        self,
        pool: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with pool() as session:
            yield session
