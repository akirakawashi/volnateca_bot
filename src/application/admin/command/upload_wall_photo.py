from dataclasses import dataclass

from application.base_interactor import Interactor


@dataclass(slots=True, frozen=True, kw_only=True)
class UploadWallPhotoCommand:
    url: str


@dataclass(slots=True, frozen=True, kw_only=True)
class UploadedWallPhotoDTO:
    attachment: str


class UploadWallPhotoHandler(Interactor[UploadWallPhotoCommand, UploadedWallPhotoDTO]):
    """Возвращает URL вложения для публикации на стене.

    URL передаётся напрямую в attachments записи wall.post — VK обрабатывает
    внешние ссылки как link-вложения с превью.
    """

    async def __call__(self, command_data: UploadWallPhotoCommand) -> UploadedWallPhotoDTO:
        return UploadedWallPhotoDTO(attachment=command_data.url)
