from ninja import Query, Router

from core.auth.deps import jwt_verified_auth

from .schemas import SearchResponseSchema, VerificationHistoryListSchema
from .services import (
    SearchServiceError,
    handle_search_error,
    list_verification_history,
    search_by_phone,
)

router = Router(tags=["Recherche"])


@router.get("/", response=SearchResponseSchema, auth=jwt_verified_auth)
def search(request, phone: str = Query(..., min_length=8, max_length=20)):
    try:
        return search_by_phone(request, request.auth, phone)
    except SearchServiceError as exc:
        handle_search_error(exc)


@router.get("/history/", response=VerificationHistoryListSchema, auth=jwt_verified_auth)
def verification_history(request):
    items = list_verification_history(request.auth)
    return {"items": items, "count": len(items)}
