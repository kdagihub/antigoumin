from ninja import Query, Router

from core.auth.deps import jwt_verified_auth

from .schemas import SearchResponseSchema
from .services import SearchServiceError, handle_search_error, search_by_phone

router = Router(tags=["Recherche"])


@router.get("/", response=SearchResponseSchema, auth=jwt_verified_auth)
def search(request, phone: str = Query(..., min_length=8, max_length=20)):
    try:
        return search_by_phone(request, request.auth, phone)
    except SearchServiceError as exc:
        handle_search_error(exc)
