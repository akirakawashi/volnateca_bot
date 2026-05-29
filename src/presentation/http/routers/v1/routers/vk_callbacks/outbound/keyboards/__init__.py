from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards._buttons import (
    VKKeyboard,
    VKTemplate,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.quiz import (
    build_quiz_offer_keyboard,
    build_quiz_question_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.registration import (
    build_consent_keyboard,
    build_main_menu_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.store import (
    build_store_catalog_carousel_template,
    build_store_catalog_keyboard,
    build_store_catalog_navigation_keyboard,
    build_store_exit_keyboard,
    build_store_prize_card_keyboard,
    build_store_prize_not_found_keyboard,
    build_store_root_keyboard,
)
from presentation.http.routers.v1.routers.vk_callbacks.outbound.keyboards.tasks import (
    build_task_info_keyboard,
    build_task_promo_code_wait_keyboard,
    build_tasks_carousel_template,
    build_tasks_navigation_keyboard,
)

__all__ = [
    "VKKeyboard",
    "VKTemplate",
    "build_consent_keyboard",
    "build_main_menu_keyboard",
    "build_quiz_offer_keyboard",
    "build_quiz_question_keyboard",
    "build_store_catalog_carousel_template",
    "build_store_catalog_keyboard",
    "build_store_catalog_navigation_keyboard",
    "build_store_exit_keyboard",
    "build_store_prize_card_keyboard",
    "build_store_prize_not_found_keyboard",
    "build_store_root_keyboard",
    "build_task_info_keyboard",
    "build_task_promo_code_wait_keyboard",
    "build_tasks_carousel_template",
    "build_tasks_navigation_keyboard",
]
