from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from core.alliances.alerts import (
    DECLARANT_PARTNER_ENGAGED_NOTICE,
    PARTNER_DECLARED_ALERT_MESSAGE,
    notify_alliance_partners_of_new_declaration,
    partner_has_active_vip_alliance,
)
from core.declarations.services import create_declaration, preview_partner
from core.models import Alliance, Declaration, InAppNotification, Payment, User


class DeclarationAllianceAlertTests(TestCase):
    def setUp(self):
        self.declarant = User.objects.create_user(
            email="declarant@example.com",
            password="strong-password",
            first_name="Nouveau",
        )
        self.allied_user = User.objects.create_user(
            email="allied@example.com",
            password="strong-password",
            phone_number="+2250700000100",
            first_name="Partenaire",
        )
        self.alliance_partner = User.objects.create_user(
            email="vip@example.com",
            password="strong-password",
            first_name="VIP",
        )
        self.declaration = Declaration.objects.create(
            author=self.allied_user,
            accepted_by=self.alliance_partner,
            partner_phone=self.allied_user.phone_number,
            partner_name="Partenaire",
            partner_photo="declarations/allied.jpg",
            status=Declaration.Status.VERIFIED,
            visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
            verified_at=timezone.now(),
        )
        payment = Payment.objects.create(
            user=self.allied_user,
            service_type=Payment.ServiceType.ALLIANCE_VIP,
            amount=1200,
            reference="alliance-alert-test",
            status=Payment.Status.SUCCESS,
        )
        Alliance.objects.create(
            initiator=self.allied_user,
            partner=self.alliance_partner,
            declaration=self.declaration,
            payment=payment,
            status=Alliance.Status.ACTIVE,
            initiator_consented_at=timezone.now(),
            partner_consented_at=timezone.now(),
            subscription_end_date=timezone.now() + timedelta(days=30),
        )
        self.declaration_payment = Payment.objects.create(
            user=self.declarant,
            service_type=Payment.ServiceType.DECLARATION,
            amount=300,
            reference="declaration-alert-test",
            status=Payment.Status.SUCCESS,
        )

    def test_partner_preview_warns_when_partner_in_active_alliance(self):
        preview = preview_partner(self.allied_user.phone_number)
        self.assertTrue(preview.partner_in_active_alliance)
        self.assertEqual(preview.partner_alliance_notice, DECLARANT_PARTNER_ENGAGED_NOTICE)

    def test_partner_has_active_vip_alliance(self):
        self.assertTrue(partner_has_active_vip_alliance(self.allied_user.phone_number))
        self.assertFalse(partner_has_active_vip_alliance("+2250700000999"))

    @patch("core.alliances.alerts.notify_user_by_email")
    @patch("core.declarations.services.send_verification_sms_async")
    @patch("core.declarations.services.notify_user_by_email")
    @patch("core.declarations.services.notify_phone_or_user_email")
    def test_new_declaration_notifies_alliance_partner(
        self,
        notify_phone,
        notify_declarant_email,
        send_sms,
        notify_alert_email,
    ):
        class DummyFile:
            content_type = "image/jpeg"
            size = 1024

        with patch("core.declarations.services.store_verification_token", return_value="token"):
            create_declaration(
                None,
                self.declarant,
                partner_phone=self.allied_user.phone_number,
                partner_name="Partenaire",
                partner_photo=DummyFile(),
                payment_id=self.declaration_payment.id,
            )

        notification = InAppNotification.objects.get(
            recipient=self.alliance_partner,
            type=InAppNotification.Type.PARTNER_DECLARED_BY_OTHER,
        )
        self.assertEqual(notification.message, PARTNER_DECLARED_ALERT_MESSAGE)
        self.assertNotIn(self.declarant.email, notification.message)
        self.assertNotIn(self.declarant.first_name, notification.message)

    def test_notify_helper_skips_declarant_recipient(self):
        notified = notify_alliance_partners_of_new_declaration(
            declared_partner_phone=self.allied_user.phone_number,
            declaration_id=999,
            exclude_user_id=self.alliance_partner.id,
        )
        self.assertEqual(notified, 0)
        self.assertFalse(
            InAppNotification.objects.filter(
                type=InAppNotification.Type.PARTNER_DECLARED_BY_OTHER,
            ).exists()
        )
