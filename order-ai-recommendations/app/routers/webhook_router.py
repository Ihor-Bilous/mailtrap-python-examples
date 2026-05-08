import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import SessionLocal
from app.dependencies import get_mailer, get_recommender, get_stripe_gateway
from app.protocols import MailerProtocol, RecommenderProtocol, StripeGatewayProtocol
from app.services import event_store
from app.services.stripe_gateway import WebhookVerificationError
from app.use_cases.process_checkout import process_checkout

logger = logging.getLogger(__name__)

router = APIRouter()

StripeGatewayDep = Annotated[StripeGatewayProtocol, Depends(get_stripe_gateway)]
RecommenderDep = Annotated[RecommenderProtocol, Depends(get_recommender)]
MailerDep = Annotated[MailerProtocol, Depends(get_mailer)]


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_gateway: StripeGatewayDep,
    recommender: RecommenderDep,
    mailer: MailerDep,
) -> JSONResponse:
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    settings = get_settings()

    try:
        event = stripe_gateway.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except WebhookVerificationError:
        logger.warning("Stripe webhook verification failed")
        return JSONResponse({"error": "Invalid signature"}, status_code=400)

    with SessionLocal() as db_session:
        if event_store.is_processed(event["id"], db_session):
            logger.info("Duplicate Stripe event skipped: %s", event["id"])
            return JSONResponse({"status": "already_processed"})

        if event["type"] == "checkout.session.completed":
            try:
                process_checkout(
                    session_id=event["data"]["object"]["id"],
                    stripe_gateway=stripe_gateway,
                    recommender=recommender,
                    mailer=mailer,
                    db_session=db_session,
                )
            except Exception:
                logger.exception(
                    "Failed to process checkout.session.completed event %s", event["id"]
                )
                return JSONResponse({"error": "Processing failed"}, status_code=500)

        event_store.mark_processed(event["id"], db_session)

    return JSONResponse({"status": "ok"})
