from ninja import Router

from core.auth.deps import jwt_verified_auth

from .schemas import (
    AllianceBadgeSchema,
    AllianceDecisionSchema,
    AllianceResultSchema,
    AllianceSchema,
    EligibleDeclarationSchema,
)
from .services import (
    AllianceServiceError,
    decide_alliance,
    end_alliance,
    handle_alliance_error,
    list_eligible_declarations,
    list_user_alliances,
    set_badge_visibility,
)

router = Router(tags=["Alliances Digitales"])


@router.get("/", response=list[AllianceSchema], auth=jwt_verified_auth)
def list_alliances(request):
    return list_user_alliances(request.auth)


@router.get(
    "/eligible-declarations/",
    response=list[EligibleDeclarationSchema],
    auth=jwt_verified_auth,
)
def eligible_declarations(request):
    return list_eligible_declarations(request.auth)


@router.post(
    "/{alliance_id}/decision",
    response=AllianceResultSchema,
    auth=jwt_verified_auth,
)
def decide(request, alliance_id: int, payload: AllianceDecisionSchema):
    try:
        return decide_alliance(
            request.auth,
            alliance_id,
            accept=payload.accept,
        )
    except AllianceServiceError as exc:
        handle_alliance_error(exc)


@router.patch(
    "/{alliance_id}/badge",
    response=AllianceSchema,
    auth=jwt_verified_auth,
)
def update_badge(request, alliance_id: int, payload: AllianceBadgeSchema):
    try:
        return set_badge_visibility(
            request.auth,
            alliance_id,
            visible=payload.visible,
        )
    except AllianceServiceError as exc:
        handle_alliance_error(exc)


@router.post(
    "/{alliance_id}/end",
    response=AllianceResultSchema,
    auth=jwt_verified_auth,
)
def end(request, alliance_id: int):
    try:
        return end_alliance(request.auth, alliance_id)
    except AllianceServiceError as exc:
        handle_alliance_error(exc)
