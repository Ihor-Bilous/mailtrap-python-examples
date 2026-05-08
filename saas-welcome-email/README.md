# SaaS — AI-Personalized Welcome Email

A FastAPI application that demonstrates how to send AI-personalized welcome emails via Mailtrap. Google Gemini generates email copy tailored to each user's role, company size, and use case. Mailtrap Sandbox lets you preview the output before switching to production — controlled by a single env variable.

## How it works

1. User fills in a signup form (name, email, role, company size, use case)
2. Google Gemini generates a personalized headline, body, and CTA for the welcome email
3. The email is sent via a Mailtrap template populated with the AI-generated variables
4. In sandbox mode the email lands in your Mailtrap testing inbox; in production it goes to the real recipient

## Prerequisites

- Python 3.12+
- A [Mailtrap](https://mailtrap.io) account with:
  - An API token (Settings → API Tokens)
  - A Sandbox inbox ID (Email Testing → Inboxes → select inbox → Integration → API)
  - A transactional email template (see below)
- A [Google AI Studio](https://aistudio.google.com) API key

## Create the Mailtrap email template

Before running the app, create a template in your Mailtrap account:

1. Go to **Sending** → **Email Templates** → **New Template**
2. Design the template however you like and insert these variables where needed:
   - `{{user_name}}` — the user's name
   - `{{headline}}` — AI-generated welcome headline
   - `{{body}}` — AI-generated body copy
   - `{{cta_text}}` — AI-generated call-to-action button label
3. Save the template and copy its **UUID** from the template detail page

## Installation

```bash
git clone https://github.com/Ihor-Bilous/mailtrap-python-examples.git
cd mailtrap-python-examples/saas-welcome-email
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `MAILTRAP_API_TOKEN` | yes | — | Mailtrap API token |
| `MAILTRAP_TEMPLATE_UUID` | yes | — | UUID of your welcome email template |
| `MAILTRAP_ENV` | no | `sandbox` | `sandbox` or `production` |
| `MAILTRAP_SANDBOX_INBOX_ID` | sandbox only | — | Inbox ID for Mailtrap Sandbox |
| `MAIL_FROM` | yes | — | Sender email address |
| `MAIL_FROM_NAME` | yes | — | Sender display name |
| `GEMINI_API_KEY` | yes | — | Google Gemini API key |
| `GEMINI_MODEL` | no | `gemini-2.0-flash` | Gemini model ID |

## Running

```bash
uvicorn main:app --reload
```

Open [http://localhost:8000/signup](http://localhost:8000/signup).

## Switching to production

Change one line in `.env`:

```
MAILTRAP_ENV=production
```

No code changes needed. Emails will be delivered to real recipients via the Mailtrap transactional API.

## Verifying emails in sandbox

1. Go to **Email Testing** → **Inboxes** in the Mailtrap dashboard
2. Select the inbox matching your `MAILTRAP_SANDBOX_INBOX_ID`
3. Submit the signup form — the personalized welcome email will appear in the inbox within seconds

## Graceful degradation

- **Gemini unavailable** — the app falls back to generic welcome copy and still sends the email
- **Mail delivery failure** — logged; the user still reaches the success page

## Project structure

```
saas-welcome-email/
├── app/
│   ├── app.py               # FastAPI app factory
│   ├── config.py            # Settings (pydantic-settings), sandbox/production flag
│   ├── dependencies.py      # DI singletons: get_personalizer, get_mailer
│   ├── protocols.py         # PersonalizerProtocol, MailerProtocol
│   ├── schemas.py           # SignupFormSchema (Pydantic validation)
│   ├── templates.py         # Jinja2Templates instance
│   ├── types.py             # WelcomeContent dataclass
│   ├── routers/
│   │   └── signup_router.py # GET/POST /signup, GET /success
│   └── services/
│       ├── personalizer.py  # GeminiPersonalizer — generates email copy
│       └── mailer.py        # MailtrapMailer — sends via template API
├── templates/pages/         # Jinja2 HTML page templates
├── main.py
├── requirements.txt
└── .env.example
```
