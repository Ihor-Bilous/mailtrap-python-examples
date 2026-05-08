# E-commerce — Order Email with AI Recommendations

A FastAPI application that receives Stripe `checkout.session.completed` webhooks and sends order confirmation emails with AI-generated product recommendations.

## How It Works

```
Stripe checkout completes
        │
        ▼
POST /stripe/webhook
        │
        ├─ Verify signature
        ├─ Check event store (dedup)
        ├─ Fetch session + line items from Stripe
        ├─ Resolve customer email
        ├─ Load product catalog from SQLite
        ├─ Ask Gemini for 3 complementary products
        └─ Send email via Mailtrap template API
                │
                └─ order details + "You might also like" section
```

## Features

- Stripe webhook signature verification
- Idempotent event handling — duplicate webhooks are safely ignored
- SQLAlchemy product catalog seeded with 16 products across 3 categories
- AI-powered recommendations: Google Gemini selects 3 complementary products from the catalog
- Graceful degradation: email is sent without recommendations if Gemini is unavailable
- `X-MT-Category: order-confirmation` header on every email for Mailtrap dashboard analytics
- Returns `500` on mail/Stripe failure so Stripe retries; never loses an order

## Prerequisites

- Python 3.12
- [Mailtrap](https://mailtrap.io) account with a transactional email template
- [Stripe](https://stripe.com) account + [Stripe CLI](https://stripe.com/docs/stripe-cli)
- [Google AI Studio](https://aistudio.google.com) API key

## Setup

**1. Clone and install**

```bash
git clone https://github.com/Ihor-Bilous/mailtrap-python-examples.git
cd mailtrap-python-examples/order-ai-recommendations
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

| Variable | Description |
|---|---|
| `MAILTRAP_API_TOKEN` | Mailtrap transactional API token |
| `MAILTRAP_TEMPLATE_UUID` | UUID of your order confirmation template |
| `MAIL_FROM` | Sender email (verified domain) |
| `MAIL_FROM_NAME` | Sender display name |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret (`whsec_...`) |
| `GEMINI_API_KEY` | Google Gemini API key |
| `ORDER_RECIPIENT_EMAIL` | Fallback email when session has no customer email |

**3. Run**

```bash
uvicorn main:app --reload
```

The app creates `store.db` on first start and seeds the product catalog automatically.

## Stripe Test Mode Setup

**1. Create a test product and price**

In the [Stripe Dashboard](https://dashboard.stripe.com/test/products), create a product with a one-time price.

**2. Install Stripe CLI**

```bash
brew install stripe/stripe-cli/stripe
stripe login
```

**3. Forward webhooks to your local server**

```bash
stripe listen --forward-to localhost:8000/stripe/webhook
```

Copy the `whsec_...` signing secret printed by the CLI and add it to `.env` as `STRIPE_WEBHOOK_SECRET`.

**4. Trigger a test event**

```bash
stripe trigger checkout.session.completed
```

**5. End-to-end test**

Create a [Payment Link](https://dashboard.stripe.com/test/payment-links) in Stripe Dashboard using your test product. Complete checkout with card `4242 4242 4242 4242`, any future expiry, and any CVC.

## Mailtrap Template Setup

Create a template in [Mailtrap](https://mailtrap.io/templates) that uses these variables:

| Variable | Type | Example |
|---|---|---|
| `order_id` | string | `"cs_test_a1b2c3d4"` |
| `items` | array | `[{"name": "Widget Pro", "quantity": 2, "price": "USD 39.98"}]` |
| `total` | string | `"USD 49.99"` |
| `shipping_address` | object or null | `{"name": "Jane Doe", "line1": "123 Main St", ...}` |
| `recommendations` | array | `[{"name": "Wireless Keyboard", "description": "...", "price": "USD 49.99"}]` |

Copy the template UUID from the template settings and set it as `MAILTRAP_TEMPLATE_UUID`.

## Project Structure

```
order-ai-recommendations/
├── app/
│   ├── app.py                      # FastAPI factory, lifespan, DB init + seed
│   ├── config.py                   # Pydantic-settings env config
│   ├── database.py                 # SQLAlchemy engine + SessionLocal
│   ├── models.py                   # Product + ProcessedEvent ORM models
│   ├── schemas.py                  # OrderItem, ShippingAddress, OrderData, RecommendedProduct
│   ├── seed.py                     # 16-product catalog seed fixture
│   ├── utils.py                    # format_amount helper
│   ├── protocols.py                # Structural interfaces for DI
│   ├── dependencies.py             # lru_cache singletons for FastAPI Depends
│   ├── routers/
│   │   └── webhook_router.py       # POST /stripe/webhook
│   ├── services/
│   │   ├── event_store.py          # SQLAlchemy-backed processed-event store
│   │   ├── stripe_gateway.py       # Stripe SDK wrapper
│   │   ├── recommender.py          # GeminiRecommender
│   │   └── mailer.py               # MailtrapMailer
│   └── use_cases/
│       └── process_checkout.py     # Checkout orchestration logic
├── main.py
├── requirements.txt
└── .env.example
```

## Key Integration Points

**Stripe signature verification**

```python
event = stripe.Webhook.construct_event(payload, sig_header, secret)
```

**SQLAlchemy catalog seed (runs once on startup)**

```python
def seed_products(session: Session) -> None:
    if session.query(Product).count() == 0:
        session.add_all([Product(**p) for p in _PRODUCTS])
        session.commit()
```

**Gemini recommendation prompt**

```python
client = genai.Client(api_key=settings.gemini_api_key)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=user_prompt,
    config=genai.types.GenerateContentConfig(system_instruction=_SYSTEM_PROMPT),
)
ids: list[int] = json.loads(response.text)
```

**Mailtrap template API with `X-MT-Category` header**

```python
mail = mt.MailFromTemplate(
    sender=mt.Address(email=settings.mail_from, name=settings.mail_from_name),
    to=[mt.Address(email=order.customer_email)],
    template_uuid=settings.mailtrap_template_uuid,
    template_variables={
        "order_id": order.order_id,
        "items": [...],
        "total": order.total,
        "shipping_address": shipping,
        "recommendations": [...],
    },
    category="order-confirmation",
)
mt.MailtrapClient(token=settings.mailtrap_api_token).send(mail)
```

**Graceful degradation when Gemini fails**

```python
try:
    ...
    ids = json.loads(response.text)
except Exception:
    logger.warning("Gemini recommendation failed — sending email without recommendations")
    return []
```
