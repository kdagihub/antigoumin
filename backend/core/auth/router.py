from ninja import Router

from core.auth.deps import jwt_auth, jwt_verified_auth

from .schemas import (
    GoogleAuthSchema,
    LoginSchema,
    PhoneOtpVerifySchema,
    PhoneUpdateSchema,
    RegisterSchema,
    StatusVisibilitySchema,
    TokenResponse,
    UserSchema,
    VerificationMessageSchema,
)
from .services import (
    AuthServiceError,
    authenticate_google,
    handle_auth_error,
    login_user,
    register_user,
    set_status_searchability,
    user_to_schema,
)
from .verification import (
    confirm_email_token,
    resend_email_verification,
    send_phone_otp,
    set_user_phone,
    verify_phone_otp,
)

router = Router(tags=["Auth"])


@router.patch(
    "/me/status-visibility",
    response=UserSchema,
    auth=jwt_verified_auth,
)
def update_status_visibility(request, payload: StatusVisibilitySchema):
    try:
        return set_status_searchability(
            request.auth,
            is_status_searchable=payload.is_status_searchable,
        )
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.patch("/me/phone", response=UserSchema, auth=jwt_auth)
def update_phone(request, payload: PhoneUpdateSchema):
    try:
        user = set_user_phone(request.auth, payload.phone_number)
        return user_to_schema(user)
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.post(
    "/resend-email-verification",
    response=VerificationMessageSchema,
    auth=jwt_auth,
)
def resend_email(request):
    try:
        return resend_email_verification(request.auth)
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.post("/verify-email/{token}", response=UserSchema)
def verify_email(request, token: str):
    try:
        return confirm_email_token(token)
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.post(
    "/phone/send-otp",
    response=VerificationMessageSchema,
    auth=jwt_auth,
)
def phone_send_otp(request):
    try:
        return send_phone_otp(request.auth)
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.post("/phone/verify", response=UserSchema, auth=jwt_auth)
def phone_verify(request, payload: PhoneOtpVerifySchema):
    try:
        return verify_phone_otp(request.auth, payload.code)
    except AuthServiceError as exc:
        handle_auth_error(exc)


@router.post("/register", response=TokenResponse)
def register(request, payload: RegisterSchema):
    try:
        return register_user(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number,
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
