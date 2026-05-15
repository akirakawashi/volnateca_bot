from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl

from application.admin.command.post_to_wall import PostToWallHandler
from application.admin.command.upload_wall_photo import UploadWallPhotoCommand, UploadWallPhotoHandler
from presentation.http.dto.admin.wall_post import PostToWallRequestSchema, PostedToWallResponseSchema

wall_admin_router = APIRouter(route_class=DishkaRoute)


class UploadWallPhotoRequestSchema(BaseModel):
    url: HttpUrl


@wall_admin_router.post(
    path="/wall",
    name="Опубликовать пост на стене сообщества",
    response_model=PostedToWallResponseSchema,
    status_code=201,
)
async def post_to_wall(
    data: PostToWallRequestSchema,
    handler: FromDishka[PostToWallHandler],
) -> PostedToWallResponseSchema:
    try:
        result = await handler(data.to_command())
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
    return PostedToWallResponseSchema.from_dto(result)


@wall_admin_router.post(
    path="/wall/photo",
    name="Вернуть URL-вложение для публикации на стене",
    status_code=201,
)
async def upload_wall_photo(
    data: UploadWallPhotoRequestSchema,
    handler: FromDishka[UploadWallPhotoHandler],
) -> dict[str, str]:
    result = await handler(UploadWallPhotoCommand(url=str(data.url)))
    return {"attachment": result.attachment}
