from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.post_to_wall import PostToWallHandler
from presentation.http.dto.admin.wall_post import PostToWallRequestSchema, PostedToWallResponseSchema

wall_admin_router = APIRouter(route_class=DishkaRoute)


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
