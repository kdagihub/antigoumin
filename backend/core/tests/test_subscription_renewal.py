from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from core.models import Alliance, Declaration, InAppNotification, Payment, User
from core.payments.services import create_checkout, process_payment_webhook
from core.subscriptions.services import (
    expire_lapsed_subscriptions,
    renew_alliance_subscription,
    send_subscription_expiry_reminders,
)


class SubscriptionRenewalTests(TestCase):
    def setUp(self):
        self.initiator = User.objects.create_user(
            email="initiator@example.com",
            password="strong-password",
            phone_number="+2250700000001",
            email_verified_at=timezone.now(),
        )
        self.partner = User.objects.create_user(
            email="partner@example.com",
            password="strong-password",
            phone_number="+2250700000002",
            email_verified_at=timezone.now(),
        )
        self.declaration = Declaration.objects.create(
            author=self.initiator,
            accepted_by=self.partner,
            partner_phone=self.partner.phone_number,
            partner_name="Partenaire",
            partner_photo="declarations/test.jpg",
            status=Declaration.Status.VERIFIED,
            visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
            verified_at=timezone.now(),
        )
        initial_payment = Payment.objects.create(
            user=self.initiator,
            service_type=Payment.ServiceType.ALLIANCE_VIP,
            amount=1200,
            reference="alliance-initial",
            status=Payment.Status.SUCCESS,
            consumed=True,
        )
        self.alliance = Alliance.objects.create(
            declaration=self.declaration,
            initiator=self.initiator,
            partner=self.partner,
            payment=initial_payment,
            status=Alliance.Status.ACTIVE,
            initiator_consented_at=timezone.now(),
            partner_consented_at=timezone.now(),
            subscription_end_date=timezone.now() + timedelta(days=5),
            initiator_badge_public=True,
            partner_badge_public=True,
        )
        self.initiator.subscription_end_date = self.alliance.subscription_end_date
        self.partner.subscription_end_date = self.alliance.subscription_end_date
        self.initiator.alliance_badge_enabled = True
        self.partner.alliance_badge_enabled = True
        self.initiator.is_status_searchable = False
        self.partner.is_status_searchable = False
        self.initiator.save()
        self.partner.save()

    def test_renew_extends_from_current_end_date(self):
        payment = Payment.objects.create(
            user=self.initiator,
            service_type=Payment.ServiceType.ALLIANCE_VIP,
            amount=1200,
            reference="renew-1",
            status=Payment.Status.SUCCESS,
        )
        previous_end = self.alliance.subscription_end_date
        new_end = renew_alliance_subscription(self.initiator, self.alliance.id, payment)

        self.assertEqual(new_end, previous_end + timedelta(days=30))
        self.alliance.refresh_from_db()
        self.initiator.refresh_from_db()
        self.partner.refresh_from_db()
        self.assertEqual(self.alliance.subscription_end_date, new_end)
        self.assertEqual(self.initiator.subscription_end_date, new_end)
        self.assertEqual(self.partner.subscription_end_date, new_end)
        payment.refresh_from_db()
        self.assertTrue(payment.consumed)

    @patch("core.payments.services.GeniusPayClient")
    def test_create_checkout_renewal_includes_alliance_metadata(self, mock_client):
        mock_client.return_value.payments.create.return_value.checkout_url = "https://pay.test"
        mock_client.return_value.payments.create.return_value.payment_url = None
        mock_client.return_value.payments.create.return_value.reference = "gp-renew"

        result = create_checkout(
            self.initiator,
            service_type="ALLIANCE_VIP",
            renewal=True,
        )

        self.assertEqual(result["service_type"], "ALLIANCE_VIP")
        create_kwargs = mock_client.return_value.payments.create.call_args.kwargs
        self.assertTrue(create_kwargs["metadata"]["renewal"])
        self.assertEqual(create_kwargs["metadata"]["alliance_id"], self.alliance.id)

    def test_process_payment_webhook_renewal(self):
        end_before = self.alliance.subscription_end_date
        process_payment_webhook(
            reference="renew-webhook-1",
            status=Payment.Status.SUCCESS,
            service_type="ALLIANCE_VIP",
            amount=1200,
            user_id=self.initiator.id,
            metadata={"renewal": True, "alliance_id": self.alliance.id},
        )
        self.alliance.refresh_from_db()
        self.assertEqual(
            self.alliance.subscription_end_date,
            end_before + timedelta(days=30),
        )

    def test_send_reminder_on_j_minus_3(self):
        self.alliance.subscription_end_date = timezone.now() + timedelta(days=3)
        self.alliance.save(update_fields=["subscription_end_date"])
        sent = send_subscription_expiry_reminders()
        self.assertEqual(sent, 2)
        self.assertTrue(
            InAppNotification.objects.filter(
                recipient=self.initiator,
                type=InAppNotification.Type.SUBSCRIPTION_EXPIRING,
            ).exists()
        )

    def test_expire_lapsed_subscription_resets_benefits(self):
        self.alliance.subscription_end_date = timezone.now() - timedelta(days=1)
        self.alliance.save(update_fields=["subscription_end_date"])
        processed = expire_lapsed_subscriptions()
        self.assertEqual(processed, 1)
        self.alliance.refresh_from_db()
        self.initiator.refresh_from_db()
        self.assertFalse(self.alliance.initiator_badge_public)
        self.assertFalse(self.initiator.alliance_badge_enabled)
        self.assertTrue(self.initiator.is_status_searchable)
        self.assertTrue(
            InAppNotification.objects.filter(
                recipient=self.initiator,
                type=InAppNotification.Type.SUBSCRIPTION_EXPIRED,
            ).exists()
        )
