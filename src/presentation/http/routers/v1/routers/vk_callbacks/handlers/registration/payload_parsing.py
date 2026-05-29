"""Хелперы для разбора payload-ов кнопок и текстовых сообщений registration-флоу."""

from application.common.dto.store import StoreSection
from presentation.http.routers.v1.routers.vk_callbacks.handlers.registration.actions import (
    CONSENT_REF_PAYLOAD_KEY,
    DEFAULT_START_MESSAGES,
)
from presentation.http.routers.v1.routers.vk_callbacks.protocol.payload import VKCallbackPayload


def parse_tasks_page(raw_page: object) -> int:
    page = parse_positive_int(raw_page)
    return page if page is not None else 1


def parse_store_section(raw_section: object) -> StoreSection:
    if isinstance(raw_section, str):
        try:
            return StoreSection(raw_section)
        except ValueError:
            return StoreSection.ALL
    return StoreSection.ALL


def parse_store_page(raw_page: object) -> int:
    page = parse_positive_int(raw_page)
    return page if page is not None else 1


def parse_payload_str(raw_value: object) -> str | None:
    if isinstance(raw_value, str):
        stripped = raw_value.strip()
        return stripped if stripped else None
    return None


def parse_positive_int(raw_value: object) -> int | None:
    if isinstance(raw_value, bool):
        return None
    if isinstance(raw_value, int) and raw_value > 0:
        return raw_value
    if isinstance(raw_value, str) and raw_value.isdecimal():
        parsed = int(raw_value)
        return parsed if parsed > 0 else None
    return None


def extract_consent_ref_key(
    *,
    button_payload: dict[str, object] | None,
    data: VKCallbackPayload,
) -> str | None:
    if button_payload is not None:
        raw_ref = button_payload.get(CONSENT_REF_PAYLOAD_KEY)
        if isinstance(raw_ref, str) and raw_ref.strip():
            return raw_ref.strip()
    return data.get_ref_key()


def is_default_start_message(data: VKCallbackPayload) -> bool:
    if not data.is_message_new():
        return False
    return data.get_message_text().strip().casefold() in DEFAULT_START_MESSAGES
