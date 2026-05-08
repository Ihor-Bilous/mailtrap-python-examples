import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import ProcessedEvent

logger = logging.getLogger(__name__)

_TTL_HOURS = 24


def is_processed(event_id: str, session: Session) -> bool:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=_TTL_HOURS)).isoformat()
    return (
        session.query(ProcessedEvent)
        .filter(
            ProcessedEvent.event_id == event_id,
            ProcessedEvent.processed_at > cutoff,
        )
        .first()
        is not None
    )


def mark_processed(event_id: str, session: Session) -> None:
    now = datetime.now(timezone.utc).isoformat()
    session.merge(ProcessedEvent(event_id=event_id, processed_at=now))
    session.commit()
    logger.info("Marked Stripe event as processed: %s", event_id)
