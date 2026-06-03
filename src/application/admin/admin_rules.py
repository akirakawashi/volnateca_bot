from domain.enums.prize import PrizeReceiveType, PrizeType


# Типы призов, которые админка разрешает создавать через форму магазина.
ADMIN_ALLOWED_PRIZE_TYPES = (
    PrizeType.MERCH,
    PrizeType.PARTNER,
    PrizeType.SUPER_PRIZE,
)

# Способы получения, доступные при создании приза из админки.
ADMIN_ALLOWED_RECEIVE_TYPES = (PrizeReceiveType.PICKUP,)

# Сколько пользователей рассылка забирает из БД за одну пачку.
ADMIN_BROADCAST_BATCH_SIZE = 500

# Сколько VK-сообщений рассылка отправляет параллельно.
ADMIN_BROADCAST_SEND_CONCURRENCY = 10

# Диапазон графиков по умолчанию, если админка не передала даты.
ADMIN_DAILY_STATS_DEFAULT_RANGE_DAYS = 30

# Максимальный диапазон графиков, который можно запросить из админки.
ADMIN_DAILY_STATS_MAX_RANGE_DAYS = 90

# Размер страницы заявок на выдачу призов в админке.
ADMIN_REDEMPTIONS_PAGE_SIZE = 50

# Размер страницы списков в карточке пользователя: заявки, задания, транзакции.
ADMIN_USER_LIST_PAGE_SIZE = 50

# Максимальная страница для offset-пагинации в админке.
ADMIN_MAX_PAGE = 1000

# Максимум результатов поиска пользователей в админке.
ADMIN_USER_SEARCH_LIMIT = 20


__all__ = [
    "ADMIN_ALLOWED_PRIZE_TYPES",
    "ADMIN_ALLOWED_RECEIVE_TYPES",
    "ADMIN_BROADCAST_BATCH_SIZE",
    "ADMIN_BROADCAST_SEND_CONCURRENCY",
    "ADMIN_DAILY_STATS_DEFAULT_RANGE_DAYS",
    "ADMIN_DAILY_STATS_MAX_RANGE_DAYS",
    "ADMIN_MAX_PAGE",
    "ADMIN_REDEMPTIONS_PAGE_SIZE",
    "ADMIN_USER_LIST_PAGE_SIZE",
    "ADMIN_USER_SEARCH_LIMIT",
]
