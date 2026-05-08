from typing import Any, Protocol

from app.schemas import OrderData, RecommendedProduct
from app.models import Product


class StripeGatewayProtocol(Protocol):
    def construct_event(self, payload: bytes, sig_header: str, secret: str) -> dict: ...
    def get_checkout_session(self, session_id: str) -> Any: ...
    def list_line_items(self, session_id: str) -> Any: ...


class RecommenderProtocol(Protocol):
    def get_recommendations(
        self, purchased_names: list[str], catalog: list[Product]
    ) -> list[RecommendedProduct]: ...


class MailerProtocol(Protocol):
    def send_order_confirmation(
        self, order: OrderData, recommendations: list[RecommendedProduct]
    ) -> None: ...
