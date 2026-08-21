from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from ninja.testing import TestClient

from core.api import api
from core.auth.jwt import create_access_token
from core.auth.services import authenticate_google, register_user
from core.auth.verification import send_phone_otp, verify_phone_otp
from core.contact.services import ContactServiceError, submit_contact
from core.models import User
from core.payments.services import PaymentServiceError, process_payment_webhook


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    EMAIL_HOST="",
)
class AccountVerificationTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch("core.auth.verification.notify_user_by_email")
    def test_register_requires_phone_and_leaves_email_unverified(self, _email):
        response = register_user(
            email="awa@example.com",
            password="strong-password",
            phone_number="0700000011",
        )
        self.assertFalse(response.user.email_verified)
        self.assertFalse(response.user.phone_verified)
        self.assertFalse(response.user.is_fully_verified)
        _email.assert_called()

    @patch("core.auth.services.google_id_token.verify_oauth2_token")
    def test_google_marks_email_verified_but_not_phone(self, verify_token):
        verify_token.return_value = {
            "sub": "google-1",
            "email": "google@example.com",
            "email_verified": True,
            "given_name": "Awa",
            "family_name": "Koffi",
        }
        with override_settings(GOOGLE_OAUTH_CLIENT_ID="test-client"):
            response = authenticate_google("id-token")
        self.assertTrue(response.user.email_verified)
        self.assertFalse(response.user.phone_verified)

    @patch("core.auth.verification.notify_user_by_email")
    @patch("core.auth.verification.send_sms")
    def test_phone_otp_confirms_number(self, _sms, _email):
        user = User.objects.create_user(
            email="otp@example.com",
            password="strong-password",
            phone_number="2250700000012",
            email_verified_at=timezone.now(),
        )
        send_phone_otp(user)
        payload = cache.get(f"agm:account-otp:{user.id}")
        schema = verify_phone_otp(user, payload["code"])
        self.assertTrue(schema.phone_verified)
        self.assertTrue(schema.is_fully_verified)

    def test_unverified_user_cannot_purchase(self):
        user = User.objects.create_user(
            email="blocked@example.com",
            password="strong-password",
            phone_number="2250700000013",
        )
        with self.assertRaises(PaymentServiceError) as ctx:
            process_payment_webhook(
                reference="pay-1",
                status="SUCCESS",
                service_type="VERIFICATION",
                amount=200,
                user_id=user.id,
                metadata={"phone": "0700000014"},
            )
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertIn("Vérifiez", ctx.exception.message)

    def test_search_api_blocked_until_verified(self):
        user = User.objects.create_user(
            email="search@example.com",
            password="strong-password",
            phone_number="2250700000015",
        )
        token = create_access_token(user.id)
        client = TestClient(api)
        response = client.get(
            "/search/?phone=0700000016",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    @patch("core.contact.services.send_transactional_email")
    def test_contact_form_routes_to_privacy(self, send_email):
        message = submit_contact(
            name="Awa Test",
            email="awa@example.com",
            destination="privacy",
            message="Question sur mes données personnelles.",
            website="",
            ip="127.0.0.1",
        )
        self.assertIn("transmis", message)
        send_email.assert_called_once()
        self.assertEqual(send_email.call_args.kwargs.get("reply_to"), "awa@example.com")

    @patch("core.contact.services.send_transactional_email")
    def test_contact_rate_limit(self, send_email):
        for index in range(5):
            submit_contact(
                name="Awa Test",
                email="awa@example.com",
                destination="contact",
                message="Question générale sur AntiGoumin.",
                website="",
                ip="10.0.0.8",
            )
        with self.assertRaises(ContactServiceError) as ctx:
            submit_contact(
                name="Awa Test",
                email="awa@example.com",
                destination="contact",
                message="Encore une question.",
                website="",
                ip="10.0.0.8",
            )
        self.assertEqual(ctx.exception.status_code, 429)
        self.assertEqual(send_email.call_count, 5)
