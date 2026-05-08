# Auth — Password Reset & Email Verification

A FastAPI application demonstrating user registration with email verification and password reset, using Mailtrap for transactional email sending.

## Stack

- **Python 3.12** · **FastAPI** · **SQLAlchemy** (SQLite) · **itsdangerous** · **Mailtrap Python SDK**

## Prerequisites

- Python 3.12+
- A [Mailtrap](https://mailtrap.io) account with a verified sending domain and an API token

## Setup

1. **Clone and enter the project directory**
   ```bash
   git clone https://github.com/Ihor-Bilous/mailtrap-python-examples.git
   cd mailtrap-python-examples/auth-emails
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

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Random secret used to sign tokens and session cookies. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `MAILTRAP_API_TOKEN` | Yes | Mailtrap transactional API token. Find it under **Sending → API Tokens** in your Mailtrap dashboard. |
| `MAIL_FROM` | Yes | Sender email address. Must belong to a domain verified in your Mailtrap account. |
| `MAIL_FROM_NAME` | Yes | Sender display name shown in email clients. |
| `BASE_URL` | Yes | Base URL of the app used to build links in emails (e.g. `http://localhost:8000`). |
| `TOKEN_MAX_AGE_SECONDS` | No | How long verification and reset tokens are valid, in seconds. Defaults to `3600` (1 hour). |

## Flows

### Registration & Email Verification
1. Visit `/register` and create an account.
2. A verification email is sent to the address you provided — open it in the [Mailtrap inbox](https://mailtrap.io).
3. Click the verification link. Your account is now active.
4. Log in at `/login`.

### Password Reset
1. Click **Forgot password?** on the login page or visit `/forgot-password`.
2. Enter your email address. A reset link is sent if the account exists (generic success shown either way).
3. Open the reset email in Mailtrap and click the link.
4. Set a new password. The link expires after `TOKEN_MAX_AGE_SECONDS` seconds.

## Key Integration Points

**Mailtrap SDK — sending transactional email**

HTML is rendered from a local Jinja2 template, then sent via `mt.MailtrapClient`:

```python
html = _render("verify_email.html", {"user_name": user_name, "verification_url": verification_url})
mail = mt.Mail(
    sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
    to=[mt.Address(email=user_email)],
    subject="Verify Your Email Address",
    html=html,
)
mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
```

The same pattern is used for password reset emails (`reset_password.html` template, `reset_url` variable).

## Project Structure

```
auth-emails/
├── app/
│   ├── app.py              # FastAPI factory, lifespan, exception handlers
│   ├── config.py           # Pydantic-settings Settings + get_settings()
│   ├── database.py         # SQLAlchemy engine and session
│   ├── models.py           # User model
│   ├── dependencies.py     # get_db, get_current_user, require_verified_user
│   ├── exceptions.py       # Domain exceptions
│   ├── templates.py        # Shared Jinja2Templates instance
│   ├── controllers/        # HTTP layer: parse form data, call use case, return response
│   ├── routers/            # Route declarations only
│   ├── use_cases/          # Business logic (one file per operation)
│   └── services/           # Stateless utilities: auth, tokens, mail
├── templates/
│   ├── pages/              # Jinja2 page templates
│   └── email/              # HTML email templates
├── main.py                 # Entry point
├── requirements.txt
└── .env.example
```
