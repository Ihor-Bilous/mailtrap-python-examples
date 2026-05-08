# Mailtrap Python Examples

Practical Python examples showing how to integrate [Mailtrap](https://mailtrap.io) into real-world application flows — from transactional auth emails to AI-powered routing and deliverability monitoring.

Each example is a self-contained FastAPI app with its own setup instructions.

## Examples

| Example | Description |
|---|---|
| [ai-contact-form](ai-contact-form/README.md) | Contact form that classifies submissions with Gemini and routes notifications to the right team inbox |
| [auth-emails](auth-emails/README.md) | User registration flow with email verification and password reset |
| [deliverability-monitor](deliverability-monitor/README.md) | Scheduled polling + webhook endpoint that tracks bounce/complaint rates and alerts via Gemini-analyzed summaries |
| [order-ai-recommendations](order-ai-recommendations/README.md) | Stripe checkout webhook that sends order confirmation emails with AI-generated product recommendations |
| [order-confirmation](order-confirmation/README.md) | Stripe checkout webhook that sends order confirmation emails via Mailtrap template API |
| [saas-welcome-email](saas-welcome-email/README.md) | Welcome email with Gemini-personalized copy based on user role, company size, and use case |
