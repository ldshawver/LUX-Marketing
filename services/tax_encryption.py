"""Encryption utilities for tax forms and TIN/EIN storage."""
import base64
import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


def _load_cipher() -> Fernet:
    key = os.environ.get("DATA_ENCRYPTION_KEY")
    if not key:
        raise ValueError("DATA_ENCRYPTION_KEY is required for tax encryption")
    try:
        return Fernet(key.encode())
    except Exception as exc:
        logger.error("Failed to load DATA_ENCRYPTION_KEY: %s", exc)
        raise


def encrypt_value(value: str) -> str:
    if not value:
        return ""
    cipher = _load_cipher()
    encrypted = cipher.encrypt(value.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_value(value: str) -> str:
    if not value:
        return ""
    cipher = _load_cipher()
    decrypted = cipher.decrypt(base64.b64decode(value.encode()))
    return decrypted.decode()


def mask_tin(value: str) -> str:
    if not value:
        return ""
    digits = "".join([c for c in value if c.isdigit()])
    if len(digits) < 4:
        return "****"
    return f"***-**-{digits[-4:]}"
