from ninja.errors import HttpError
from ninja.security import HttpBearer

from core.models import User

from .jwt import decode_access_token


VERIFICATION_REQUIRED_MESSAGE = (
    "Vérifiez votre email ou votre téléphone avant d'utiliser les services."
)


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = decode_access_token(token)
            user = User.objects.get(id=payload["user_id"], is_active=True)
        except User.DoesNotExist as exc:
            raise HttpError(401, "Utilisateur introuvable.") from exc
        except Exception as exc:
            raise HttpError(401, "Token invalide ou expiré.") from exc

        request.user = user
        return user


class JWTVerifiedAuth(JWTAuth):
    def authenticate(self, request, token):
        user = super().authenticate(request, token)
        if user and not user.is_fully_verified:
            raise HttpError(403, VERIFICATION_REQUIRED_MESSAGE)
        return user


def require_fully_verified(user: User) -> None:
    if not user.is_fully_verified:
        raise HttpError(403, VERIFICATION_REQUIRED_MESSAGE)


jwt_auth = JWTAuth()
jwt_verified_auth = JWTVerifiedAuth()
