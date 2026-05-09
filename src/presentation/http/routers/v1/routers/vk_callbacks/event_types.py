from enum import StrEnum


class VKEventType(StrEnum):
    CONFIRMATION = "confirmation"
    GROUP_JOIN = "group_join"
    LIKE_ADD = "like_add"
    LIKE_REMOVE = "like_remove"
    MESSAGE_ALLOW = "message_allow"
    MESSAGE_NEW = "message_new"
    WALL_POST_NEW = "wall_post_new"
    WALL_REPOST = "wall_repost"


class VKEventGroups:
    LIKE = frozenset((VKEventType.LIKE_ADD, VKEventType.LIKE_REMOVE))
    REGISTRATION = frozenset((VKEventType.MESSAGE_NEW, VKEventType.MESSAGE_ALLOW))
    REPOST = frozenset((VKEventType.WALL_REPOST,))
    SUBSCRIPTION = frozenset((VKEventType.GROUP_JOIN,))
    WALL_POST = frozenset((VKEventType.WALL_POST_NEW,))
