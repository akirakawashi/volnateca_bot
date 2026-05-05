from settings.app.app import AppSettings
from settings.app.docs import DocsSettings
from settings.db.db import DBSettings


class ConfigFactory:
    def __init__(self) -> None:
        self.app = AppSettings()
        self.db = DBSettings()
        self.docs = DocsSettings()
