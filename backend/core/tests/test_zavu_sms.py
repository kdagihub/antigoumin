from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from core.notifications.zavu import send_sms
from core.utils.phone import to_e164


class PhoneFormattingTests(SimpleTestCase):
    def test_local_ivory_coast_number_becomes_e164(self):
        self.assertEqual(to_e164("07 00 00 00 00"), "+2250700000000")
        self.assertEqual(to_e164("2250700000000"), "+2250700000000")
        self.assertEqual(to_e164("+2250700000000"), "+2250700000000")


class ZavuSmsTests(SimpleTestCase):
    @override_settings(ZAVU_API_KEY="", ZAVU_SENDER_ID="")
    def test_logs_when_zavu_is_not_configured(self):
        with self.assertLogs("core.notifications.zavu", level="INFO") as logs:
            send_sms("0700000000", "Bonjour")
        self.assertTrue(any("Zavu non configuré" in line for line in logs.output))

    @override_settings(
        ZAVU_API_KEY="zv_live_test",
        ZAVU_SENDER_ID="kd78a2aesmzccsatd5ayz5rhx98dxgp6",
        ZAVU_API_BASE_URL="https://api.zavu.dev",
    )
    @patch("core.notifications.zavu.requests.post")
    def test_sends_sms_with_bearer_and_sender_header(self, post):
        response = Mock()
        response.ok = True
        post.return_value = response

        send_sms("0700000000", "Bonjour AntiGoumin")

        post.assert_called_once()
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://api.zavu.dev/v1/messages")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer zv_live_test")
        self.assertEqual(
            kwargs["headers"]["Zavu-Sender"],
            "kd78a2aesmzccsatd5ayz5rhx98dxgp6",
        )
        self.assertEqual(kwargs["json"]["to"], "+2250700000000")
        self.assertEqual(kwargs["json"]["text"], "Bonjour AntiGoumin")
        self.assertEqual(kwargs["json"]["channel"], "sms")
