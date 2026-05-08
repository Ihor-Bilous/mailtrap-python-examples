from sqlalchemy.orm import Session

from app.exceptions import InvalidCredentials
from app.models import User
from app.services.auth import verify_password


def login_user(email: str, password: str, db: Session) -> int:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentials()
    return user.id
