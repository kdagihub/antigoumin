from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.dashboard.services import build_dashboard_summary
from core.models import (
    Alliance,
    Declaration,
    Payment,
    PhoneVerificationAccess,
    TransparencyRequest,
    User,
)


class DashboardSummaryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="member@example.com",
            password="strong-password",
            first_name="Awa",
            email_verified_at=timezone.now(),
        )

    def test_empty_user_gets_first_verification_action(self):
        summary = build_dashboard_summary(self.user)
        stat_map = {item.key: item.value for item in summary["stats"]}
        self.assertEqual(stat_map["declarations"], 0)
        self.assertEqual(stat_map["verifications"], 0)
        self.assertEqual(stat_map["active_alliances"], 0)
        self.assertEqual(stat_map["transparency_requests"], 0)
        self.assertEqual(summary["activity"], [])
        self.assertEqual(summary["next_action"].code, "first_verification")

    def test_unverified_user_gets_verify_account_action(self):
        self.user.email_verified_at = None
        self.user.save(update_fields=["email_verified_at"])
        summary = build_dashboard_summary(self.user)
        self.assertEqual(summary["next_action"].code, "verify_account")

    def test_stats_and_activity_reflect_user_actions(self):
        access = PhoneVerificationAccess.objects.create(
            user=self.user,
            phone="2250700000001",
            payment=None,
            expires_at=timezone.now(),
            used_at=timezone.now(),
            result_status="NOT_A_MEMBER",
        )
        Declaration.objects.create(
            author=self.user,
            partner_phone="2250700000002",
            partner_name="Kofi",
            partner_photo="declarations/test.jpg",
            status=Declaration.Status.PENDING,
        )
        TransparencyRequest.objects.create(
            requester=self.user,
            target_phone="2250700000003",
            token="token-abc",
            expires_at=timezone.now() + timedelta(hours=48),
        )

        summary = build_dashboard_summary(self.user)
        stat_map = {item.key: item.value for item in summary["stats"]}
        self.assertEqual(stat_map["verifications"], 1)
        self.assertEqual(stat_map["declarations"], 1)
        self.assertEqual(stat_map["transparency_requests"], 1)
        self.assertGreaterEqual(len(summary["activity"]), 3)
        self.assertIsNone(summary["next_action"])

    def test_suggests_alliance_when_verified_relation_exists(self):
        partner = User.objects.create_user(
            email="partner2@example.com",
            password="strong-password",
            phone_number="2250700000006",
        )
        Declaration.objects.create(
            author=self.user,
            accepted_by=partner,
            partner_phone=partner.phone_number,
            partner_name="Kofi",
            partner_photo="declarations/verified.jpg",
            status=Declaration.Status.VERIFIED,
            verified_at=timezone.now(),
        )
        PhoneVerificationAccess.objects.create(
            user=self.user,
            phone="2250700000007",
            payment=None,
            expires_at=timezone.now(),
            used_at=timezone.now(),
            result_status="NOT_A_MEMBER",
        )

        summary = build_dashboard_summary(self.user)
        self.assertEqual(summary["next_action"].code, "create_alliance")

    def test_active_alliance_skips_create_alliance_action(self):
        partner = User.objects.create_user(
            email="partner@example.com",
            password="strong-password",
            phone_number="2250700000004",
        )
        declaration = Declaration.objects.create(
            author=self.user,
            accepted_by=partner,
            partner_phone=partner.phone_number,
            partner_name="Partenaire",
            partner_photo="declarations/alliance.jpg",
            status=Declaration.Status.VERIFIED,
            verified_at=timezone.now(),
        )
        payment = Payment.objects.create(
            user=self.user,
            service_type=Payment.ServiceType.ALLIANCE_VIP,
            amount=1200,
            reference="dash-alliance",
            status=Payment.Status.SUCCESS,
        )
        Alliance.objects.create(
            initiator=self.user,
            partner=partner,
            declaration=declaration,
            payment=payment,
            status=Alliance.Status.ACTIVE,
            initiator_consented_at=timezone.now(),
            partner_consented_at=timezone.now(),
            subscription_end_date=timezone.now() + timedelta(days=30),
        )
        PhoneVerificationAccess.objects.create(
            user=self.user,
            phone="2250700000005",
            payment=None,
            expires_at=timezone.now(),
            used_at=timezone.now(),
            result_status="ENGAGED",
        )
        TransparencyRequest.objects.create(
            requester=self.user,
            target_phone="2250700000008",
            token="token-alliance",
            expires_at=timezone.now() + timedelta(hours=48),
        )

        summary = build_dashboard_summary(self.user)
        stat_map = {item.key: item.value for item in summary["stats"]}
        self.assertEqual(stat_map["active_alliances"], 1)
        self.assertIsNone(summary["next_action"])
