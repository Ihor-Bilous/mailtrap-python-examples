from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.exceptions import NotAuthenticated, NotVerified
from app.models import User
from app.protocols import MailerProtocol
from app.services.auth import read_session_cookie
from app.services.mail import MailtrapMailer


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = read_session_cookie(request)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_verified_user(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise NotAuthenticated()
    if user.email_verified_at is None:
        raise NotVerified()
    return user


@lru_cache(maxsize=1)
def get_mailer() -> MailtrapMailer:
    return MailtrapMailer()


MailerDep = Annotated[MailerProtocol, Depends(get_mailer)]
