from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from di.providers import make_providers
from presentation.http.routers.healthcheck import healthcheck_router
from settings.factory import ConfigFactory

config = ConfigFactory()


def include_routers(application: FastAPI) -> None:
    application.include_router(healthcheck_router)


def create_di_container() -> AsyncContainer:
    return make_async_container(*make_providers())


def create_fastapi_app() -> FastAPI:
    application = FastAPI(
        debug=config.app.DEBUG,
        title=config.app.APP_NAME,
        version=config.app.APP_VERSION,
        openapi_url=config.docs.OPENAPI_URL,
    )
    include_routers(application)
    return application


def create_app() -> FastAPI:
    application = create_fastapi_app()
    setup_dishka(create_di_container(), application)
    return application


app = create_app()
