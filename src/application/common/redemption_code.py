import secrets


def generate_redemption_code(*, prefix: str = "VLT") -> str:
    """Генерирует короткий код заявки для пункта выдачи."""

    return f"{prefix}-{secrets.token_hex(3).upper()}"


__all__ = ["generate_redemption_code"]
