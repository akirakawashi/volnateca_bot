from settings.db.db import DBSettings


class ConfigFactory:
    def __init__(self) -> None:
        self.db = DBSettings()
