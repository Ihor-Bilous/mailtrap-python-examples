from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import EmailEvent
from app.schemas import MailtrapEventItem


def save_event(event: MailtrapEventItem, session: Session) -> None:
    ts = datetime.utcfromtimestamp(event.timestamp).isoformat()
    session.add(EmailEvent(
        event_type=event.event,
        recipient=event.email,
        message_id=event.message_id,
        timestamp=ts,
    ))
    session.commit()


def get_event_counts(window_hours: int, session: Session) -> dict[str, int]:
    cutoff = (datetime.utcnow() - timedelta(hours=window_hours)).isoformat()
    rows = (
        session.query(EmailEvent.event_type, func.count())
        .filter(EmailEvent.timestamp >= cutoff)
        .group_by(EmailEvent.event_type)
        .all()
    )
    return {event_type: count for event_type, count in rows}


def prune_old_events(retention_hours: int, session: Session) -> None:
    cutoff = (datetime.utcnow() - timedelta(hours=retention_hours)).isoformat()
    session.query(EmailEvent).filter(EmailEvent.timestamp < cutoff).delete()
    session.commit()
