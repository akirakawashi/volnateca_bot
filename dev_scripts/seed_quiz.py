"""
TODO DEV: удалить dev_scripts/ перед релизом — только для локальной отладки.

Скрипт для вставки тестовых данных викторины в БД.

Запуск из корня проекта:
    PYTHONPATH=src poetry run python scripts/seed_quiz.py
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Чтобы работали импорты из src/ без установки пакета
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.enums.task import TaskRepeatPolicy, TaskType
from infrastructure.database.models.quiz_question_options import QuizQuestionOption
from infrastructure.database.models.quiz_questions import QuizQuestion
from infrastructure.database.models.tasks import Task
from settings.db.db import DBSettings

# ---------------------------------------------------------------------------
# Тестовые данные
# ---------------------------------------------------------------------------

QUIZ_TASKS = [
    {
        "code": "quiz_history_2016",
        "task_name": "Викторина: история Волны — 2016",
        "description": "Ответь на вопросы об истории мобильного оператора «Волна» (2016 год).",
        "task_type": TaskType.QUIZ,
        "points": 15,
        "week_number": None,
        "repeat_policy": TaskRepeatPolicy.ONCE,
        "starts_at": datetime(2026, 5, 11, tzinfo=timezone.utc),  # сегодня — активно
        "ends_at":   datetime(2026, 5, 18, tzinfo=timezone.utc),
        "is_active": True,
    },
    {
        "code": "quiz_history_2017",
        "task_name": "Викторина: история Волны — 2017",
        "description": "Ответь на вопросы об истории мобильного оператора «Волна» (2017 год).",
        "task_type": TaskType.QUIZ,
        "points": 15,
        "week_number": None,
        "repeat_policy": TaskRepeatPolicy.ONCE,
        "starts_at": datetime(2026, 5, 18, tzinfo=timezone.utc),  # ещё не началась
        "ends_at":   datetime(2026, 5, 25, tzinfo=timezone.utc),
        "is_active": True,
    },
]

# Вопросы для каждого задания: code задания → список вопросов
QUESTIONS_BY_TASK: dict[str, list[dict]] = {
    "quiz_history_2016": [
        {
            "question_text": "В каком году был основан мобильный оператор «Волна»?",
            "options": [
                {"option_text": "2014", "is_correct": False, "sort_order": 1},
                {"option_text": "2016", "is_correct": True,  "sort_order": 2},
                {"option_text": "2018", "is_correct": False, "sort_order": 3},
                {"option_text": "2020", "is_correct": False, "sort_order": 4},
            ],
        },
        {
            "question_text": "Как называется внутренняя валюта юбилейного проекта?",
            "options": [
                {"option_text": "Баллы",     "is_correct": False, "sort_order": 1},
                {"option_text": "Дискошары", "is_correct": True,  "sort_order": 2},
                {"option_text": "Звёзды",    "is_correct": False, "sort_order": 3},
                {"option_text": "Волны",     "is_correct": False, "sort_order": 4},
            ],
        },
        {
            "question_text": "Сколько недель длится юбилейный проект «Волнатека»?",
            "options": [
                {"option_text": "8",  "is_correct": False, "sort_order": 1},
                {"option_text": "10", "is_correct": False, "sort_order": 2},
                {"option_text": "12", "is_correct": True,  "sort_order": 3},
                {"option_text": "16", "is_correct": False, "sort_order": 4},
            ],
        },
    ],
    "quiz_history_2017": [
        {
            "question_text": "Сколько дискошаров начисляется за репост поста недели?",
            "options": [
                {"option_text": "10 ✦", "is_correct": False, "sort_order": 1},
                {"option_text": "15 ✦", "is_correct": False, "sort_order": 2},
                {"option_text": "20 ✦", "is_correct": True,  "sort_order": 3},
                {"option_text": "30 ✦", "is_correct": False, "sort_order": 4},
            ],
        },
        {
            "question_text": "Какой уровень открывает доступ к суперпризам?",
            "options": [
                {"option_text": "Новая волна", "is_correct": False, "sort_order": 1},
                {"option_text": "Прибой",      "is_correct": False, "sort_order": 2},
                {"option_text": "Шторм",       "is_correct": True,  "sort_order": 3},
                {"option_text": "Цунами",      "is_correct": False, "sort_order": 4},
            ],
        },
    ],
}


# ---------------------------------------------------------------------------
# Логика вставки
# ---------------------------------------------------------------------------

async def seed(session: AsyncSession) -> None:
    # Чистим старые тестовые данные в правильном порядке (FK: options → questions → tasks)
    codes = [t["code"] for t in QUIZ_TASKS]
    placeholders = ", ".join(f":code_{i}" for i in range(len(codes)))
    params = {f"code_{i}": code for i, code in enumerate(codes)}

    await session.execute(
        text(
            f"DELETE FROM quiz_question_options WHERE quiz_questions_id IN ("
            f"  SELECT qq.quiz_questions_id FROM quiz_questions qq"
            f"  JOIN tasks t ON t.tasks_id = qq.tasks_id"
            f"  WHERE t.code IN ({placeholders})"
            f")"
        ),
        params,
    )
    await session.execute(
        text(
            f"DELETE FROM quiz_questions WHERE tasks_id IN ("
            f"  SELECT tasks_id FROM tasks WHERE code IN ({placeholders})"
            f")"
        ),
        params,
    )
    await session.execute(
        text(f"DELETE FROM tasks WHERE code IN ({placeholders})"),
        params,
    )
    print("Старые данные удалены.\n")

    for task_data in QUIZ_TASKS:
        task = Task(**task_data)
        session.add(task)
        await session.flush()

        starts_at = task_data["starts_at"]
        if not isinstance(starts_at, datetime):
            raise TypeError("starts_at должен быть datetime")
        status = "🟢 активно" if starts_at.date().isoformat() <= "2026-05-11" else "🔴 не началось"
        print(f"Задание: tasks_id={task.tasks_id}, code={task.code!r}  {status}")

        for q_data in QUESTIONS_BY_TASK[task.code]:
            question = QuizQuestion(
                tasks_id=task.tasks_id,
                question_text=q_data["question_text"],
            )
            session.add(question)
            await session.flush()

            print(f"  Вопрос: {question.quiz_questions_id} — {question.question_text!r}")

            for opt in q_data["options"]:
                option = QuizQuestionOption(
                    quiz_questions_id=question.quiz_questions_id,
                    **opt,
                )
                session.add(option)
                marker = "✓" if opt["is_correct"] else " "
                print(f"    [{marker}] {opt['option_text']!r}")

    await session.commit()
    print("\nГотово. Данные зафиксированы.")


async def main() -> None:
    db = DBSettings()
    engine = create_async_engine(db.dsn(), echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
