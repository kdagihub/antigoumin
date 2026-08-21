from ninja import Router

from core.auth.deps import jwt_verified_auth

from .schemas import (
    TransparencyRequestCreateSchema,
    TransparencyRequestPreviewSchema,
    TransparencyRequestRespondSchema,
    TransparencyRequestResultSchema,
    TransparencyRequestSchema,
)
from .services import (
    TransparencyRequestServiceError,
    create_transparency_request,
    handle_transparency_request_error,
    preview_transparency_request,
    respond_to_transparency_request,
)

router = Router(tags=["Demandes de Transparence"])


@router.post("/", response=TransparencyRequestSchema, auth=jwt_verified_auth)
def create_request(request, payload: TransparencyRequestCreateSchema):
    try:
        return create_transparency_request(
            request,
            request.auth,
            target_phone=payload.target_phone,
            payment_id=payload.payment_id,
        )
    except TransparencyRequestServiceError as exc:
        handle_transparency_request_error(exc)


@router.get("/{token}", response=TransparencyRequestPreviewSchema)
def get_request(request, token: str):
    try:
        return preview_transparency_request(token)
    except TransparencyRequestServiceError as exc:
        handle_transparency_request_error(exc)


@router.post("/{token}/respond", response=TransparencyRequestResultSchema)
def respond(request, token: str, payload: TransparencyRequestRespondSchema):
    try:
        return respond_to_transparency_request(
            token,
            action=payload.action,
            declared_status=payload.declared_status,
            declared_partner_name=payload.declared_partner_name,
        )
    except TransparencyRequestServiceError as exc:
        handle_transparency_request_error(exc)
