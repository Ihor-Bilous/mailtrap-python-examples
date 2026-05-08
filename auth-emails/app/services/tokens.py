from functools import lru_cache

from itsdangerous import URLSafeTimedSerializer

from app.config import get_settings

_VERIFICATION_SALT = "email-verification"
_RESET_SALT = "password-reset"


@lru_cache(maxsize=1)
def _get_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_settings().secret_key)


def generate_verification_token(email: str) -> str:
    return _get_serializer().dumps(email, salt=_VERIFICATION_SALT)


def confirm_verification_token(token: str, max_age: int) -> str:
    return _get_serializer().loads(token, salt=_VERIFICATION_SALT, max_age=max_age)


def generate_reset_token(email: str) -> str:
    return _get_serializer().dumps(email, salt=_RESET_SALT)


def confirm_reset_token(token: str, max_age: int) -> str:
    return _get_serializer().loads(token, salt=_RESET_SALT, max_age=max_age)
