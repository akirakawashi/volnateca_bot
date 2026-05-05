from settings.base import Settings


class DocsSettings(Settings):
    OPENAPI_URL: str | None = "/openapi.json"
