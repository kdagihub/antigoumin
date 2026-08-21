from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone

from core.models import Payment, User
from core.payments.services import apply_geniuspay_event, create_checkout


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    FRONTEND_BASE_URL="http://localhost:5173",
)
class GeniusPayCheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="pay@example.com",
            password="strong-password",
            phone_number="2250700000099",
            email_verified_at=timezone.now(),
            phone_verified_at=timezone.now(),
        )

    @patch("core.payments.services.GeniusPayClient")
    def test_checkout_creates_geniuspay_session(self, client_cls):
        payment = MagicMock()
        payment.checkout_url = "https://geniuspay.ci/checkout/abc"
        payment.payment_url = None
        payment.reference = "MTX-TEST-1"
        client_cls.return_value.payments.create.return_value = payment

        result = create_checkout(
            self.user,
            service_type="DECLARATION",
        )
        self.assertEqual(result["checkout_url"], "https://geniuspay.ci/checkout/abc")
        self.assertEqual(result["reference"], "MTX-TEST-1")
        kwargs = client_cls.return_value.payments.create.call_args.kwargs
        self.assertEqual(kwargs["amount"], 300)
        self.assertEqual(kwargs["metadata"]["user_id"], self.user.id)
        self.assertEqual(kwargs["metadata"]["service_type"], "DECLARATION")

    def test_geniuspay_success_credits_declaration(self):
        apply_geniuspay_event(
            {
                "event": "payment.success",
                "data": {
                    "reference": "MTX-TEST-2",
                    "amount": 300,
                    "status": "completed",
                    "metadata": {
                        "user_id": self.user.id,
                        "service_type": "DECLARATION",
                    },
                },
            }
        )
        credited = Payment.objects.get(reference="MTX-TEST-2")
        self.assertEqual(credited.status, Payment.Status.SUCCESS)
        self.assertEqual(credited.service_type, "DECLARATION")
        self.assertFalse(credited.consumed)
