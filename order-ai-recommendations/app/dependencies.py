from functools import lru_cache

from app.services.mailer import MailtrapMailer
from app.services.recommender import GeminiRecommender
from app.services.stripe_gateway import StripeGateway


@lru_cache(maxsize=1)
def get_stripe_gateway() -> StripeGateway:
    return StripeGateway()


@lru_cache(maxsize=1)
def get_recommender() -> GeminiRecommender:
    return GeminiRecommender()


@lru_cache(maxsize=1)
def get_mailer() -> MailtrapMailer:
    return MailtrapMailer()
