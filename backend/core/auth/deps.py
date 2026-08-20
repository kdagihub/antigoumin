from ninja.errors import HttpError
from ninja.security import HttpBearer

from core.models import User

from .jwt import decode_access_token


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


jwt_auth = JWTAuth()
