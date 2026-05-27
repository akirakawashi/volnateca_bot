from collections.abc import Sequence

from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send


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
        await super().__call__(scope, receive, send)
