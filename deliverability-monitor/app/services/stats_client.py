import logging
from datetime import date, timedelta

import httpx

from app.schemas import DeliveryStats, EmailLogEntry

logger = logging.getLogger(__name__)

_BASE_URL = "https://mailtrap.io"


class MailtrapStatsClient:
    def __init__(self, api_token: str, account_id: str) -> None:
        self._headers = {"Api-Token": api_token}
        self._account_id = account_id

    def fetch_stats(self) -> DeliveryStats | None:
        today = date.today()
        yesterday = today - timedelta(days=1)
        try:
            with httpx.Client(base_url=_BASE_URL, timeout=10) as client:
                response = client.get(
                    f"/api/accounts/{self._account_id}/stats",
                    headers=self._headers,
                    params={
                        "start_date": yesterday.isoformat(),
                        "end_date": today.isoformat(),
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            delivered = data.get("delivery_count", 0)
            bounced = data.get("bounce_count", 0)
            complained = data.get("spam_count", 0)
            return DeliveryStats(
                sent=delivered + bounced + complained,
                delivered=delivered,
                bounced=bounced,
                complained=complained,
                opened=data.get("open_count", 0),
            )
        except Exception:
            logger.warning("Mailtrap Stats API unavailable", exc_info=True)
            return None

    def fetch_email_logs(self, status: str) -> list[EmailLogEntry]:
        # API status values: delivered | not_delivered | enqueued | opted_out
        filter_status = "not_delivered" if status == "bounced" else status
        try:
            with httpx.Client(base_url=_BASE_URL, timeout=10) as client:
                response = client.get(
                    f"/api/accounts/{self._account_id}/email_logs",
                    headers=self._headers,
                    params={"filters[status][value]": filter_status},
                )
                response.raise_for_status()
                messages = response.json().get("messages", [])
            return [
                EmailLogEntry(
                    message_id=item.get("message_id", ""),
                    recipient=item.get("to", ""),
                    status=item.get("status", ""),
                    sent_at=item.get("sent_at", ""),
                    bounce_reason=None,
                )
                for item in messages
            ]
        except Exception:
            logger.warning("Mailtrap Email Logs API unavailable", exc_info=True)
            return []
