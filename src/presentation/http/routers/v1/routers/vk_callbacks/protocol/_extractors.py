import json
from typing import Any

from pydantic import ValidationError

from application.common.dto.vk import VKPollDTO, VKWallPostDTO
from presentation.http.dto.request import VKCallbackWallPostSchema
from presentation.http.routers.v1.routers.vk_callbacks.protocol.event_objects import (
    VKCommentObjectSchema,
    VKLikeObjectSchema,
    VKMessageObjectSchema,
    VKPollVoteObjectSchema,
    VKRepostObjectSchema,
    VKUserObjectSchema,
    VKWallPostAttachmentSchema,
    VKWallPostObjectSchema,
    VKWallPostPollSchema,
)


def extract_like_user_id(*, like_object: VKLikeObjectSchema | None) -> int | None:
    return normalize_vk_user_id(raw_user_id=like_object.liker_id if like_object else None)


def extract_comment_user_id(*, comment_object: VKCommentObjectSchema | None) -> int | None:
    return normalize_vk_user_id(raw_user_id=comment_object.from_id if comment_object else None)


def extract_poll_user_id(*, poll_vote_object: VKPollVoteObjectSchema | None) -> int | None:
    return normalize_vk_user_id(raw_user_id=poll_vote_object.user_id if poll_vote_object else None)


def extract_repost_author_user_id(*, repost_object: VKRepostObjectSchema | None) -> int | None:
    return normalize_vk_user_id(raw_user_id=repost_object.from_id if repost_object else None)


def is_repost_published_on_author_wall(*, repost_object: VKRepostObjectSchema | None) -> bool:
    if repost_object is None:
        return False

    from_id = extract_repost_author_user_id(repost_object=repost_object)
    wall_owner_id = normalize_vk_user_id(raw_user_id=repost_object.owner_id)
    return from_id is not None and wall_owner_id is not None and from_id == wall_owner_id


def extract_vk_user_id(
    *,
    message_object: VKMessageObjectSchema | None,
    user_object: VKUserObjectSchema | None,
) -> int | None:
    message = message_object.message if message_object is not None else None
    raw_user_id: Any = (
        message.from_id
        if message and message.from_id is not None
        else message.user_id
        if message and message.user_id is not None
        else user_object.user_id
        if user_object and user_object.user_id is not None
        else user_object.from_id
        if user_object is not None
        else None
    )
    return normalize_vk_user_id(raw_user_id=raw_user_id)


def extract_first_name(
    *,
    message_object: VKMessageObjectSchema | None,
    user_object: VKUserObjectSchema | None,
) -> str | None:
    if user_object is not None and user_object.first_name:
        return user_object.first_name

    message = message_object.message if message_object is not None else None
    if message is not None and message.first_name:
        return message.first_name
    return None


def extract_last_name(
    *,
    message_object: VKMessageObjectSchema | None,
    user_object: VKUserObjectSchema | None,
) -> str | None:
    if user_object is not None and user_object.last_name:
        return user_object.last_name

    message = message_object.message if message_object is not None else None
    if message is not None and message.last_name:
        return message.last_name
    return None


def extract_message_text(*, message_object: VKMessageObjectSchema | None) -> str:
    message = message_object.message if message_object is not None else None
    return message.text if message and message.text is not None else ""


def extract_ref_key(
    *,
    event_object_extra: dict[str, Any] | None,
    message_object: VKMessageObjectSchema | None,
) -> str | None:
    key = (event_object_extra or {}).get("key")
    if key is not None and str(key).strip():
        return str(key).strip()

    message = message_object.message if message_object is not None else None
    if message is not None and message.ref is not None and message.ref.strip():
        return message.ref.strip()

    return None


def parse_button_payload(*, message_object: VKMessageObjectSchema | None) -> dict[str, Any] | None:
    message = message_object.message if message_object is not None else None
    raw_payload = message.payload if message and message.payload is not None else None
    if raw_payload is None:
        return None

    try:
        parsed = json.loads(raw_payload)
    except (json.JSONDecodeError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


def extract_commented_post_external_ids(
    *,
    comment_object: VKCommentObjectSchema | None,
) -> tuple[str, ...]:
    if comment_object is None:
        return ()

    post = VKWallPostDTO(
        owner_id=comment_object.owner_id,
        post_id=comment_object.post_id,
    )
    return post.external_id_variants


def extract_liked_post(*, like_object: VKLikeObjectSchema | None) -> VKWallPostDTO | None:
    if like_object is None:
        return None
    return VKWallPostDTO(
        owner_id=like_object.object_owner_id,
        post_id=like_object.object_id,
    )


def extract_liked_post_external_ids(
    *,
    like_object: VKLikeObjectSchema | None,
) -> tuple[str, ...]:
    post = extract_liked_post(like_object=like_object)
    if post is None:
        return ()
    return post.external_id_variants


def extract_repost_external_id(*, wall_post_object: VKWallPostObjectSchema | None) -> str | None:
    post = extract_wall_post(wall_post_object=wall_post_object)
    return post.external_id if post is not None else None


def extract_reposted_wall_post_external_ids(
    *,
    repost_object: VKRepostObjectSchema | None,
) -> tuple[str, ...]:
    if repost_object is None:
        return ()

    external_ids: set[str] = set()
    for copied_post in repost_object.copy_history:
        post = _to_wall_post_dto(copied_post=copied_post)
        if post is not None:
            external_ids.update(post.external_id_variants)
    return tuple(sorted(external_ids))


def extract_wall_post(*, wall_post_object: VKWallPostObjectSchema | None) -> VKWallPostDTO | None:
    if wall_post_object is None:
        return None
    return VKWallPostDTO(
        owner_id=wall_post_object.owner_id,
        post_id=wall_post_object.post_id,
    )


def extract_wall_post_text(*, wall_post_object: VKWallPostObjectSchema | None) -> str:
    return wall_post_object.text if wall_post_object and wall_post_object.text else ""


def extract_wall_post_poll(*, wall_post_object: VKWallPostObjectSchema | None) -> VKPollDTO | None:
    poll = _find_wall_post_poll_attachment(wall_post_object=wall_post_object)
    if poll is None or poll.owner_id is None or poll.poll_id is None:
        return None
    return VKPollDTO(owner_id=poll.owner_id, poll_id=poll.poll_id)


def extract_wall_post_poll_question(*, wall_post_object: VKWallPostObjectSchema | None) -> str | None:
    poll = _find_wall_post_poll_attachment(wall_post_object=wall_post_object)
    if poll is None or poll.question is None or not poll.question.strip():
        return None
    return poll.question.strip()


def extract_voted_poll(*, poll_vote_object: VKPollVoteObjectSchema | None) -> VKPollDTO | None:
    if poll_vote_object is None:
        return None
    return VKPollDTO(
        owner_id=poll_vote_object.owner_id,
        poll_id=poll_vote_object.poll_id,
    )


def extract_voted_poll_external_ids(
    *,
    poll_vote_object: VKPollVoteObjectSchema | None,
) -> tuple[str, ...]:
    poll = extract_voted_poll(poll_vote_object=poll_vote_object)
    if poll is None:
        return ()
    return poll.external_id_variants


def normalize_vk_user_id(*, raw_user_id: Any) -> int | None:
    if raw_user_id is None:
        return None

    try:
        vk_user_id = int(raw_user_id)
    except (TypeError, ValueError):
        return None
    return vk_user_id if vk_user_id > 0 else None


def _find_wall_post_poll_attachment(
    *,
    wall_post_object: VKWallPostObjectSchema | None,
) -> VKWallPostPollSchema | None:
    if wall_post_object is None:
        return None

    for raw_attachment in wall_post_object.attachments:
        if not isinstance(raw_attachment, dict):
            continue

        try:
            attachment = VKWallPostAttachmentSchema.model_validate(raw_attachment)
        except ValidationError:
            continue

        if attachment.type != "poll" or attachment.poll is None:
            continue
        return attachment.poll

    return None


def _to_wall_post_dto(copied_post: VKCallbackWallPostSchema) -> VKWallPostDTO | None:
    if copied_post.owner_id is None or copied_post.post_id is None:
        return None
    return VKWallPostDTO(owner_id=copied_post.owner_id, post_id=copied_post.post_id)
