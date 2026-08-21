from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from core.notifications.d7 import send_sms
from core.utils.phone import to_e164


class PhoneFormattingTests(SimpleTestCase):
    def test_local_ivory_coast_number_becomes_e164(self):
        self.assertEqual(to_e164("07 00 00 00 00"), "+2250700000000")
        self.assertEqual(to_e164("2250700000000"), "+2250700000000")
        self.assertEqual(to_e164("+2250700000000"), "+2250700000000")


class D7SmsTests(SimpleTestCase):
    @override_settings(D7_TOKEN="", D7_CLIENT_ID="", D7_CLIENT_SECRET="")
    def test_logs_when_d7_is_not_configured(self):
        with self.assertLogs("core.notifications.d7", level="INFO") as logs:
            send_sms("0700000000", "Bonjour")
        self.assertTrue(any("D7 non configuré" in line for line in logs.output))

    @override_settings(
        D7_TOKEN="test-token",
        D7_ORIGINATOR="AntiGoumin",
        D7_API_BASE_URL="https://api.d7networks.com",
    )
    @patch("core.notifications.d7.requests.post")
    def test_sends_bearer_request_with_e164_recipient(self, post):
        response = Mock()
        response.ok = True
        post.return_value = response

        send_sms("0700000000", "Bonjour AntiGoumin")

        post.assert_called_once()
        args, kwargs = post.call_args
        self.assertEqual(args[0], "https://api.d7networks.com/messages/v1/send")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer test-token")
        self.assertEqual(
            kwargs["json"]["messages"][0]["recipients"],
            ["+2250700000000"],
        )
        self.assertEqual(kwargs["json"]["message_globals"]["originator"], "AntiGoumin")
