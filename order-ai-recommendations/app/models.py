from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    category: Mapped[str]
    price_cents: Mapped[int]
    currency: Mapped[str] = mapped_column(default="usd")


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(primary_key=True)
    processed_at: Mapped[str]  # ISO 8601 UTC
