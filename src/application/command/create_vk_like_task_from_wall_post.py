import re
from dataclasses import dataclass

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKLikeTaskCreationDTO,
    VKLikeTaskCreationStatus,
)
from application.common.dto.vk import VKWallPostDTO
from application.interface.repositories.tasks import ITaskCompletionRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy

LIKE_TASK_MARKER = "#volnateca_like_task"
LIKE_TASK_POINTS_PATTERN = re.compile(r"#volnateca_points_(?P<points>\d+)", re.IGNORECASE)
LIKE_TASK_WEEK_PATTERN = re.compile(r"#volnateca_week_(?P<week>\d+)", re.IGNORECASE)
DEFAULT_LIKE_TASK_POINTS = 10
MAX_TASK_DESCRIPTION_LENGTH = 500


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateVKLikeTaskFromWallPostCommand:
    event_id: str | None
    group_id: int
    post: VKWallPostDTO
    text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ParsedVKLikeTaskMarker:
    points: int
    week_number: int | None


class CreateVKLikeTaskFromWallPostHandler(
    Interactor[CreateVKLikeTaskFromWallPostCommand, VKLikeTaskCreationDTO],
):
    def __init__(
        self,
        repository: ITaskCompletionRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.repository = repository
        self.uow = uow

    async def __call__(
        self,
        command_data: CreateVKLikeTaskFromWallPostCommand,
    ) -> VKLikeTaskCreationDTO:
        canonical_post = self._get_canonical_group_post(
            group_id=command_data.group_id,
            post=command_data.post,
        )
        if canonical_post is None:
            return VKLikeTaskCreationDTO(
                status=VKLikeTaskCreationStatus.WRONG_WALL_OWNER,
                event_id=command_data.event_id,
                reason="wall_post_owner_is_not_callback_group",
            )

        parsed_marker = self._parse_marker(text=command_data.text)
        if parsed_marker is None:
            return VKLikeTaskCreationDTO(
                status=VKLikeTaskCreationStatus.IGNORED,
                event_id=command_data.event_id,
                external_id=canonical_post.external_id,
                reason="like_task_marker_not_found",
            )
        if parsed_marker.points <= 0:
            return VKLikeTaskCreationDTO(
                status=VKLikeTaskCreationStatus.INVALID_MARKER,
                event_id=command_data.event_id,
                external_id=canonical_post.external_id,
                reason="points_must_be_positive",
            )
        if parsed_marker.week_number is not None and not 1 <= parsed_marker.week_number <= 12:
            return VKLikeTaskCreationDTO(
                status=VKLikeTaskCreationStatus.INVALID_MARKER,
                event_id=command_data.event_id,
                external_id=canonical_post.external_id,
                points=parsed_marker.points,
                week_number=parsed_marker.week_number,
                reason="week_number_must_be_between_1_and_12",
            )

        result = await self.repository.create_like_task_if_not_exists(
            code=self._build_task_code(post=canonical_post),
            task_name=self._build_task_name(parsed_marker=parsed_marker),
            description=self._build_task_description(
                post=canonical_post,
                text=command_data.text,
            ),
            external_id=canonical_post.external_id,
            points=parsed_marker.points,
            week_number=parsed_marker.week_number,
            repeat_policy=TaskRepeatPolicy.ONCE,
            event_id=command_data.event_id,
        )
        await self.uow.commit()
        logger.info(
            "TEMP VK like task creation handled: "
            "event_id={}, status={}, tasks_id={}, code={}, external_id={}, points={}, week_number={}",
            command_data.event_id,
            result.status,
            result.tasks_id,
            result.code,
            result.external_id,
            result.points,
            result.week_number,
        )
        return result

    @staticmethod
    def _get_canonical_group_post(
        group_id: int,
        post: VKWallPostDTO,
    ) -> VKWallPostDTO | None:
        if abs(post.owner_id) != group_id:
            return None
        return VKWallPostDTO(owner_id=-abs(group_id), post_id=post.post_id)

    @staticmethod
    def _parse_marker(text: str) -> ParsedVKLikeTaskMarker | None:
        if LIKE_TASK_MARKER not in text.lower():
            return None

        points = DEFAULT_LIKE_TASK_POINTS
        points_match = LIKE_TASK_POINTS_PATTERN.search(text)
        if points_match is not None:
            points = int(points_match.group("points"))

        week_number = None
        week_match = LIKE_TASK_WEEK_PATTERN.search(text)
        if week_match is not None:
            week_number = int(week_match.group("week"))

        return ParsedVKLikeTaskMarker(points=points, week_number=week_number)

    @staticmethod
    def _build_task_code(post: VKWallPostDTO) -> str:
        return f"vk_like_wall_{abs(post.owner_id)}_{post.post_id}"

    @staticmethod
    def _build_task_name(parsed_marker: ParsedVKLikeTaskMarker) -> str:
        if parsed_marker.week_number is not None:
            return f"Поставить лайк посту недели {parsed_marker.week_number}"
        return "Поставить лайк посту"

    @staticmethod
    def _build_task_description(
        post: VKWallPostDTO,
        text: str,
    ) -> str:
        cleaned_text = "\n".join(
            line
            for line in text.splitlines()
            if not line.strip().lower().startswith("#volnateca_")
        ).strip()
        description = f"Автоматически создано из VK-поста {post.external_id}."
        if cleaned_text:
            description = f"{description}\n\n{cleaned_text}"
        return description[:MAX_TASK_DESCRIPTION_LENGTH]
