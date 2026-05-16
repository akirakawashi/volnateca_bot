import re
from functools import lru_cache
from urllib.parse import unquote

VKAttachmentType = tuple[str, ...]
DEFAULT_VK_ATTACHMENT_TYPES: VKAttachmentType = ("photo", "video", "doc", "clip")


def extract_vk_attachment(
    value: str,
    *,
    allowed_types: VKAttachmentType = DEFAULT_VK_ATTACHMENT_TYPES,
) -> str | None:
    candidates = [value]

    try:
        decoded = unquote(value)
    except Exception:
        decoded = value

    if decoded != value:
        candidates.append(decoded)

    pattern = _build_attachment_pattern(allowed_types)
    for candidate in candidates:
        match = pattern.search(candidate)
        if match is not None:
            return match.group(0)

    return None


def extract_vk_photo_attachment(value: str) -> str | None:
    return extract_vk_attachment(value, allowed_types=("photo",))


@lru_cache(maxsize=None)
def _build_attachment_pattern(allowed_types: VKAttachmentType) -> re.Pattern[str]:
    allowed = "|".join(re.escape(attachment_type) for attachment_type in allowed_types)
    return re.compile(rf"(?:{allowed})-?\d+_\d+(?:_[A-Za-z0-9]+)?")
