from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from application.admin.interface.db_manager import IDBManager

# Все таблицы перечислены в порядке «листья → корни»;
# RESTART IDENTITY CASCADE позволяет PostgreSQL самому разрешить
# порядок зависимостей, но явный список исключает случайные таблицы.
_ALL_TABLES = ", ".join([
    "quiz_answers",
    "prize_promo_codes",
    "quiz_question_options",
    "prize_redemptions",
    "task_completions",
    "referrals",
    "user_achievements",
    "user_daily_activities",
    "transactions",
    "quiz_questions",
    "tasks",
    "users",
    "prizes",
    "achievements",
])

_TRUNCATE_SQL = text(f"TRUNCATE {_ALL_TABLES} RESTART IDENTITY CASCADE")


class DBManager(IDBManager):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def truncate_all(self) -> None:
        await self._session.execute(_TRUNCATE_SQL)
        await self._session.commit()
