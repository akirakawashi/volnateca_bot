from dishka import Provider, Scope, provide

from settings.db.db import DBSettings
from settings.factory import ConfigFactory


class ConfigProvider(Provider):
    @provide(scope=Scope.APP, provides=ConfigFactory)
    def get_config(self) -> ConfigFactory:
        return ConfigFactory()

    @provide(scope=Scope.APP)
    def get_db_config(self, cfg_factory: ConfigFactory) -> DBSettings:
        return cfg_factory.db
