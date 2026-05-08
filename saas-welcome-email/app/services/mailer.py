import logging

import mailtrap as mt

from app.config import get_settings
from app.types import WelcomeContent

logger = logging.getLogger(__name__)


class MailtrapMailer:
    def send_welcome(self, name: str, email: str, content: WelcomeContent) -> None:
        settings = get_settings()
        try:
            if settings.is_sandbox:
                client = mt.MailtrapClient(
                    token=settings.mailtrap_api_token,
                    sandbox=True,
                    inbox_id=settings.mailtrap_sandbox_inbox_id,
                )
            else:
                client = mt.MailtrapClient(token=settings.mailtrap_api_token)

            mail = mt.MailFromTemplate(
                sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
                to=[mt.Address(email=email)],
                template_uuid=settings.mailtrap_template_uuid,
                template_variables={
                    "user_name": name,
                    "headline": content.headline,
                    "body": content.body,
                    "cta_text": content.cta_text,
                },
                headers={"X-MT-Category": "welcome-email"},
            )
            client.send(mail)
        except Exception:
            logger.exception("Failed to send welcome email to %s", email)
