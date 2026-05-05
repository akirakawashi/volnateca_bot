from collections.abc import Iterable

from dishka import Provider

from di.config import ConfigProvider
from di.session import DBProvider
from di.uow import UoWProvider


def make_providers() -> Iterable[Provider]:
    return (
        ConfigProvider(),
        DBProvider(),
        UoWProvider(),
    )
