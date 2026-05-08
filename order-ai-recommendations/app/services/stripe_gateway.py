import stripe
import stripe.checkout


class WebhookVerificationError(Exception):
    pass


class StripeGateway:
    def construct_event(self, payload: bytes, sig_header: str, secret: str) -> dict:
        try:
            return stripe.Webhook.construct_event(payload, sig_header, secret)
        except (stripe.errors.SignatureVerificationError, ValueError) as e:
            raise WebhookVerificationError(str(e)) from e

    def get_checkout_session(self, session_id: str) -> stripe.checkout.Session:
        return stripe.checkout.Session.retrieve(session_id)

    def list_line_items(self, session_id: str) -> stripe.ListObject:
        return stripe.checkout.Session.list_line_items(session_id)
