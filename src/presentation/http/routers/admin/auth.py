import secrets

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from settings.app.app import AppSettings

security = HTTPBasic(auto_error=False)
settings = AppSettings()

auth_admin_router = APIRouter()


def verify_admin_credentials(
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


@auth_admin_router.get(
    path="/auth/check",
    name="Проверить доступ к админ-панели",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def check_admin_auth() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
