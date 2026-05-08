from dataclasses import dataclass, field

from pydantic import BaseModel


class MailtrapEventItem(BaseModel):
    event: str
    email: str
    message_id: str
    timestamp: int  # Unix epoch


class MailtrapWebhookPayload(BaseModel):
    events: list[MailtrapEventItem]


@dataclass
class DeliveryStats:
    sent: int
    delivered: int
    bounced: int
    complained: int
    opened: int


@dataclass
class EmailLogEntry:
    message_id: str
    recipient: str
    status: str
    sent_at: str
    bounce_reason: str | None = None


@dataclass
class Anomaly:
    type: str  # "high_bounce" | "high_complaint" | "low_open_rate"
    rate: float
    threshold: float
    sample_size: int
    details: list[EmailLogEntry] = field(default_factory=list)


@dataclass
class AnomalyReport:
    summary: str
    root_cause: str
    recommended_actions: list[str]
