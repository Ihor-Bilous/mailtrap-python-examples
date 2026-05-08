from functools import lru_cache

from app.services.mailer import MailtrapMailer
from app.services.personalizer import GeminiPersonalizer


@lru_cache(maxsize=1)
def get_personalizer() -> GeminiPersonalizer:
    return GeminiPersonalizer()


@lru_cache(maxsize=1)
def get_mailer() -> MailtrapMailer:
    return MailtrapMailer()
