import json
import logging

from google import genai
from google.genai import types

from app.config import get_settings
from app.types import ClassificationResult

logger = logging.getLogger(__name__)

_VALID_CATEGORIES = {"sales", "support", "partnership", "spam", "other"}
_VALID_URGENCIES = {"high", "normal", "low"}
_FALLBACK = ClassificationResult("other", "normal", "Classification unavailable")

_PROMPT_TEMPLATE = """\
You are an email classifier for a business contact form. Classify the message into exactly ONE category and assess its urgency.

Categories:
- sales: Pricing inquiries, demo requests, purchase intent, product questions from potential buyers
- support: Bug reports, technical issues, how-to questions, account problems from existing users
- partnership: Integration proposals, reseller inquiries, co-marketing, affiliate requests
- spam: Irrelevant content, advertisements, phishing attempts, gibberish
- other: Feedback, general questions, job applications, press inquiries

Urgency levels:
- high: Production issues, security concerns, time-sensitive deals, angry customers
- normal: Standard inquiries, general questions, feature requests
- low: Nice-to-have feedback, casual questions, FYI messages

Respond with a JSON object only:
{{
  "category": "sales|support|partnership|spam|other",
  "urgency": "high|normal|low",
  "reason": "One sentence explaining the classification"
}}

Subject: {subject}
Message: {message}\
"""


class GeminiClassifier:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model

    def classify(self, subject: str, message: str) -> ClassificationResult:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=_PROMPT_TEMPLATE.format(subject=subject, message=message),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                    max_output_tokens=1024,
                ),
            )
            data = json.loads(response.text)
            category = data.get("category", "other")
            urgency = data.get("urgency", "normal")
            reason = data.get("reason", "")
            if category not in _VALID_CATEGORIES:
                category = "other"
            if urgency not in _VALID_URGENCIES:
                urgency = "normal"
            return ClassificationResult(category, urgency, reason)
        except Exception:
            logger.exception("Gemini classification failed for subject: %s", subject)
            return _FALLBACK
