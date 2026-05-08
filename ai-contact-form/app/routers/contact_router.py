import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.config import get_settings
from app.dependencies import get_classifier, get_mailer
from app.protocols import ClassifierProtocol, MailerProtocol
from app.schemas import ContactFormSchema
from app.templates import templates

logger = logging.getLogger(__name__)

router = APIRouter()

ClassifierDep = Annotated[ClassifierProtocol, Depends(get_classifier)]
MailerDep = Annotated[MailerProtocol, Depends(get_mailer)]


def _field_errors(exc: ValidationError) -> dict[str, str]:
    return {str(err["loc"][0]): err["msg"] for err in exc.errors() if err["loc"]}


@router.get("/")
def root():
    return RedirectResponse("/contact", status_code=303)


@router.get("/contact")
def contact_form(request: Request):
    return templates.TemplateResponse(request, "pages/contact.html", {"field_errors": {}, "values": {}})


@router.post("/contact")
async def contact_post(
    request: Request,
    background_tasks: BackgroundTasks,
    classifier: ClassifierDep,
    mailer: MailerDep,
):
    raw = dict(await request.form())
    try:
        form = ContactFormSchema.model_validate(raw)
    except ValidationError as e:
        return templates.TemplateResponse(
            request, "pages/contact.html", {"field_errors": _field_errors(e), "values": raw}
        )

    result = classifier.classify(subject=form.subject, message=form.message)
    settings = get_settings()
    team_email = settings.routing_map.get(result.category, settings.route_default_email)

    if result.category == "spam":
        logger.warning("Spam submission from %s <%s>: %s", form.name, form.email, result.reason)
    else:
        background_tasks.add_task(mailer.send_notification, form.name, form.email, form.subject, form.message, result, team_email)
        background_tasks.add_task(mailer.send_auto_reply, form.name, form.email, form.subject)

    return RedirectResponse("/success", status_code=303)


@router.get("/success")
def success(request: Request):
    return templates.TemplateResponse(request, "pages/success.html", {})
