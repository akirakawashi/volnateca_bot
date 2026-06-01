import secrets


def generate_redemption_code(*, prefix: str = "VLT") -> str:
    """Генерирует короткий код заявки для пункта выдачи."""

    return f"{prefix}-{secrets.token_hex(3).upper()}"


def normalize_redemption_code(value: str) -> str:
    """Нормализует код заявки для точного поиска на стойке выдачи."""

    compact = "".join(value.split()).replace("-", "").upper()
    if compact.startswith("VLT") and len(compact) > 3:
        return f"VLT-{compact[3:]}"
    return compact


__all__ = ["generate_redemption_code", "normalize_redemption_code"]
