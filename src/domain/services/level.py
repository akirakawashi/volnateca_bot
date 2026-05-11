LEVEL_THRESHOLDS: dict[int, int] = {
    1: 0,
    2: 300,
    3: 1500,
    4: 5000,
}

LEVEL_NAMES: dict[int, str] = {
    1: "Новая волна",
    2: "Прибой",
    3: "Шторм",
    4: "Цунами",
}


def get_level(earned_points_total: int) -> int:
    """Возвращает уровень пользователя по суммарно заработанным очкам."""
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS.items():
        if earned_points_total >= threshold:
            level = lvl
    return level


def get_level_name(level: int) -> str:
    return LEVEL_NAMES.get(level, "Новая волна")


__all__ = ["LEVEL_NAMES", "LEVEL_THRESHOLDS", "get_level", "get_level_name"]
