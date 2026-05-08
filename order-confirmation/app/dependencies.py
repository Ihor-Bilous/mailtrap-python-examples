from functools import lru_cache

from app.services.mailer import MailtrapMailer
from app.services.stripe_gateway import StripeGateway


@lru_cache(maxsize=1)
def get_mailer() -> MailtrapMailer:
    return MailtrapMailer()


@lru_cache(maxsize=1)
def get_stripe_gateway() -> StripeGateway:
    return StripeGateway()
