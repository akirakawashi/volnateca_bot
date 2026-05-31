import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from presentation.http.admin_session import (
    create_admin_session_cookie_value,
    verify_admin_session_cookie_value,
)
from settings.app.app import AppSettings

security = HTTPBasic(auto_error=False)
settings = AppSettings()

auth_admin_router = APIRouter()
ADMIN_SESSION_COOKIE_NAME = "volnateca_admin_session"
ADMIN_SESSION_COOKIE_PATH = "/v1/admin"


def verify_admin_login_password(
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> None:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный логин или пароль администратора",
        headers={"WWW-Authenticate": "Basic"},
    )

    if credentials is None:
        raise unauthorized

    login_ok = secrets.compare_digest(credentials.username, settings.ADMIN_LOGIN)
    password_ok = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)

    if not (login_ok and password_ok):
        raise unauthorized


def verify_admin_token(
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> None:
    forbidden = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Некорректный X-Admin-Token",
    )

    if admin_token is None:
        raise forbidden

    token_ok = secrets.compare_digest(admin_token, settings.ADMIN_TOKEN)
    if not token_ok:
        raise forbidden


def verify_admin_session(
    admin_session: str | None = Cookie(default=None, alias=ADMIN_SESSION_COOKIE_NAME),
) -> None:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Сессия администратора истекла или недействительна",
    )

    if admin_session is None:
        raise unauthorized

    session_ok = verify_admin_session_cookie_value(
        cookie_value=admin_session,
        secret=settings.ADMIN_SESSION_SECRET,
    )
    if not session_ok:
        raise unauthorized


@auth_admin_router.post(
    path="/auth/login",
    name="Войти в админ-панель",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(verify_admin_login_password), Depends(verify_admin_token)],
)
async def login_admin() -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.set_cookie(
        key=ADMIN_SESSION_COOKIE_NAME,
        value=create_admin_session_cookie_value(
            secret=settings.ADMIN_SESSION_SECRET,
            ttl_seconds=settings.ADMIN_SESSION_TTL_SECONDS,
        ),
        max_age=settings.ADMIN_SESSION_TTL_SECONDS,
        httponly=True,
        secure=settings.ADMIN_SESSION_COOKIE_SECURE,
        samesite=settings.ADMIN_SESSION_COOKIE_SAMESITE,
        path=ADMIN_SESSION_COOKIE_PATH,
    )
    return response


@auth_admin_router.get(
    path="/auth/check",
    name="Проверить доступ к админ-панели",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(verify_admin_session)],
)
async def check_admin_auth() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@auth_admin_router.post(
    path="/auth/logout",
    name="Выйти из админ-панели",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def logout_admin() -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(
        key=ADMIN_SESSION_COOKIE_NAME,
        path=ADMIN_SESSION_COOKIE_PATH,
        secure=settings.ADMIN_SESSION_COOKIE_SECURE,
        httponly=True,
        samesite=settings.ADMIN_SESSION_COOKIE_SAMESITE,
    )
    return response
