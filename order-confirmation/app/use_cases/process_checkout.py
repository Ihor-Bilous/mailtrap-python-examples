import logging

from app.config import get_settings
from app.protocols import MailerProtocol, StripeGatewayProtocol
from app.schemas import OrderData, OrderItem, ShippingAddress

logger = logging.getLogger(__name__)

_ZERO_DECIMAL_CURRENCIES = frozenset({
    "bif", "clp", "djf", "gnf", "jpy", "kmf", "krw",
    "mga", "pyg", "rwf", "ugx", "vnd", "vuv", "xaf", "xof", "xpf",
})


def _format_amount(amount: int, currency: str) -> str:
    upper = currency.upper()
    if currency.lower() in _ZERO_DECIMAL_CURRENCIES:
        return f"{upper} {amount:,}"
    return f"{upper} {amount / 100:.2f}"


def process_checkout(
    session_id: str,
    stripe_gateway: StripeGatewayProtocol,
    mailer: MailerProtocol,
) -> None:
    settings = get_settings()

    session = stripe_gateway.get_checkout_session(session_id)
    line_items = stripe_gateway.list_line_items(session_id)

    customer_details = getattr(session, "customer_details", None)
    customer_email = (
        (customer_details and getattr(customer_details, "email", None))
        or settings.order_recipient_email
        or None
    )

    if not customer_email:
        logger.warning(
            "No customer email for session %s and ORDER_RECIPIENT_EMAIL not set — skipping send",
            session_id,
        )
        return

    items = [
        OrderItem(
            name=item.description or "",
            quantity=item.quantity or 1,
            price=_format_amount(item.amount_total, item.currency),
        )
        for item in line_items.data
    ]

    shipping_address = None
    shipping_details = getattr(session, "shipping_details", None)
    if shipping_details and getattr(shipping_details, "address", None):
        addr = shipping_details.address
        shipping_address = ShippingAddress(
            name=getattr(shipping_details, "name", "") or "",
            line1=getattr(addr, "line1", "") or "",
            line2=getattr(addr, "line2", "") or "",
            city=getattr(addr, "city", "") or "",
            state=getattr(addr, "state", "") or "",
            postal_code=getattr(addr, "postal_code", "") or "",
            country=getattr(addr, "country", "") or "",
        )

    order = OrderData(
        order_id=session.id,
        customer_email=customer_email,
        items=items,
        total=_format_amount(session.amount_total, session.currency),
        shipping_address=shipping_address,
    )

    logger.info(
        "Processing order %s for %s (%d items)",
        order.order_id,
        order.customer_email,
        len(items),
    )

    mailer.send_order_confirmation(order)
