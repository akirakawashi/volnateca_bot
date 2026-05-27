from collections.abc import Sequence

from loguru import logger
from starlette.datastructures import Headers
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send


class CORSMiddlewareWithLogging(CORSMiddleware):
    def preflight_response(self, request_headers: Headers):
        response = super().preflight_response(request_headers)

        if response.status_code == 400:
            logger.warning(
                "CORS preflight rejected: origin={origin} method={method} headers={headers}",
                origin=request_headers.get("origin"),
                method=request_headers.get("access-control-request-method"),
                headers=request_headers.get("access-control-request-headers"),
            )

        return response


class TrustedHostMiddlewareWithPathBypass(TrustedHostMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        allowed_hosts: Sequence[str] | None = None,
        bypass_paths: Sequence[str] | None = None,
        www_redirect: bool = True,
    ) -> None:
        super().__init__(app=app, allowed_hosts=allowed_hosts, www_redirect=www_redirect)
        self.bypass_paths = frozenset(bypass_paths or ())

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("path") in self.bypass_paths:
            await self.app(scope, receive, send)
            return

        if scope["type"] == "http" and not self.allow_any:
            headers = Headers(scope=scope)
            host, is_valid_host, found_www_redirect = self._inspect_host(headers=headers)
            if not is_valid_host and not (found_www_redirect and self.www_redirect):
                logger.warning(
                    "Trusted host rejected request: method={method} path={path} host={host} origin={origin} "
                    "acr_method={acr_method} acr_headers={acr_headers} allowed_hosts={allowed_hosts}",
                    method=scope.get("method"),
                    path=scope.get("path"),
                    host=host,
                    origin=headers.get("origin"),
                    acr_method=headers.get("access-control-request-method"),
                    acr_headers=headers.get("access-control-request-headers"),
                    allowed_hosts=self.allowed_hosts,
                )

        await super().__call__(scope, receive, send)

    def _inspect_host(self, headers: Headers) -> tuple[str, bool, bool]:
        host = headers.get("host", "").split(":")[0]
        is_valid_host = False
        found_www_redirect = False

        for pattern in self.allowed_hosts:
            if host == pattern or (pattern.startswith("*") and host.endswith(pattern[1:])):
                is_valid_host = True
                break
            if "www." + host == pattern:
                found_www_redirect = True

        return host, is_valid_host, found_www_redirect
