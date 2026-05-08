# Contact Form — AI Classification & Smart Routing

A FastAPI application that renders a contact form, classifies submissions with Google Gemini, routes notifications to the correct team inbox, and sends an auto-reply to the submitter — all via the Mailtrap Python SDK.

## How It Works

```
Visitor submits contact form
        │
        ▼
POST /contact
        │
        ├─ Validate input (Pydantic)
        ├─ Classify with Gemini → category + urgency
        ├─ Look up team email from routing map
        ├─ Send notification to team email  ─┐ (background tasks,
        └─ Send auto-reply to submitter     ─┘  isolated failures)
                │
                └─ Redirect to /success
```

**Categories:** `sales` · `support` · `partnership` · `spam` · `other`

**Urgency levels:** `high` · `normal` · `low`

Spam submissions are logged but never forwarded — no notification, no auto-reply.

## Features

- Pydantic form validation with inline field errors on the same page
- Google Gemini classifies every submission into a category and urgency level
- Smart routing: each category maps to a dedicated team email via env vars
- Auto-reply confirms receipt to the submitter for every non-spam message
- `X-MT-Category` header on every outgoing email for Mailtrap dashboard analytics
- Graceful degradation: Gemini failure falls back to `other / normal`; notification and auto-reply failures are isolated and logged without crashing

## Prerequisites

- Python 3.12+
- [Mailtrap](https://mailtrap.io) account with a verified sending domain and an API token
- [Google AI Studio](https://aistudio.google.com) API key

## Setup

1. **Clone and enter the project directory**
   ```bash
   git clone https://github.com/Ihor-Bilous/mailtrap-python-examples.git
   cd mailtrap-python-examples/ai-contact-form
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in all required values (see table below).

5. **Run the app**
   ```bash
   uvicorn main:app --reload
   ```
   The app is available at [http://localhost:8000](http://localhost:8000).

## Environment Variables

| Variable | Description |
|---|---|
| `MAILTRAP_API_TOKEN` | Mailtrap transactional API token |
| `MAIL_FROM` | Sender email (must belong to a verified domain) |
| `MAIL_FROM_NAME` | Sender display name |
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Gemini model ID (default: `gemini-2.5-flash`) |
| `ROUTE_SALES_EMAIL` | Team email for `sales` submissions |
| `ROUTE_SUPPORT_EMAIL` | Team email for `support` submissions |
| `ROUTE_PARTNERSHIPS_EMAIL` | Team email for `partnership` submissions |
| `ROUTE_DEFAULT_EMAIL` | Fallback email for `other` and unmatched categories |

## Flows

### Contact Form Submission
1. Visit `/contact` and fill in name, email, subject, and message.
2. On submit, Gemini classifies the message and assigns an urgency level.
3. A notification email is routed to the matching team inbox.
4. The submitter receives an auto-reply confirming receipt.
5. The page redirects to `/success`.

### Spam Handling
If Gemini classifies the message as `spam`, the submission is logged and silently dropped — no notification, no auto-reply, but the submitter still sees the success page.

### Graceful Degradation
- **Gemini unavailable** — classification falls back to `category: other, urgency: normal`; routing and email continue normally.
- **Mail failure** — notification and auto-reply are sent in separate background tasks; one failure does not block the other.

## Project Structure

```
ai-contact-form/
├── app/
│   ├── app.py              # FastAPI factory
│   ├── config.py           # Pydantic-settings config + routing map
│   ├── dependencies.py     # lru_cache singletons for FastAPI Depends
│   ├── protocols.py        # Structural interfaces (ClassifierProtocol, MailerProtocol)
│   ├── schemas.py          # ContactFormSchema (Pydantic)
│   ├── templates.py        # Shared Jinja2Templates instance
│   ├── types.py            # ClassificationResult dataclass
│   ├── routers/
│   │   └── contact_router.py   # GET+POST /contact, GET /success
│   └── services/
│       ├── classifier.py       # GeminiClassifier
│       └── mailer.py           # MailtrapMailer (notification + auto-reply)
├── templates/
│   ├── email/
│   │   ├── notification.html   # Team notification email
│   │   └── auto_reply.html     # Submitter auto-reply email
│   └── pages/
│       ├── base.html
│       ├── contact.html        # Contact form page
│       └── success.html        # Post-submission success page
├── main.py
├── requirements.txt
└── .env.example
```

## Key Integration Points

**Gemini classification with JSON output**

```python
response = self._client.models.generate_content(
    model=self._model,
    contents=_PROMPT_TEMPLATE.format(subject=subject, message=message),
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1,
    ),
)
data = json.loads(response.text)
```

**Smart routing via env-configured map**

```python
team_email = settings.routing_map.get(result.category, settings.route_default_email)
```

**Notification email with `X-MT-Category` header**

```python
mail = mt.Mail(
    sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
    to=[mt.Address(email=team_email)],
    subject=f"[{result.urgency.upper()}] {result.category.capitalize()}: {subject}",
    html=html,
    category=result.category,
)
mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
```

**Graceful degradation on Gemini failure**

```python
except Exception:
    logger.exception("Gemini classification failed for subject: %s", subject)
    return _FALLBACK  # ClassificationResult("other", "normal", "Classification unavailable")
```
