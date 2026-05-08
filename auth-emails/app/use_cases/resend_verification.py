from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import AlreadyVerified, UserNotFound
from app.models import User
from app.services.tokens import generate_verification_token


def resend_verification(email: str, db: Session) -> tuple[str, str, str]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise UserNotFound()
    if user.email_verified_at is not None:
        raise AlreadyVerified()

    token = generate_verification_token(email)
    verification_url = f"{get_settings().base_url}/verify-email/{token}"
    return user.name, user.email, verification_url
