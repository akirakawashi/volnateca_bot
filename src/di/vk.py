from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide

from application.interface.clients import IVKUserClient
from infrastructure.vk import VKAPIClient
from settings.vk import VKSettings


class VKProvider(Provider):
    @provide(scope=Scope.APP, provides=IVKUserClient)
    async def get_vk_user_client(
        self,
        settings: VKSettings,
    ) -> AsyncIterable[VKAPIClient]:
        async with VKAPIClient(settings=settings) as client:
            yield client
