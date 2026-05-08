from functools import lru_cache

from app.services.classifier import GeminiClassifier
from app.services.mailer import MailtrapMailer


@lru_cache(maxsize=1)
def get_classifier() -> GeminiClassifier:
    return GeminiClassifier()


@lru_cache(maxsize=1)
def get_mailer() -> MailtrapMailer:
    return MailtrapMailer()
