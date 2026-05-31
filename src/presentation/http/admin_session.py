import base64
import binascii
import hashlib
import hmac
import json
import time


def _base64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_admin_session_cookie_value(*, secret: str, ttl_seconds: int) -> str:
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + ttl_seconds,
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded_payload = _base64url_encode(payload_bytes)
    signature = hmac.new(secret.encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded_payload}.{_base64url_encode(signature)}"


def verify_admin_session_cookie_value(*, cookie_value: str, secret: str) -> bool:
    try:
        encoded_payload, encoded_signature = cookie_value.split(".", 1)
        expected_signature = hmac.new(
            secret.encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        signature = _base64url_decode(encoded_signature)
        if not hmac.compare_digest(signature, expected_signature):
            return False

        payload = json.loads(_base64url_decode(encoded_payload))
    except (ValueError, json.JSONDecodeError, binascii.Error):
        return False

    if not isinstance(payload, dict):
        return False

    exp = payload.get("exp")
    if not isinstance(exp, int):
        return False

    return exp > int(time.time())


__all__ = [
    "create_admin_session_cookie_value",
    "verify_admin_session_cookie_value",
]
