from datetime import datetime, timezone

from pydantic import ValidationError


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def field_errors(exc: ValidationError) -> dict[str, str]:
    return {str(err["loc"][0]): err["msg"] for err in exc.errors() if err["loc"]}
