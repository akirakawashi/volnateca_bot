from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from di.providers import make_providers
from presentation.http.exception_handlers import setup_exception_handlers
from presentation.http.middleware import CORSMiddlewareWithLogging, TrustedHostMiddlewareWithPathBypass
from presentation.http.routers import admin_router, api_v1_router, healthcheck_router
from settings.factory import ConfigFactory

config = ConfigFactory()


def include_routers(application: FastAPI) -> None:
    application.include_router(api_v1_router)
    application.include_router(admin_router)
    application.include_router(healthcheck_router)


def create_di_container() -> AsyncContainer:
    return make_async_container(*make_providers())


def create_fastapi_app() -> FastAPI:
    application = FastAPI(
        debug=config.app.DEBUG,
        title=config.app.NAME,
        version=config.app.VERSION,
        openapi_url=config.docs.OPENAPI_URL,
        docs_url=None,
        redoc_url=None,
    )
    include_routers(application)

    application.add_middleware(
        CORSMiddlewareWithLogging,
        allow_origins=["*"],
        allow_credentials=config.cors.ALLOW_CREDENTIALS,
        allow_methods=config.cors.allowed_methods,
        allow_headers=config.cors.allowed_headers,
    )
    application.add_middleware(
        TrustedHostMiddlewareWithPathBypass,
        allowed_hosts=config.app.allowed_hosts,
        bypass_paths=("/healthcheck",),
    )

    return application


def create_app() -> FastAPI:
    application = create_fastapi_app()
    setup_exception_handlers(application)
    setup_dishka(create_di_container(), application)
    return application


app = create_app()
