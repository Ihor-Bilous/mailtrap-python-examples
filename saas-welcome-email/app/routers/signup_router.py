import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app.dependencies import get_mailer, get_personalizer
from app.protocols import MailerProtocol, PersonalizerProtocol
from app.schemas import SignupFormSchema
from app.templates import templates

logger = logging.getLogger(__name__)

router = APIRouter()

PersonalizerDep = Annotated[PersonalizerProtocol, Depends(get_personalizer)]
MailerDep = Annotated[MailerProtocol, Depends(get_mailer)]


def _field_errors(exc: ValidationError) -> dict[str, str]:
    return {str(err["loc"][0]): err["msg"] for err in exc.errors() if err["loc"]}


@router.get("/")
def root():
    return RedirectResponse("/signup", status_code=303)


@router.get("/signup")
def signup_form(request: Request):
    return templates.TemplateResponse(
        request, "pages/signup.html", {"field_errors": {}, "values": {}}
    )


@router.post("/signup")
async def signup_post(
    request: Request,
    background_tasks: BackgroundTasks,
    personalizer: PersonalizerDep,
    mailer: MailerDep,
):
    raw = dict(await request.form())
    try:
        form = SignupFormSchema.model_validate(raw)
    except ValidationError as e:
        return templates.TemplateResponse(
            request,
            "pages/signup.html",
            {"field_errors": _field_errors(e), "values": raw},
        )

    content = personalizer.generate(
        name=form.name,
        role=form.role,
        company_size=form.company_size,
        use_case=form.use_case,
    )
    background_tasks.add_task(mailer.send_welcome, form.name, str(form.email), content)

    return RedirectResponse("/success", status_code=303)


@router.get("/success")
def success(request: Request):
    return templates.TemplateResponse(request, "pages/success.html", {})
