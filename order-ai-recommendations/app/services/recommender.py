import json
import logging

from google import genai

from app.config import get_settings
from app.models import Product
from app.schemas import RecommendedProduct
from app.utils import format_amount

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a product recommendation engine for an online store. "
    "Given a list of purchased items and a product catalog, return exactly 3 product IDs "
    "from the catalog that best complement the purchased items. "
    "Respond with a JSON array of integers only, e.g. [3, 7, 12]. No explanation."
)


class GeminiRecommender:
    def get_recommendations(
        self, purchased_names: list[str], catalog: list[Product]
    ) -> list[RecommendedProduct]:
        if not purchased_names or not catalog:
            return []

        prompt = self._build_prompt(purchased_names, catalog)
        ids = self._fetch_recommended_ids(prompt)
        if ids is None:
            return []

        return self._resolve_products(ids, catalog)

    def _build_prompt(self, purchased_names: list[str], catalog: list[Product]) -> str:
        catalog_text = "\n".join(
            f"ID {p.id}: {p.name} ({p.category}) — {p.description}" for p in catalog
        )
        return f"Purchased: {', '.join(purchased_names)}\n\nCatalog:\n{catalog_text}"

    def _fetch_recommended_ids(self, prompt: str) -> list[int] | None:
        try:
            settings = get_settings()
            client = genai.Client(api_key=settings.gemini_api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=_SYSTEM_PROMPT,
                ),
            )
            return json.loads(response.text)
        except Exception:
            logger.warning(
                "Gemini recommendation failed — sending email without recommendations",
                exc_info=True,
            )
            return None

    def _resolve_products(
        self, ids: list[int], catalog: list[Product]
    ) -> list[RecommendedProduct]:
        catalog_by_id = {p.id: p for p in catalog}
        result = []
        for pid in ids:
            product = catalog_by_id.get(pid)
            if product:
                result.append(
                    RecommendedProduct(
                        name=product.name,
                        description=product.description,
                        price=format_amount(product.price_cents, product.currency),
                    )
                )
        return result
