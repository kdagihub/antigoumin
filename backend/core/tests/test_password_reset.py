from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings

from ninja.testing import TestClient

from core.api import api
from core.auth.password_reset import confirm_password_reset, request_password_reset
from core.auth.services import AuthServiceError, login_user
from core.models import User


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    EMAIL_HOST="",
)
class PasswordResetTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch("core.auth.password_reset.notify_user_by_email")
    def test_request_sends_email_for_password_account(self, send_email):
        User.objects.create_user(
            email="reset@example.com",
            password="old-password-1",
        )
        result = request_password_reset("reset@example.com", ip="127.0.0.1")
        self.assertIn("Si un compte email existe", result.message)
        send_email.assert_called_once()

    @patch("core.auth.password_reset.notify_user_by_email")
    def test_request_is_generic_for_unknown_email(self, send_email):
        result = request_password_reset("missing@example.com", ip="127.0.0.1")
        self.assertIn("Si un compte email existe", result.message)
        send_email.assert_not_called()

    @patch("core.auth.password_reset.notify_user_by_email")
    def test_request_skips_google_only_account(self, send_email):
        user = User(
            email="google@example.com",
            auth_provider=User.AuthProvider.GOOGLE,
            google_id="google-reset",
        )
        user.set_unusable_password()
        user.save()
        result = request_password_reset("google@example.com", ip="127.0.0.1")
        self.assertIn("Si un compte email existe", result.message)
        send_email.assert_not_called()

    @patch("core.auth.password_reset.notify_user_by_email")
    def test_confirm_resets_password(self, _send_email):
        user = User.objects.create_user(
            email="confirm@example.com",
            password="old-password-1",
        )
        request_password_reset("confirm@example.com", ip="127.0.0.1")
        token = cache.get(f"agm:password-reset-user:{user.id}")
        result = confirm_password_reset(token, "new-password-9")
        self.assertIn("mis à jour", result.message)
        login_user("confirm@example.com", "new-password-9")

    def test_confirm_rejects_invalid_token(self):
        with self.assertRaises(AuthServiceError):
            confirm_password_reset("invalid-token", "new-password-9")

    @patch("core.auth.password_reset.notify_user_by_email")
    def test_api_endpoints(self, _send_email):
        user = User.objects.create_user(
            email="api-reset@example.com",
            password="old-password-1",
        )
        client = TestClient(api)
        response = client.post(
            "/auth/password-reset/request",
            json={"email": "api-reset@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        token = cache.get(f"agm:password-reset-user:{user.id}")
        confirm = client.post(
            f"/auth/password-reset/{token}",
            json={"password": "brand-new-password"},
        )
        self.assertEqual(confirm.status_code, 200)
        login_user("api-reset@example.com", "brand-new-password")
