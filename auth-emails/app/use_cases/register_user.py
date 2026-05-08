from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import EmailAlreadyRegistered
from app.models import User
from app.services.auth import hash_password
from app.services.tokens import generate_verification_token


def register_user(name: str, email: str, password: str, db: Session) -> tuple[User, str]:
    if db.query(User).filter(User.email == email).first():
        raise EmailAlreadyRegistered()

    user = User(name=name, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_verification_token(email)
    verification_url = f"{get_settings().base_url}/verify-email/{token}"
    return user, verification_url
