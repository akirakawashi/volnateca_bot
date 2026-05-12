from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from application.admin.command.create_quiz import CreateQuizHandler
from presentation.http.dto.admin.quiz import CreateQuizRequestSchema, CreatedQuizResponseSchema

quiz_admin_router = APIRouter(route_class=DishkaRoute)


@quiz_admin_router.post(
    path="/quiz",
    name="Создать квиз",
    response_model=CreatedQuizResponseSchema,
    status_code=201,
)
async def create_quiz(
    data: CreateQuizRequestSchema,
    handler: FromDishka[CreateQuizHandler],
) -> CreatedQuizResponseSchema:
    result = await handler(data.to_command())
    return CreatedQuizResponseSchema.from_dto(result)
