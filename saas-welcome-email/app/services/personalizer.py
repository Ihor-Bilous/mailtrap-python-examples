import json
import logging

from google import genai
from google.genai import types

from app.config import get_settings
from app.types import WelcomeContent

logger = logging.getLogger(__name__)

_FALLBACK = WelcomeContent(
    headline="Welcome aboard!",
    body="We're thrilled to have you with us. Explore everything we have to offer and reach out anytime — we're here to help you succeed.",
    cta_text="Get started",
)

_PROMPT_TEMPLATE = """\
You are a SaaS copywriter writing a personalized welcome email for a new user.

User profile:
- Name: {name}
- Role: {role}
- Company size: {company_size}
- Use case: {use_case}

Write personalized welcome email content. Respond with a JSON object only:
{{
  "headline": "A short, role-aware welcome headline (max 10 words)",
  "body": "2-3 sentences personalized to their role, company size, and use case",
  "cta_text": "Call-to-action button label (max 5 words)"
}}\
"""


class GeminiPersonalizer:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def generate(
        self, name: str, role: str, company_size: str, use_case: str
    ) -> WelcomeContent:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=_PROMPT_TEMPLATE.format(
                    name=name,
                    role=role,
                    company_size=company_size,
                    use_case=use_case,
                ),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                    max_output_tokens=1024,
                ),
            )
            data = json.loads(response.text)
            return WelcomeContent(
                headline=str(data.get("headline", _FALLBACK.headline)),
                body=str(data.get("body", _FALLBACK.body)),
                cta_text=str(data.get("cta_text", _FALLBACK.cta_text)),
            )
        except Exception:
            logger.exception("Gemini personalization failed for user: %s", name)
            return _FALLBACK
