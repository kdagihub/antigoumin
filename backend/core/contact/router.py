from ninja import Router

from .schemas import ContactCreateSchema, ContactResultSchema
from .services import ContactServiceError, handle_contact_error, submit_contact

router = Router(tags=["Contact"])


@router.post("/", response=ContactResultSchema)
def post_contact(request, payload: ContactCreateSchema):
    ip = request.META.get("REMOTE_ADDR", "")
    try:
        message = submit_contact(
            name=payload.name,
            email=str(payload.email),
            destination=payload.destination,
            message=payload.message,
            website=payload.website,
            ip=ip,
        )
    except ContactServiceError as exc:
        handle_contact_error(exc)
    return ContactResultSchema(message=message)
