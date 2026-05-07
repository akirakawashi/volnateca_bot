from settings.app.app import AppSettings
from settings.app.cors import CorsSettings
from settings.app.docs import DocsSettings
from settings.app.logger import LoggingSettings
from settings.db.db import DBSettings
from settings.vk import VKSettings


class ConfigFactory:
    def __init__(self) -> None:
        self.app = AppSettings()
        self.db = DBSettings()
        self.docs = DocsSettings()
        self.cors = CorsSettings()
        self.logging = LoggingSettings()
        self.vk = VKSettings()
