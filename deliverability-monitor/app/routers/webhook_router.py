import logging

from fastapi import APIRouter, Request

from app.config import get_settings
from app.database import SessionLocal
from app.schemas import DeliveryStats, MailtrapWebhookPayload
from app.services import event_store
from app.services.ai_analyzer import GeminiAnalyzer
from app.services.alert_mailer import AlertMailer
from app.services.anomaly_detector import detect

router = APIRouter()
logger = logging.getLogger(__name__)

_analyzer = GeminiAnalyzer()
_mailer = AlertMailer()


@router.post("/webhooks/mailtrap")
async def mailtrap_webhook(request: Request):
    try:
        payload = MailtrapWebhookPayload.model_validate(await request.json())
        settings = get_settings()

        with SessionLocal() as session:
            for item in payload.events:
                event_store.save_event(item, session)

            counts = event_store.get_event_counts(settings.event_retention_hours, session)
            stats = _counts_to_stats(counts)
            anomalies = detect(stats, settings)

            for anomaly in anomalies:
                report = _analyzer.analyze(anomaly)
                _mailer.send_if_not_cooling_down(anomaly, report, session)

    except Exception:
        logger.error("Webhook processing error", exc_info=True)

    return {"status": "ok"}


def _counts_to_stats(counts: dict[str, int]) -> DeliveryStats:
    delivered = counts.get("delivery", 0)
    bounced = counts.get("bounce", 0) + counts.get("soft_bounce", 0)
    complained = counts.get("spam_complaint", 0)
    opened = counts.get("open", 0)
    rejected = counts.get("reject", 0)
    sent = delivered + bounced + complained + rejected
    return DeliveryStats(
        sent=sent,
        delivered=delivered,
        bounced=bounced,
        complained=complained,
        opened=opened,
    )
