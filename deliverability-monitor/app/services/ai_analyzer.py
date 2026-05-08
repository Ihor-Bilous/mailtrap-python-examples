import json
import logging
import re

from google import genai

from app.config import get_settings
from app.schemas import Anomaly, AnomalyReport

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are an email deliverability expert. Analyze the provided anomaly and return a JSON object "
    "with exactly three keys: summary (string, 2-3 sentences), root_cause (string, hypothesis), "
    "recommended_actions (array of 3-5 strings). No other text."
)


class GeminiAnalyzer:
    def analyze(self, anomaly: Anomaly) -> AnomalyReport:
        try:
            settings = get_settings()
            client = genai.Client(api_key=settings.gemini_api_key)
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=_build_prompt(anomaly),
                config=genai.types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.7,
                ),
            )
            data = json.loads(response.text)
            return AnomalyReport(
                summary=data["summary"],
                root_cause=data["root_cause"],
                recommended_actions=data["recommended_actions"],
            )
        except Exception:
            logger.warning("Gemini analysis failed", exc_info=True)
            return AnomalyReport(
                summary="AI analysis unavailable — check logs for details.",
                root_cause="",
                recommended_actions=[],
            )
            

def _build_prompt(anomaly: Anomaly) -> str:
    lines = [
        f"Anomaly type: {anomaly.type}",
        f"Observed rate: {anomaly.rate:.2%}",
        f"Threshold: {anomaly.threshold:.2%}",
        f"Sample size: {anomaly.sample_size}",
    ]
    if anomaly.details:
        lines.append("\nAffected messages (sample):")
        for entry in anomaly.details[:5]:
            reason = f" — {entry.bounce_reason}" if entry.bounce_reason else ""
            lines.append(f"  {entry.recipient} | {entry.status}{reason}")
    return "\n".join(lines)
