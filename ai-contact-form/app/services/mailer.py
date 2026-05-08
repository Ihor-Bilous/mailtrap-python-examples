import logging
from pathlib import Path

import mailtrap as mt
from jinja2 import Environment, FileSystemLoader

from app.config import get_settings
from app.types import ClassificationResult

logger = logging.getLogger(__name__)

_email_templates = Environment(
    loader=FileSystemLoader(Path(__file__).parent.parent.parent / "templates" / "email"),
    autoescape=True,
)


def _render(template_name: str, context: dict) -> str:
    return _email_templates.get_template(template_name).render(**context)


class MailtrapMailer:
    def send_notification(
        self,
        name: str,
        email: str,
        subject: str,
        message: str,
        result: ClassificationResult,
        team_email: str,
    ) -> None:
        settings = get_settings()
        try:
            html = _render("notification.html", {
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
                "category": result.category,
                "urgency": result.urgency,
                "reason": result.reason,
            })
            mail = mt.Mail(
                sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
                to=[mt.Address(email=team_email)],
                subject=f"[{result.urgency.upper()}] {result.category.capitalize()}: {subject}",
                html=html,
                category=result.category,
            )
            mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
        except Exception:
            logger.exception("Failed to send notification email to %s", team_email)

    def send_auto_reply(self, name: str, email: str, subject: str) -> None:
        settings = get_settings()
        try:
            html = _render("auto_reply.html", {"name": name, "subject": subject})
            mail = mt.Mail(
                sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
                to=[mt.Address(email=email)],
                subject="We received your message",
                html=html,
                category="auto-reply",
            )
            mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
        except Exception:
            logger.exception("Failed to send auto-reply to %s", email)
