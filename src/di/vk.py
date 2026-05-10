from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide

from application.interface.clients import IVKMessageClient, IVKUserClient
from infrastructure.vk import VKAPIClient
from settings.vk import VKSettings


class VKProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_vk_api_client(
        self,
        settings: VKSettings,
    ) -> AsyncIterable[VKAPIClient]:
        async with VKAPIClient(settings=settings) as client:
            yield client

    @provide(scope=Scope.APP, provides=IVKUserClient)
    def get_vk_user_client(self, client: VKAPIClient) -> IVKUserClient:
        return client

    @provide(scope=Scope.APP, provides=IVKMessageClient)
    def get_vk_message_client(self, client: VKAPIClient) -> IVKMessageClient:
        return client
