import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import Settings, get_settings
from app.database import SessionLocal
from app.schemas import DeliveryStats
from app.services.ai_analyzer import GeminiAnalyzer
from app.services.alert_mailer import AlertMailer
from app.services.anomaly_detector import detect
from app.services.event_store import prune_old_events
from app.services.stats_client import MailtrapStatsClient

logger = logging.getLogger(__name__)

_analyzer = GeminiAnalyzer()
_mailer = AlertMailer()


def run_pull_cycle() -> None:
    settings = get_settings()
    client = MailtrapStatsClient(settings.mailtrap_api_token, settings.mailtrap_account_id)

    stats = client.fetch_stats()
    if stats is None:
        return

    anomalies = detect(stats, settings)
    if not anomalies:
        logger.debug("Pull cycle: no anomalies detected (sent=%d)", stats.sent)
        return

    logs = client.fetch_email_logs(status="bounced")

    with SessionLocal() as session:
        prune_old_events(settings.event_retention_hours, session)
        for anomaly in anomalies:
            anomaly.details = logs
            report = _analyzer.analyze(anomaly)
            _mailer.send_if_not_cooling_down(anomaly, report, session)


def create_scheduler(settings: Settings) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_pull_cycle,
        "interval",
        minutes=settings.poll_interval_minutes,
        id="stats_poll",
    )
    return scheduler
