import re
from dataclasses import dataclass

from loguru import logger

from application.base_interactor import Interactor
from application.common.dto.task import (
    VKLikeTaskCreationStatus,
    VKPostTasksCreationDTO,
    VKPostTasksCreationStatus,
    VKRepostTaskCreationStatus,
)
from application.common.dto.vk import VKWallPostDTO
from application.interface.repositories.tasks import ITaskRepository
from application.interface.uow import IUnitOfWork
from domain.enums.task import TaskRepeatPolicy

POST_TASKS_MARKER = "#volnateca"
POST_TASKS_MARKER_PATTERN = re.compile(rf"{re.escape(POST_TASKS_MARKER)}(?!_\w)", re.IGNORECASE)
POST_TASKS_REPOST_POINTS_PATTERN = re.compile(
    rf"{re.escape(POST_TASKS_MARKER)}_repost_points_(?P<points>\d+)", re.IGNORECASE
)
POST_TASKS_LIKE_POINTS_PATTERN = re.compile(
    rf"{re.escape(POST_TASKS_MARKER)}_like_points_(?P<points>\d+)", re.IGNORECASE
)
POST_TASKS_WEEK_PATTERN = re.compile(rf"{re.escape(POST_TASKS_MARKER)}_week_(?P<week>\d+)", re.IGNORECASE)
DEFAULT_REPOST_POINTS = 20
DEFAULT_LIKE_POINTS = 10
MAX_TASK_DESCRIPTION_LENGTH = 500


@dataclass(slots=True, frozen=True, kw_only=True)
class CreateVKPostTasksCommand:
    event_id: str | None
    group_id: int
    post: VKWallPostDTO
    text: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ParsedVKPostMarker:
    repost_points: int
    like_points: int
    week_number: int | None


class CreateVKPostTasksHandler(
    Interactor[CreateVKPostTasksCommand, VKPostTasksCreationDTO],
):
    def __init__(
        self,
        task_repository: ITaskRepository,
        uow: IUnitOfWork,
    ) -> None:
        self.task_repository = task_repository
        self.uow = uow

    async def __call__(
        self,
        command_data: CreateVKPostTasksCommand,
    ) -> VKPostTasksCreationDTO:
        canonical_post = self._get_canonical_group_post(
            group_id=command_data.group_id,
            post=command_data.post,
        )
        if canonical_post is None:
            return VKPostTasksCreationDTO(
                status=VKPostTasksCreationStatus.WRONG_WALL_OWNER,
                event_id=command_data.event_id,
                reason="wall_post_owner_is_not_callback_group",
            )

        parsed_marker = self._parse_marker(text=command_data.text)
        if parsed_marker is None:
            return VKPostTasksCreationDTO(
                status=VKPostTasksCreationStatus.IGNORED,
                event_id=command_data.event_id,
                external_id=canonical_post.external_id,
                reason="volnateca_marker_not_found",
            )
        if parsed_marker.repost_points <= 0 or parsed_marker.like_points <= 0:
            return VKPostTasksCreationDTO(
                status=VKPostTasksCreationStatus.INVALID_MARKER,
                event_id=command_data.event_id,
                external_id=canonical_post.external_id,
                reason="points_must_be_positive",
            )
        if parsed_marker.week_number is not None and not 1 <= parsed_marker.week_number <= 12:
            return VKPostTasksCreationDTO(
                status=VKPostTasksCreationStatus.INVALID_MARKER,
                event_id=command_data.event_id,
                external_id=canonical_post.external_id,
                week_number=parsed_marker.week_number,
                reason="week_number_must_be_between_1_and_12",
            )

        description = self._build_task_description(
            post=canonical_post,
            text=command_data.text,
        )

        repost_result = await self.task_repository.create_repost_task_if_not_exists(
            code=f"vk_repost_wall_{abs(canonical_post.owner_id)}_{canonical_post.post_id}",
            task_name=self._build_repost_task_name(parsed_marker=parsed_marker),
            description=description,
            external_id=canonical_post.external_id,
            points=parsed_marker.repost_points,
            week_number=parsed_marker.week_number,
            repeat_policy=TaskRepeatPolicy.ONCE,
            event_id=command_data.event_id,
        )
        like_result = await self.task_repository.create_like_task_if_not_exists(
            code=f"vk_like_wall_{abs(canonical_post.owner_id)}_{canonical_post.post_id}",
            task_name=self._build_like_task_name(parsed_marker=parsed_marker),
            description=description,
            external_id=canonical_post.external_id,
            points=parsed_marker.like_points,
            week_number=parsed_marker.week_number,
            repeat_policy=TaskRepeatPolicy.ONCE,
            event_id=command_data.event_id,
        )

        await self.uow.commit()

        if (
            repost_result.status == VKRepostTaskCreationStatus.ALREADY_EXISTS
            and like_result.status == VKLikeTaskCreationStatus.ALREADY_EXISTS
        ):
            overall_status = VKPostTasksCreationStatus.ALREADY_EXISTS
        else:
            overall_status = VKPostTasksCreationStatus.CREATED

        result = VKPostTasksCreationDTO(
            status=overall_status,
            event_id=command_data.event_id,
            external_id=canonical_post.external_id,
            repost_tasks_id=repost_result.tasks_id,
            like_tasks_id=like_result.tasks_id,
            repost_points=parsed_marker.repost_points,
            like_points=parsed_marker.like_points,
            week_number=parsed_marker.week_number,
        )
        logger.info(
            "TEMP VK post tasks creation handled: "
            "event_id={}, status={}, external_id={}, "
            "repost_tasks_id={}, like_tasks_id={}, "
            "repost_points={}, like_points={}, week_number={}",
            command_data.event_id,
            result.status,
            result.external_id,
            result.repost_tasks_id,
            result.like_tasks_id,
            result.repost_points,
            result.like_points,
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
    def _parse_marker(text: str) -> ParsedVKPostMarker | None:
        # Check for #volnateca marker but exclude sub-tags like #volnateca_week_N etc.
        # We look for a standalone "#volnateca" word (not followed by "_")
        if not POST_TASKS_MARKER_PATTERN.search(text):
            return None

        repost_points = DEFAULT_REPOST_POINTS
        repost_match = POST_TASKS_REPOST_POINTS_PATTERN.search(text)
        if repost_match is not None:
            repost_points = int(repost_match.group("points"))

        like_points = DEFAULT_LIKE_POINTS
        like_match = POST_TASKS_LIKE_POINTS_PATTERN.search(text)
        if like_match is not None:
            like_points = int(like_match.group("points"))

        week_number = None
        week_match = POST_TASKS_WEEK_PATTERN.search(text)
        if week_match is not None:
            week_number = int(week_match.group("week"))

        return ParsedVKPostMarker(
            repost_points=repost_points,
            like_points=like_points,
            week_number=week_number,
        )

    @staticmethod
    def _build_repost_task_name(parsed_marker: ParsedVKPostMarker) -> str:
        if parsed_marker.repost_points >= 60:
            return "Сделать репост партнёрского поста"
        if parsed_marker.week_number is not None:
            return f"Сделать репост поста недели {parsed_marker.week_number}"
        return "Сделать репост поста"

    @staticmethod
    def _build_like_task_name(parsed_marker: ParsedVKPostMarker) -> str:
        if parsed_marker.week_number is not None:
            return f"Поставить лайк посту недели {parsed_marker.week_number}"
        return "Поставить лайк посту"

    @staticmethod
    def _build_task_description(
        post: VKWallPostDTO,
        text: str,
    ) -> str:
        cleaned_text = "\n".join(
            line for line in text.splitlines() if not line.strip().lower().startswith(POST_TASKS_MARKER)
        ).strip()
        description = f"Автоматически создано из VK-поста {post.external_id}."
        if cleaned_text:
            description = f"{description}\n\n{cleaned_text}"
        return description[:MAX_TASK_DESCRIPTION_LENGTH]
