from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status

from application.admin.command.create_quiz import CreateQuizHandler
from application.admin.command.quiz import (
    ListQuizzesCommand,
    ListQuizzesHandler,
    UpdateQuizQuestionImageHandler,
)
from presentation.http.dto.admin.quiz import (
    CreateQuizRequestSchema,
    CreatedQuizResponseSchema,
    QuizAdminResponseSchema,
    UpdateQuizQuestionImageRequestSchema,
)

quiz_admin_router = APIRouter(route_class=DishkaRoute)


@quiz_admin_router.get(
    path="/quiz",
    name="Получить список квизов",
    response_model=list[QuizAdminResponseSchema],
    status_code=status.HTTP_200_OK,
)
async def list_quizzes(
    handler: FromDishka[ListQuizzesHandler],
) -> list[QuizAdminResponseSchema]:
    result = await handler(ListQuizzesCommand())
    return [QuizAdminResponseSchema.from_dto(item) for item in result]


@quiz_admin_router.post(
    path="/quiz",
    name="Создать квиз",
    response_model=CreatedQuizResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_quiz(
    data: CreateQuizRequestSchema,
    handler: FromDishka[CreateQuizHandler],
) -> CreatedQuizResponseSchema:
    result = await handler(data.to_command())
    return CreatedQuizResponseSchema.from_dto(result)


@quiz_admin_router.patch(
    path="/quiz/questions/{quiz_questions_id}/image",
    name="Обновить изображение вопроса квиза",
    response_model=QuizAdminResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_quiz_question_image(
    quiz_questions_id: int,
    data: UpdateQuizQuestionImageRequestSchema,
    handler: FromDishka[UpdateQuizQuestionImageHandler],
) -> QuizAdminResponseSchema:
    try:
        result = await handler(data.to_command(quiz_questions_id=quiz_questions_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос квиза не найден")
    return QuizAdminResponseSchema.from_dto(result)
