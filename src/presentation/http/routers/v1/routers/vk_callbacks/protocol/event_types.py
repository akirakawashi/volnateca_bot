from enum import StrEnum


class VKEventType(StrEnum):
    CONFIRMATION = "confirmation"
    GROUP_JOIN = "group_join"
    LIKE_ADD = "like_add"
    LIKE_REMOVE = "like_remove"
    MESSAGE_ALLOW = "message_allow"
    MESSAGE_NEW = "message_new"
    POLL_VOTE_NEW = "poll_vote_new"
    WALL_POST_NEW = "wall_post_new"
    WALL_REPLY_NEW = "wall_reply_new"


class VKEventGroups:
    COMMENT = frozenset((VKEventType.WALL_REPLY_NEW,))
    LIKE = frozenset((VKEventType.LIKE_ADD, VKEventType.LIKE_REMOVE))
    POLL = frozenset((VKEventType.POLL_VOTE_NEW,))
    POST_CREATE = frozenset((VKEventType.WALL_POST_NEW,))
    REGISTRATION = frozenset((VKEventType.MESSAGE_NEW, VKEventType.MESSAGE_ALLOW))
    SUBSCRIPTION = frozenset((VKEventType.GROUP_JOIN,))
