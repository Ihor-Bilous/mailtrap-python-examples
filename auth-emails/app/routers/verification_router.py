from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.dependencies import MailerDep, get_db
from app.exceptions import AlreadyVerified, TokenExpired, TokenInvalid, UserNotFound
from app.schemas import ResendVerificationSchema
from app.templates import templates
from app.use_cases.resend_verification import resend_verification
from app.use_cases.verify_email import verify_email
from app.utils import field_errors

router = APIRouter()


@router.get("/verify-email")
def verify_pending(request: Request):
    email = request.query_params.get("email", "")
    sent = request.query_params.get("sent")
    message = "A new verification link has been sent." if sent else None
    return templates.TemplateResponse(
        request, "pages/verify_pending.html",
        {"email": email, "message": message, "field_errors": {}, "values": {"email": email}},
    )


@router.get("/verify-success")
def verify_success(request: Request):
    return templates.TemplateResponse(request, "pages/verify_success.html")


@router.get("/verify-email/{token}")
def verify_email_get(token: str, request: Request, db: Session = Depends(get_db)):
    try:
        verify_email(token, db)
    except TokenExpired:
        return templates.TemplateResponse(
            request, "pages/verify_error.html",
            {"error": "Your verification link has expired. Please request a new one.", "field_errors": {}, "values": {}},
        )
    except (TokenInvalid, AlreadyVerified):
        return templates.TemplateResponse(
            request, "pages/verify_error.html",
            {"error": "This verification link is invalid or has already been used.", "field_errors": {}, "values": {}},
        )
    return RedirectResponse("/verify-success", status_code=303)


@router.post("/verify-email/resend")
async def resend_verification_post(
    request: Request,
    background_tasks: BackgroundTasks,
    mailer: MailerDep,
    db: Session = Depends(get_db),
):
    raw = dict(await request.form())
    try:
        form = ResendVerificationSchema.model_validate(raw)
    except ValidationError as e:
        email = raw.get("email", "")
        return templates.TemplateResponse(
            request, "pages/verify_pending.html",
            {"email": email, "field_errors": field_errors(e), "values": raw},
        )

    try:
        name, user_email, verification_url = resend_verification(form.email, db)
        background_tasks.add_task(mailer.send_verification_email, name, user_email, verification_url)
    except (UserNotFound, AlreadyVerified):
        pass  # silent — do not reveal whether the account exists

    return RedirectResponse(f"/verify-email?email={form.email}&sent=1", status_code=303)
