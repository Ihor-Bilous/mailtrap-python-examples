import dataclasses
import logging

import mailtrap as mt

from app.config import get_settings
from app.schemas import OrderData

logger = logging.getLogger(__name__)


class MailtrapMailer:
    def send_order_confirmation(self, order: OrderData) -> None:
        settings = get_settings()

        if not settings.mailtrap_template_uuid:
            logger.warning(
                "MAILTRAP_TEMPLATE_UUID not configured — skipping confirmation for order %s",
                order.order_id,
            )
            return

        shipping = (
            dataclasses.asdict(order.shipping_address) if order.shipping_address else None
        )
        mail = mt.MailFromTemplate(
            sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
            to=[mt.Address(email=order.customer_email)],
            template_uuid=settings.mailtrap_template_uuid,
            template_variables={
                "order_id": order.order_id,
                "items": [
                    {"name": item.name, "quantity": item.quantity, "price": item.price}
                    for item in order.items
                ],
                "total": order.total,
                "shipping_address": shipping,
            },
        )

        mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
        logger.info(
            "Order confirmation sent for %s to %s", order.order_id, order.customer_email
        )
