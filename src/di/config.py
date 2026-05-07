from dishka import Provider, Scope, provide

from settings.app.app import AppSettings
from settings.app.cors import CorsSettings
from settings.app.docs import DocsSettings
from settings.app.logger import LoggingSettings
from settings.db.db import DBSettings
from settings.factory import ConfigFactory
from settings.vk import VKSettings


class ConfigProvider(Provider):
    @provide(scope=Scope.APP, provides=ConfigFactory)
    def get_config(self) -> ConfigFactory:
        return ConfigFactory()

    @provide(scope=Scope.APP)
    def get_app_config(self, cfg_factory: ConfigFactory) -> AppSettings:
        return cfg_factory.app

    @provide(scope=Scope.APP)
    def get_db_config(self, cfg_factory: ConfigFactory) -> DBSettings:
        return cfg_factory.db

    @provide(scope=Scope.APP)
    def get_docs_config(self, cfg_factory: ConfigFactory) -> DocsSettings:
        return cfg_factory.docs

    @provide(scope=Scope.APP)
    def get_cors_config(self, cfg_factory: ConfigFactory) -> CorsSettings:
        return cfg_factory.cors

    @provide(scope=Scope.APP)
    def get_logging_config(self, cfg_factory: ConfigFactory) -> LoggingSettings:
        return cfg_factory.logging

    @provide(scope=Scope.APP)
    def get_vk_config(self, cfg_factory: ConfigFactory) -> VKSettings:
        return cfg_factory.vk
