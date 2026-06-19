"""Строки action-ов из payload-кнопок registration-флоу (MESSAGE_NEW + MESSAGE_ALLOW).

Эти константы фиксируют публичный payload protocol VK-кнопок и должны
соответствовать значениям, отправляемым клавиатурами бота.
"""

BALANCE_ACTION = "balance"
TASKS_ACTION = "tasks"
TASKS_PAGE_ACTION = "tasks_page"
SHOP_ACTION = "shop"
REFERRAL_ACTION = "referral"
SUPPORT_ACTION = "support"
BOT_SUPPORT_ACTION = "bot_support"
CUSTOM_PROMO_START_ACTION = "custom_promo_start"
CUSTOM_PROMO_EXIT_ACTION = "custom_promo_exit"
CONSENT_ACCEPT_ACTION = "consent_accept"
CONSENT_DECLINE_ACTION = "consent_decline"
CONSENT_REF_PAYLOAD_KEY = "consent_ref"
DEFAULT_START_MESSAGES = frozenset(("начать", "start", "/start", "старт"))
