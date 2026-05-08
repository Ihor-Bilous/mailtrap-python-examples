# Mailtrap Observability — Deliverability Monitor & Webhook Event Processing

A FastAPI application that monitors email deliverability health via two complementary patterns: a scheduled pull job that polls the Mailtrap Stats and Email Logs APIs, and a real-time push endpoint that receives Mailtrap delivery event webhooks. When bounce or complaint rates exceed configurable thresholds, Google Gemini analyzes the anomaly and sends an alert email via the Mailtrap SDK.

## How It Works

```
Pull path (APScheduler)                Push path (Mailtrap webhooks)
───────────────────────                ─────────────────────────────
Every POLL_INTERVAL_MINUTES            Mailtrap sends event batch
        │                                         │
        ▼                                         ▼
GET /api/v1/sending/statistics         POST /webhooks/mailtrap
  (raw httpx)                            │
        │                                ├─ Parse events[] array
        ├─ Parse DeliveryStats            ├─ Store each event in SQLite
        ├─ Anomaly detection              ├─ Derive stats from event counts
        │                                └─ Anomaly detection
        │                                         │
        └──────────────┬──────────────────────────┘
                       │  anomaly found?
                       ▼
           GET /api/v1/sending/messages   ← fetch bounce/complaint log details
             (raw httpx)
                       │
                       ▼
             Gemini: root-cause analysis
                       │
                       ▼
             Mailtrap SDK: send alert email
               (with cooldown — no duplicate alerts)
```

## Features

- **Pull path** — APScheduler polls Mailtrap Stats API on a configurable interval
- **Push path** — webhook endpoint stores real-time Mailtrap delivery events in SQLite
- **Raw httpx API usage** — Stats API and Email Logs API called directly (not via SDK)
- **Anomaly detection** — configurable thresholds for bounce rate, complaint rate, and open rate
- **AI analysis** — Google Gemini produces a root-cause hypothesis and recommended actions
- **Alert cooldown** — prevents duplicate alerts of the same type within a configurable window
- **Graceful degradation** — Gemini or API failures are logged; monitoring never crashes

## Prerequisites

- Python 3.12
- [Mailtrap](https://mailtrap.io) account with a verified sending domain
- [Google AI Studio](https://aistudio.google.com) API key

## Setup

**1. Clone and install**

```bash
git clone https://github.com/Ihor-Bilous/mailtrap-python-examples.git
cd mailtrap-python-examples/deliverability-monitor
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Required | Description |
|---|---|---|
| `MAILTRAP_API_TOKEN` | Yes | Mailtrap API token — used for SDK sending and raw API calls |
| `MAILTRAP_ACCOUNT_ID` | Yes | Numeric Mailtrap account ID (visible in the dashboard URL) |
| `MAIL_FROM` | Yes | Sender email address (verified domain) |
| `MAIL_FROM_NAME` | Yes | Sender display name |
| `ALERT_RECIPIENT_EMAIL` | Yes | Email address that receives anomaly alerts |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Gemini model name (default: `gemini-2.5-flash`) |
| `POLL_INTERVAL_MINUTES` | No | Stats polling interval (default: `15`) |
| `EVENT_RETENTION_HOURS` | No | SQLite event retention window (default: `24`) |
| `BOUNCE_RATE_THRESHOLD` | No | Bounce rate that triggers an alert (default: `0.05`) |
| `COMPLAINT_RATE_THRESHOLD` | No | Complaint rate that triggers an alert (default: `0.001`) |
| `OPEN_RATE_THRESHOLD` | No | Open rate below which an alert fires (default: `0.20`) |
| `MIN_SAMPLE_SIZE` | No | Minimum sent count before detection runs (default: `10`) |
| `ALERT_COOLDOWN_MINUTES` | No | Minimum gap between same-type alerts (default: `60`) |

**3. Run**

```bash
uvicorn main:app --reload
```

The app creates `monitor.db` on first start and begins the pull scheduler automatically.

## Testing Webhooks

### Inspect the payload — Webhook.site

[Webhook.site](https://webhook.site) is Mailtrap's recommended tool for inspecting webhook payloads without any local setup:

1. Open [webhook.site](https://webhook.site) — you get a unique public URL instantly
2. In Mailtrap: **Settings → Webhooks → Create New Webhook**, paste the URL
3. Click **Run Test** — Webhook.site shows the exact JSON payload Mailtrap sends

Use this to verify the payload structure before wiring up your app.

### End-to-end local testing — ngrok

To receive real Mailtrap webhook events on `localhost:8000`:

```bash
# Install (macOS)
brew install ngrok

# Authenticate once (free account at ngrok.com)
ngrok config add-authtoken <your-token>

# Expose your local app
ngrok http 8000
```

ngrok prints a public URL like `https://abc123.ngrok-free.app`. In Mailtrap:
**Settings → Webhooks → Create New Webhook** → set URL to `https://abc123.ngrok-free.app/webhooks/mailtrap`.

> Free-tier ngrok URLs change on every restart — update the Mailtrap webhook URL each session.

## Simulating Anomalies

Send a batch of fake bounce events to trigger anomaly detection immediately (adjust `MIN_SAMPLE_SIZE` to `3` in `.env` for quick testing):

```bash
curl -s -X POST http://localhost:8000/webhooks/mailtrap \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {"event": "delivery",       "email": "ok1@example.com",      "message_id": "m1", "timestamp": '"$(date +%s)"'},
      {"event": "delivery",       "email": "ok2@example.com",      "message_id": "m2", "timestamp": '"$(date +%s)"'},
      {"event": "bounce",         "email": "bad1@example.com",     "message_id": "m3", "timestamp": '"$(date +%s)"'},
      {"event": "bounce",         "email": "bad2@example.com",     "message_id": "m4", "timestamp": '"$(date +%s)"'},
      {"event": "spam_complaint", "email": "angry@example.com",    "message_id": "m5", "timestamp": '"$(date +%s)"'}
    ]
  }'
```

With `MIN_SAMPLE_SIZE=3`, this fires a `high_bounce` anomaly, triggers Gemini analysis, and sends an alert email.

## Project Structure

```
deliverability-monitor/
├── app/
│   ├── app.py                      # FastAPI factory, lifespan (DB init, scheduler start/stop)
│   ├── config.py                   # Pydantic-settings env config
│   ├── database.py                 # SQLAlchemy engine + SessionLocal
│   ├── models.py                   # EmailEvent + SentAlert ORM models
│   ├── schemas.py                  # Pydantic webhook payload + internal dataclasses
│   ├── routers/
│   │   └── webhook_router.py       # POST /webhooks/mailtrap
│   └── services/
│       ├── event_store.py          # SQLite event persistence + count queries
│       ├── stats_client.py         # httpx Stats API + Email Logs API client
│       ├── anomaly_detector.py     # Threshold-based anomaly detection
│       ├── ai_analyzer.py          # GeminiAnalyzer — root-cause analysis
│       ├── alert_mailer.py         # Alert HTML email + Mailtrap SDK send + cooldown
│       └── scheduler.py            # APScheduler pull job
├── main.py
├── requirements.txt
└── .env.example
```

## Key Integration Points

**Raw httpx — Stats API**

```python
with httpx.Client(base_url="https://mailtrap.io", timeout=10) as client:
    response = client.get(
        f"/api/accounts/{account_id}/stats",
        headers={"Api-Token": api_token},
        params={"start_date": yesterday, "end_date": today},
    )
    response.raise_for_status()
    data = response.json()
# response fields: delivery_count, bounce_count, spam_count, open_count
```

**Raw httpx — Email Logs API**

```python
with httpx.Client(base_url="https://mailtrap.io", timeout=10) as client:
    response = client.get(
        f"/api/accounts/{account_id}/emails",
        headers={"Api-Token": api_token},
        params={"status": "bounced", "limit": 20},
    )
```

**Anomaly detection**

```python
bounce_rate = stats.bounced / stats.sent
if bounce_rate > settings.bounce_rate_threshold:
    anomalies.append(Anomaly(type="high_bounce", rate=bounce_rate, ...))
```

**Gemini root-cause analysis**

```python
client = genai.Client(api_key=settings.gemini_api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=genai.types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
)
data = json.loads(response.text)
# {"summary": "...", "root_cause": "...", "recommended_actions": [...]}
```

**Alert email via Mailtrap SDK**

```python
mail = mt.Mail(
    sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
    to=[mt.Address(email=settings.alert_recipient_email)],
    subject=f"[Alert] Email deliverability anomaly: {anomaly.type}",
    html=html_body,
    headers={"X-MT-Category": "deliverability-alert"},
)
mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
```

**Graceful degradation — Gemini unavailable**

```python
except Exception:
    logger.warning("Gemini analysis failed", exc_info=True)
    return AnomalyReport(
        summary="AI analysis unavailable — check logs for details.",
        root_cause="",
        recommended_actions=[],
    )
```

**Alert cooldown**

```python
cutoff = (datetime.utcnow() - timedelta(minutes=settings.alert_cooldown_minutes)).isoformat()
already_sent = session.query(SentAlert).filter(
    SentAlert.anomaly_type == anomaly_type,
    SentAlert.sent_at >= cutoff,
).first()
```
