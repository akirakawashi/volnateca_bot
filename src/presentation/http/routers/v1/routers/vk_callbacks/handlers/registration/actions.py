"""Строки action-ов из payload-кнопок registration-флоу (MESSAGE_NEW + MESSAGE_ALLOW).

Эти константы фиксируют публичный payload protocol VK-кнопок и должны
соответствовать значениям, отправляемым клавиатурами бота.
"""

BALANCE_ACTION = "balance"
TASKS_ACTION = "tasks"
TASKS_PAGE_ACTION = "tasks_page"
SHOP_ACTION = "shop"
REFERRAL_ACTION = "referral"
CUSTOM_PROMO_START_ACTION = "custom_promo_start"
CUSTOM_PROMO_EXIT_ACTION = "custom_promo_exit"
CONSENT_ACCEPT_ACTION = "consent_accept"
CONSENT_DECLINE_ACTION = "consent_decline"
CONSENT_REF_PAYLOAD_KEY = "consent_ref"
STORE_ROOT_ACTION = "store_root"
STORE_EXIT_ACTION = "store_exit"
STORE_CATALOG_ACTION = "store_catalog"
STORE_PRIZE_ACTION = "store_prize"
STORE_CLAIM_ACTION = "store_claim"
STORE_CLAIM_CONFIRM_ACTION = "store_claim_confirm"
STORE_MY_REDEMPTIONS_ACTION = "store_my_redemptions"
DEFAULT_START_MESSAGES = frozenset(("начать", "start", "/start", "старт"))
