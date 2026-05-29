from dataclasses import dataclass
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError

from application.common.dto.vk import VKPollDTO, VKWallPostDTO
from presentation.http.dto.request import VKCallbackSchema
from presentation.http.routers.v1.routers.vk_callbacks.protocol.extractors import (
    extract_comment_user_id,
    extract_commented_post_external_ids,
    extract_first_name,
    extract_last_name,
    extract_like_user_id,
    extract_liked_post,
    extract_liked_post_external_ids,
    extract_message_text,
    extract_poll_user_id,
    extract_ref_key,
    extract_repost_author_user_id,
    extract_repost_external_id,
    extract_reposted_wall_post_external_ids,
    extract_vk_user_id,
    extract_voted_poll,
    extract_voted_poll_external_ids,
    extract_wall_post,
    extract_wall_post_poll,
    extract_wall_post_poll_question,
    extract_wall_post_text,
    is_repost_published_on_author_wall,
    parse_button_payload,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.event_objects import (
    VKCallbackEventObjectSchema,
    VKCommentObjectSchema,
    VKLikeObjectSchema,
    VKMessageObjectSchema,
    VKPollVoteObjectSchema,
    VKRepostObjectSchema,
    VKUserObjectSchema,
    VKWallPostObjectSchema,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.event_types import VKEventGroups, VKEventType

EventObjectT = TypeVar("EventObjectT", bound=VKCallbackEventObjectSchema)


@dataclass(slots=True, frozen=True)
class VKCallbackPayload:
    """Удобная оболочка над сырым VK callback payload.

    VK присылает разные формы object/message для похожих сценариев, поэтому
    этот класс централизует распознавание типа события, нормализацию user_id
    и безопасный разбор вложенных объектов без исключений наружу.
    """

    data: VKCallbackSchema

    # Метаданные события VK

    @property
    def type(self) -> str | None:
        return self.data.type

    @property
    def group_id(self) -> int | None:
        return self.data.group_id

    @property
    def event_id(self) -> str | None:
        return self.data.event_id

    # Классификация событий

    def is_confirmation(self) -> bool:
        return self.type == VKEventType.CONFIRMATION

    def is_like(self) -> bool:
        return self.type in VKEventGroups.LIKE

    def is_poll_vote_event(self) -> bool:
        return self.type in VKEventGroups.POLL

    def is_repost(self) -> bool:
        return self.type in VKEventGroups.REPOST

    def is_subscription_event(self) -> bool:
        return self.type in VKEventGroups.SUBSCRIPTION

    def is_comment_event(self) -> bool:
        return self.type in VKEventGroups.COMMENT

    def is_registration_event(self) -> bool:
        return self.type in VKEventGroups.REGISTRATION

    def is_message_new(self) -> bool:
        return self.type == VKEventType.MESSAGE_NEW

    def is_wall_post_event(self) -> bool:
        return self.type in VKEventGroups.POST_CREATE

    # Проверка события VK

    def is_expected_group(self, expected_group_id: int) -> bool:
        return self.group_id == expected_group_id

    def has_valid_secret(self, expected_secret: str) -> bool:
        return self.data.secret == expected_secret

    # Извлечение пользователя

    def get_like_user_id(self) -> int | None:
        return extract_like_user_id(like_object=self.get_like_object())

    def get_comment_user_id(self) -> int | None:
        return extract_comment_user_id(comment_object=self.get_comment_object())

    def get_poll_user_id(self) -> int | None:
        return extract_poll_user_id(poll_vote_object=self.get_poll_vote_object())

    def get_primary_vk_user_id(self) -> int | None:
        if self.is_like():
            return self.get_like_user_id()
        if self.is_poll_vote_event():
            return self.get_poll_user_id()
        if self.is_repost():
            return self.get_repost_user_id()
        if self.is_comment_event():
            return self.get_comment_user_id()
        return self.get_vk_user_id()

    def get_repost_user_id(self) -> int | None:
        """Возвращает автора репоста только для репоста на собственной стене."""

        repost_object = self.get_repost_object()
        if not is_repost_published_on_author_wall(repost_object=repost_object):
            return None
        return extract_repost_author_user_id(repost_object=repost_object)

    def get_vk_user_id(self) -> int | None:
        """Достаёт user_id из message/user object с учётом разных форматов VK."""

        return extract_vk_user_id(
            message_object=self.get_message_object(),
            user_object=self.get_user_object(),
        )

    def get_first_name(self) -> str | None:
        return extract_first_name(
            message_object=self.get_message_object(),
            user_object=self.get_user_object(),
        )

    def get_last_name(self) -> str | None:
        return extract_last_name(
            message_object=self.get_message_object(),
            user_object=self.get_user_object(),
        )

    def get_message_text(self) -> str:
        return extract_message_text(message_object=self.get_message_object())

    def get_ref_key(self) -> str | None:
        """Возвращает реферальный ключ из события VK.

        VK передаёт ref двумя способами:
        - message_allow: object.key — приходит когда пользователь разрешил сообщения
          перейдя по ссылке vk.com/write-{group_id}?ref={value}
        - message_new: message.ref — отдельное поле объекта сообщения
        """
        return extract_ref_key(
            event_object_extra=self.data.event_object.model_extra,
            message_object=self.get_message_object(),
        )

    def get_button_payload(self) -> dict[str, Any] | None:
        """Возвращает распарсенный JSON payload нажатой кнопки клавиатуры VK.

        VK передаёт payload как строку с JSON внутри message.payload.
        Возвращает None если payload отсутствует или не является валидным JSON-объектом.
        """
        return parse_button_payload(message_object=self.get_message_object())

    # Извлечение постов

    def get_commented_post_external_ids(self) -> tuple[str, ...]:
        return extract_commented_post_external_ids(comment_object=self.get_comment_object())

    def get_liked_post(self) -> VKWallPostDTO | None:
        return extract_liked_post(like_object=self.get_like_object())

    def get_liked_post_external_ids(self) -> tuple[str, ...]:
        return extract_liked_post_external_ids(like_object=self.get_like_object())

    def get_repost_external_id(self) -> str | None:
        return extract_repost_external_id(wall_post_object=self.get_wall_post_object())

    def get_reposted_wall_post_external_ids(self) -> tuple[str, ...]:
        """Возвращает все варианты external_id исходных постов из copy_history."""

        return extract_reposted_wall_post_external_ids(repost_object=self.get_repost_object())

    def get_wall_post(self) -> VKWallPostDTO | None:
        return extract_wall_post(wall_post_object=self.get_wall_post_object())

    def get_wall_post_text(self) -> str:
        return extract_wall_post_text(wall_post_object=self.get_wall_post_object())

    def get_wall_post_poll(self) -> VKPollDTO | None:
        return extract_wall_post_poll(wall_post_object=self.get_wall_post_object())

    def get_wall_post_poll_question(self) -> str | None:
        return extract_wall_post_poll_question(wall_post_object=self.get_wall_post_object())

    def get_voted_poll(self) -> VKPollDTO | None:
        return extract_voted_poll(poll_vote_object=self.get_poll_vote_object())

    def get_voted_poll_external_ids(self) -> tuple[str, ...]:
        return extract_voted_poll_external_ids(poll_vote_object=self.get_poll_vote_object())

    # Извлечение типизированного объекта события

    def get_comment_object(self) -> VKCommentObjectSchema | None:
        if not self.is_comment_event():
            return None
        return self._parse_event_object(schema=VKCommentObjectSchema)

    def get_like_object(self) -> VKLikeObjectSchema | None:
        if not self.is_like():
            return None
        return self._parse_event_object(schema=VKLikeObjectSchema)

    def get_poll_vote_object(self) -> VKPollVoteObjectSchema | None:
        if not self.is_poll_vote_event():
            return None
        return self._parse_event_object(schema=VKPollVoteObjectSchema)

    def get_repost_object(self) -> VKRepostObjectSchema | None:
        if not self.is_repost():
            return None
        return self._parse_event_object(schema=VKRepostObjectSchema)

    def get_wall_post_object(self) -> VKWallPostObjectSchema | None:
        return self._parse_event_object(schema=VKWallPostObjectSchema)

    def get_message_object(self) -> VKMessageObjectSchema | None:
        return self._parse_event_object(schema=VKMessageObjectSchema)

    def get_user_object(self) -> VKUserObjectSchema | None:
        return self._parse_event_object(schema=VKUserObjectSchema)

    # Помощники для логирования

    def get_event_object_keys(self) -> tuple[str, ...]:
        return self._get_present_keys(model=self.data.event_object)

    def get_message_keys(self) -> tuple[str, ...]:
        if self.data.event_object.message is None:
            return ()
        return self._get_present_keys(model=self.data.event_object.message)

    # Внутренняя логика

    def _parse_event_object(self, *, schema: Type[EventObjectT]) -> EventObjectT | None:
        try:
            return schema.model_validate(self.data.event_object.model_dump(by_alias=True))
        except ValidationError:
            return None

    @staticmethod
    def _get_present_keys(model: BaseModel) -> tuple[str, ...]:
        extra_keys = set(model.model_extra or {})
        return tuple(sorted(model.model_fields_set | extra_keys))
