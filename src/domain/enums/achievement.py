from enum import Enum


class AchievementType(str, Enum):
    """Тип достижения или бонусного правила проекта."""

    REFERRAL_MILESTONE = "referral_milestone"  # Бонус за 3/5/10 приглашённых друзей
    DAILY_STREAK = "daily_streak"  # Бонус за 7/30/60 дней активности подряд
    WEEK_COMPLETION = "week_completion"  # Бонус за выполнение всех заданий недели
    QUIZ_STREAK = "quiz_streak"  # Бонус за серию правильных ответов в викторинах
    MONTHLY_RATING = "monthly_rating"  # Бонус за место в месячном рейтинге
    PROJECT_COMPLETION = "project_completion"  # Бонус за прохождение всего проекта
    CUSTOM = "custom"  # Нестандартный бонус


class AchievementRepeatPolicy(str, Enum):
    """Правило повторной выдачи одного достижения пользователю."""

    ONCE = "once"  # Один раз за весь проект
    WEEKLY = "weekly"  # Один раз в рамках недели проекта
    MONTHLY = "monthly"  # Один раз в рамках календарного месяца


__all__ = [
    "AchievementRepeatPolicy",
    "AchievementType",
]
