# Volnateca — VK Gamification Backend

Backend платформы геймификации во ВКонтакте. Пользователи выполняют задания,
получают баллы и достижения, приглашают друзей и обменивают баллы на призы.
Сервис обрабатывает события VK Callback API и предоставляет API для
[административной панели](https://github.com/akirakawashi/volnateca_admin).

## Возможности

- Регистрация участников и реферальные приглашения.
- Задания на подписки, реакции, комментарии, опросы и промокоды.
- Викторины, баллы, уровни и достижения.
- Каталог призов, заявки на получение, выдача и отмена наград.
- Журнал начислений и списаний.
- Администрирование пользователей, заданий, призов, сообщений и рассылок.

## Стек

Python, FastAPI, SQLAlchemy / SQLModel, PostgreSQL, Alembic,
Dishka, Pydantic Settings, aiohttp, Docker Compose, Poetry.

## Структура

| Путь | Ответственность |
| --- | --- |
| [src/presentation/http/](src/presentation/http/) | Callback, административный API, DTO и обработка ошибок |
| [src/application/](src/application/) | Команды, сервисы, сценарии и интерфейсы |
| [src/domain/](src/domain/) | Предметные модели и правила |
| [src/infrastructure/](src/infrastructure/) | Репозитории, Unit of Work и клиент VK |
| [src/di/](src/di/) | Сборка зависимостей |
| [src/settings/](src/settings/) | Конфигурация приложения |
| [migrations/](migrations/) | Миграции Alembic |

## Подготовка окружения

Требования и зависимости указаны в [pyproject.toml](pyproject.toml).
Для контейнерного запуска используются [Dockerfile](Dockerfile) и
[docker-compose.yml](docker-compose.yml); применение миграций и запуск API
описаны в [entrypoint.sh](entrypoint.sh).

## Связанные проекты

[Volnateca Admin](https://github.com/akirakawashi/volnateca_admin) ·
[Профиль автора](https://github.com/akirakawashi)
