from functools import lru_cache

from fastapi import Request, Response
from itsdangerous import BadSignature, URLSafeSerializer
from passlib.context import CryptContext

from app.config import get_settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


@lru_cache(maxsize=1)
def _get_session_serializer() -> URLSafeSerializer:
    return URLSafeSerializer(get_settings().secret_key, salt="session")


def set_session_cookie(response: Response, user_id: int) -> None:
    token = _get_session_serializer().dumps(user_id)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key="session")


def read_session_cookie(request: Request) -> int | None:
    value = request.cookies.get("session")
    if value is None:
        return None
    try:
        return _get_session_serializer().loads(value)
    except BadSignature:
        return None
