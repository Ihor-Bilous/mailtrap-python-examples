from typing import Optional

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User
from app.services.tokens import generate_reset_token


def request_password_reset(email: str, db: Session) -> Optional[tuple[str, str, str]]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    token = generate_reset_token(email)
    reset_url = f"{get_settings().base_url}/reset-password/{token}"
    return user.name, user.email, reset_url
