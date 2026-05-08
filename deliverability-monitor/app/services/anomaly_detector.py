from app.config import Settings
from app.schemas import Anomaly, DeliveryStats


def detect(stats: DeliveryStats, settings: Settings) -> list[Anomaly]:
    anomalies = []

    if stats.sent < settings.min_sample_size:
        return anomalies

    bounce_rate = stats.bounced / stats.sent
    if bounce_rate > settings.bounce_rate_threshold:
        anomalies.append(Anomaly(
            type="high_bounce",
            rate=bounce_rate,
            threshold=settings.bounce_rate_threshold,
            sample_size=stats.sent,
        ))

    complaint_rate = stats.complained / stats.sent
    if complaint_rate > settings.complaint_rate_threshold:
        anomalies.append(Anomaly(
            type="high_complaint",
            rate=complaint_rate,
            threshold=settings.complaint_rate_threshold,
            sample_size=stats.sent,
        ))

    if stats.delivered >= settings.min_sample_size:
        open_rate = stats.opened / stats.delivered
        if open_rate < settings.open_rate_threshold:
            anomalies.append(Anomaly(
                type="low_open_rate",
                rate=open_rate,
                threshold=settings.open_rate_threshold,
                sample_size=stats.delivered,
            ))

    return anomalies
