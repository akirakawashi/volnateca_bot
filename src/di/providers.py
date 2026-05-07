from collections.abc import Iterable

from dishka import Provider

from di.config import ConfigProvider
from di.ioc import InteractorProvider
from di.repository import RepositoriesProvider
from di.session import DBProvider
from di.uow import UoWProvider
from di.vk import VKProvider


def make_providers() -> Iterable[Provider]:
    return (
        ConfigProvider(),
        DBProvider(),
        VKProvider(),
        RepositoriesProvider(),
        InteractorProvider(),
        UoWProvider(),
    )
