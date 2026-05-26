from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from application.admin.interface.db_manager import IDBManager

# Очищаем только рабочие таблицы.
# Справочники message_templates и achievements остаются на месте:
# они относятся к базовой конфигурации окружения, а не к пользовательским данным.
# Таблицы перечислены в порядке «листья → корни»; RESTART IDENTITY CASCADE
# позволяет PostgreSQL самому разрешить порядок зависимостей.
_TRUNCATED_TABLES = ", ".join(
    [
        "quiz_answers",
        "prize_promo_codes",
        "quiz_question_options",
        "prize_redemptions",
        "task_completions",
        "referrals",
        "user_achievements",
        "transactions",
        "quiz_questions",
        "tasks",
        "users",
        "prizes",
    ]
)

_TRUNCATE_SQL = text(f"TRUNCATE {_TRUNCATED_TABLES} RESTART IDENTITY CASCADE")


class DBManager(IDBManager):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def truncate_all(self) -> None:
        # Это изолированная dev-only операция вне продуктовых use-case'ов.
        # Коммитим сразу здесь, чтобы TRUNCATE гарантированно завершился в той же
        # служебной операции и не зависел от общей UoW-оркестрации приложения.
        await self._session.execute(_TRUNCATE_SQL)
        await self._session.commit()
