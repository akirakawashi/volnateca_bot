def normalize_page(*, page: int, total_pages: int) -> int:
    return min(max(1, page), total_pages)


def parse_vk_user_id(raw_ref: str | None) -> int | None:
    if raw_ref is None:
        return None
    try:
        return int(raw_ref)
    except (TypeError, ValueError):
        return None
