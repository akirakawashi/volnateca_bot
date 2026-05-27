from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from di.providers import make_providers
from presentation.http.exception_handlers import setup_exception_handlers
from presentation.http.middleware import TrustedHostMiddlewareWithPathBypass
from presentation.http.routers import admin_router, api_v1_router, healthcheck_router
from settings.factory import ConfigFactory

config = ConfigFactory()

TEMP_ALLOWED_HOSTS = ("test.volnateca.showcases.ic8",)
TEMP_CORS_ORIGINS = ("http://test.volnateca-admin.showcases.ic8",)


def include_routers(application: FastAPI) -> None:
    application.include_router(api_v1_router)
    application.include_router(admin_router)
    application.include_router(healthcheck_router)


def create_di_container() -> AsyncContainer:
    return make_async_container(*make_providers())


def merge_items(*groups: list[str] | tuple[str, ...]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()

    for group in groups:
        for item in group:
            if item in seen:
                continue
            seen.add(item)
            merged.append(item)

    return merged


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

    cors_origins = merge_items(config.cors.allowed_origins, TEMP_CORS_ORIGINS)
    if cors_origins:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=config.cors.ALLOW_CREDENTIALS,
            allow_methods=config.cors.allowed_methods,
            allow_headers=config.cors.allowed_headers,
        )
    application.add_middleware(
        TrustedHostMiddlewareWithPathBypass,
        allowed_hosts=merge_items(config.app.allowed_hosts, TEMP_ALLOWED_HOSTS),
        bypass_paths=("/healthcheck",),
    )

    return application


def create_app() -> FastAPI:
    application = create_fastapi_app()
    setup_exception_handlers(application)
    setup_dishka(create_di_container(), application)
    return application


app = create_app()
