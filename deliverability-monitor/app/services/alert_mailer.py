import logging
from datetime import datetime, timedelta

import mailtrap as mt
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import SentAlert
from app.schemas import Anomaly, AnomalyReport

logger = logging.getLogger(__name__)


class AlertMailer:
    def send_if_not_cooling_down(
        self, anomaly: Anomaly, report: AnomalyReport, session: Session
    ) -> None:
        if self._is_cooling_down(anomaly.type, session):
            logger.info("Alert for %s suppressed (cooldown active)", anomaly.type)
            return

        settings = get_settings()
        client = mt.MailtrapClient(token=settings.mailtrap_api_token)
        try:
            mail = mt.Mail(
                sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
                to=[mt.Address(email=settings.alert_recipient_email)],
                subject=f"[Alert] Email deliverability anomaly: {anomaly.type}",
                html=_render_html(anomaly, report),
                headers={"X-MT-Category": "deliverability-alert"},
            )
            client.send(mail)
            self._record_alert(anomaly.type, session)
            logger.info("Alert sent for anomaly: %s", anomaly.type)
        except Exception:
            logger.error("Failed to send alert email", exc_info=True)

    def _is_cooling_down(self, anomaly_type: str, session: Session) -> bool:
        settings = get_settings()
        cutoff = (datetime.utcnow() - timedelta(minutes=settings.alert_cooldown_minutes)).isoformat()
        return (
            session.query(SentAlert)
            .filter(SentAlert.anomaly_type == anomaly_type, SentAlert.sent_at >= cutoff)
            .first()
        ) is not None

    def _record_alert(self, anomaly_type: str, session: Session) -> None:
        session.add(SentAlert(anomaly_type=anomaly_type, sent_at=datetime.utcnow().isoformat()))
        session.commit()


def _render_html(anomaly: Anomaly, report: AnomalyReport) -> str:
    root_cause = (
        f"<h3>Root Cause Hypothesis</h3><p>{report.root_cause}</p>"
        if report.root_cause
        else ""
    )

    actions = ""
    if report.recommended_actions:
        items = "".join(f"<li>{a}</li>" for a in report.recommended_actions)
        actions = f"<h3>Recommended Actions</h3><ul>{items}</ul>"

    details = ""
    if anomaly.details:
        rows = "".join(
            f"<tr><td>{e.recipient}</td><td>{e.status}</td><td>{e.bounce_reason or '&mdash;'}</td></tr>"
            for e in anomaly.details[:5]
        )
        details = (
            "<h3>Affected Messages (sample)</h3>"
            "<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse'>"
            "<tr><th>Recipient</th><th>Status</th><th>Bounce Reason</th></tr>"
            f"{rows}</table>"
        )

    return (
        "<html><body style='font-family:Arial,sans-serif;max-width:620px;margin:0 auto;color:#333'>"
        "<h2 style='color:#d32f2f'>Deliverability Anomaly Detected</h2>"
        "<table cellpadding='6' style='border-collapse:collapse'>"
        f"<tr><td><strong>Type</strong></td><td>{anomaly.type}</td></tr>"
        f"<tr><td><strong>Observed rate</strong></td><td>{anomaly.rate:.2%}</td></tr>"
        f"<tr><td><strong>Threshold</strong></td><td>{anomaly.threshold:.2%}</td></tr>"
        f"<tr><td><strong>Sample size</strong></td><td>{anomaly.sample_size:,}</td></tr>"
        "</table>"
        f"<h3>AI Summary</h3><p>{report.summary}</p>"
        f"{root_cause}{actions}{details}"
        "</body></html>"
    )
