from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import TokenExpired, TokenInvalid
from app.models import User
from app.services.auth import hash_password
from app.services.tokens import confirm_reset_token


def reset_password(token: str, new_password: str, db: Session) -> None:
    try:
        email = confirm_reset_token(token, max_age=get_settings().token_max_age_seconds)
    except SignatureExpired:
        raise TokenExpired()
    except BadSignature:
        raise TokenInvalid()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise TokenInvalid()

    user.hashed_password = hash_password(new_password)
    db.commit()
