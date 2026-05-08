import logging
from pathlib import Path

import mailtrap as mt
from jinja2 import Environment, FileSystemLoader

from app.config import get_settings

logger = logging.getLogger(__name__)

_email_templates = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent.parent / "templates" / "email"),
    autoescape=True,
)


def _render(template_name: str, context: dict) -> str:
    return _email_templates.get_template(template_name).render(**context)


class MailtrapMailer:
    def send_verification_email(self, user_name: str, user_email: str, verification_url: str) -> None:
        settings = get_settings()
        try:
            html = _render("verify_email.html", {"user_name": user_name, "verification_url": verification_url})
            mail = mt.Mail(
                sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
                to=[mt.Address(email=user_email)],
                subject="Verify Your Email Address",
                html=html,
            )
            mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
        except Exception:
            logger.exception("Failed to send verification email to %s", user_email)

    def send_reset_email(self, user_name: str, user_email: str, reset_url: str) -> None:
        settings = get_settings()
        try:
            html = _render("reset_password.html", {"user_name": user_name, "reset_url": reset_url})
            mail = mt.Mail(
                sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
                to=[mt.Address(email=user_email)],
                subject="Reset Your Password",
                html=html,
            )
            mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
        except Exception:
            logger.exception("Failed to send reset email to %s", user_email)
