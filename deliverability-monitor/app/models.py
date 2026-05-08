from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EmailEvent(Base):
    __tablename__ = "email_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str]
    recipient: Mapped[str]
    message_id: Mapped[str]
    timestamp: Mapped[str]  # ISO 8601 UTC


class SentAlert(Base):
    __tablename__ = "sent_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    anomaly_type: Mapped[str]
    sent_at: Mapped[str]  # ISO 8601 UTC
