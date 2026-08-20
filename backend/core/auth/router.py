from ninja import Router

from .schemas import GoogleAuthSchema, LoginSchema, RegisterSchema, TokenResponse
from .services import (
    AuthServiceError,
    authenticate_google,
    handle_auth_error,
    login_user,
    register_user,
)

router = Router(tags=["Auth"])


@router.post("/register", response=TokenResponse)
def register(request, payload: RegisterSchema):
    try:
        return register_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.post("/login", response=TokenResponse)
def login(request, payload: LoginSchema):
    try:
        return login_user(email=payload.email, password=payload.password)
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.post("/google", response=TokenResponse)
def google_login(request, payload: GoogleAuthSchema):
    try:
        return authenticate_google(payload.id_token)
    except AuthServiceError as exc:
        handle_auth_error(exc)
