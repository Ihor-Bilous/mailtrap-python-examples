from itsdangerous import BadSignature, SignatureExpired
from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import AlreadyVerified, TokenExpired, TokenInvalid
from app.models import User
from app.services.tokens import confirm_verification_token
from app.utils import utcnow


def verify_email(token: str, db: Session) -> User:
    try:
        email = confirm_verification_token(token, max_age=get_settings().token_max_age_seconds)
    except SignatureExpired:
        raise TokenExpired()
    except BadSignature:
        raise TokenInvalid()

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise TokenInvalid()
    if user.email_verified_at is not None:
        raise AlreadyVerified()

    user.email_verified_at = utcnow()
    db.commit()
    db.refresh(user)
    return user
