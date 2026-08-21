from ninja import File, Form, Query, Router, UploadedFile

from core.auth.deps import jwt_verified_auth
from core.models import Declaration

from .schemas import (
    DeclarationListSchema,
    DeclarationSchema,
    PartnerPreviewSchema,
    VerifyPreviewSchema,
    VerifyResultSchema,
)
from .services import (
    DeclarationServiceError,
    create_declaration,
    end_declaration,
    handle_declaration_error,
    list_declarations,
    preview_partner,
    preview_verification,
    process_verification,
)

router = Router(tags=["Déclarations"])


@router.get("/", response=DeclarationListSchema, auth=jwt_verified_auth)
def get_declarations(request):
    items = list_declarations(request, request.auth)
    return {"items": items, "count": len(items)}


@router.get("/partner-preview", response=PartnerPreviewSchema, auth=jwt_verified_auth)
def get_partner_preview(request, phone: str = Query(..., min_length=8, max_length=20)):
    try:
        return preview_partner(phone)
    except DeclarationServiceError as exc:
        handle_declaration_error(exc)


@router.post("/{declaration_id}/end", response=VerifyResultSchema, auth=jwt_verified_auth)
def end_verified_declaration(request, declaration_id: int):
    try:
        return end_declaration(request.auth, declaration_id)
    except DeclarationServiceError as exc:
        handle_declaration_error(exc)


@router.post("/", response=DeclarationSchema, auth=jwt_verified_auth)
def post_declaration(
    request,
    partner_phone: str = Form(...),
    partner_name: str = Form(...),
    partner_photo: UploadedFile = File(...),
    relation_type: str = Form(Declaration.RelationType.AMOUR),
    visibility: str = Form(Declaration.Visibility.PUBLIC_CERTIFIED),
    payment_id: int | None = Form(None),
):
    try:
        return create_declaration(
            request,
            request.auth,
            partner_phone=partner_phone,
            partner_name=partner_name,
            partner_photo=partner_photo,
            relation_type=relation_type,
            visibility=visibility,
            payment_id=payment_id,
        )
    except DeclarationServiceError as exc:
        handle_declaration_error(exc)


@router.get("/verify/{token}", response=VerifyPreviewSchema)
def get_verify_preview(request, token: str):
    try:
        return preview_verification(token)
    except DeclarationServiceError as exc:
        handle_declaration_error(exc)


@router.post("/verify/{token}/accept", response=VerifyResultSchema)
def accept_declaration(request, token: str):
    try:
        return process_verification(token, accept=True)
    except DeclarationServiceError as exc:
        handle_declaration_error(exc)


@router.post("/verify/{token}/reject", response=VerifyResultSchema)
def reject_declaration(request, token: str):
    try:
        return process_verification(token, accept=False)
    except DeclarationServiceError as exc:
        handle_declaration_error(exc)
