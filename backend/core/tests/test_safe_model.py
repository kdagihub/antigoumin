from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from core.alliances.services import (
    create_pending_alliance,
    decide_alliance,
    end_alliance,
)
from core.auth.services import set_status_searchability
from core.fidelity_tests.services import (
    create_transparency_request,
    respond_to_transparency_request,
)
from core.models import (
    Alliance,
    Declaration,
    InAppNotification,
    Payment,
    PhoneVerificationAccess,
    TransparencyRequest,
    User,
)
from core.search.services import search_by_phone
from core.utils.phone import normalize_phone


class SafeSearchTests(TestCase):
    def setUp(self):
        self.searcher = User.objects.create_user(
            email="searcher@example.com",
            password="strong-password",
        )

    def unlock(self, phone: str):
        phone = normalize_phone(phone)
        payment = Payment.objects.create(
            user=self.searcher,
            service_type=Payment.ServiceType.VERIFICATION,
            amount=200,
            reference=f"verify-{phone}",
            status=Payment.Status.SUCCESS,
        )
        PhoneVerificationAccess.objects.create(
            user=self.searcher,
            phone=phone,
            payment=payment,
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def test_unknown_and_private_numbers_are_indistinguishable(self):
        private_user = User.objects.create_user(
            email="private@example.com",
            password="strong-password",
            phone_number="2250700000001",
            is_status_searchable=False,
        )
        self.assertIsNotNone(private_user)
        for phone in ("+2250700000001", "+2250700000099"):
            self.unlock(phone)
            result = search_by_phone(None, self.searcher, phone)
            self.assertEqual(
                result.certified_status,
                "NOT_LISTED_OR_NOT_SEARCHABLE",
            )

    def test_public_certification_returns_only_binary_status(self):
        author = User.objects.create_user(
            email="author@example.com",
            password="strong-password",
            phone_number="2250700000002",
            is_status_searchable=True,
        )
        partner = User.objects.create_user(
            email="partner@example.com",
            password="strong-password",
            phone_number="2250700000003",
            is_status_searchable=True,
        )
        Declaration.objects.create(
            author=author,
            accepted_by=partner,
            partner_phone=partner.phone_number,
            partner_name="Partenaire",
            partner_photo="declarations/test.jpg",
            status=Declaration.Status.VERIFIED,
            visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
            verified_at=timezone.now(),
        )
        self.unlock(partner.phone_number)
        result = search_by_phone(None, self.searcher, partner.phone_number)
        self.assertEqual(result.certified_status, "ENGAGED")
        self.assertFalse(hasattr(result, "relation_count"))
        self.assertFalse(hasattr(result, "results"))


class TransparencyRequestTests(TestCase):
    @patch(
        "core.fidelity_tests.services.send_transparency_request_sms_async"
    )
    def test_request_is_identifiable_and_refusal_is_neutral(self, send_sms):
        requester = User.objects.create_user(
            email="requester@example.com",
            password="strong-password",
            first_name="Awa",
        )
        payment = Payment.objects.create(
            user=requester,
            service_type=Payment.ServiceType.TRANSPARENCY_REQUEST,
            amount=550,
            reference="transparency-1",
            status=Payment.Status.SUCCESS,
        )
        created = create_transparency_request(
            None,
            requester,
            target_phone="+2250700000010",
            payment_id=payment.id,
        )
        send_sms.assert_called_once()
        result = respond_to_transparency_request(
            TransparencyRequest.objects.get(id=created.id).token,
            action="REFUSE",
        )
        self.assertEqual(result.status, TransparencyRequest.Status.REFUSED)
        self.assertNotIn("échoué", result.message.lower())


class BilateralAllianceTests(TestCase):
    def test_payment_creates_pending_alliance_until_partner_accepts(self):
        initiator = User.objects.create_user(
            email="initiator@example.com",
            password="strong-password",
            phone_number="+2250700000020",
        )
        partner = User.objects.create_user(
            email="alliance-partner@example.com",
            password="strong-password",
            phone_number="+2250700000021",
        )
        declaration = Declaration.objects.create(
            author=initiator,
            accepted_by=partner,
            partner_phone=partner.phone_number,
            partner_name="Partenaire",
            partner_photo="declarations/alliance.jpg",
            status=Declaration.Status.VERIFIED,
            visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
            verified_at=timezone.now(),
        )
        payment = Payment.objects.create(
            user=initiator,
            service_type=Payment.ServiceType.ALLIANCE_VIP,
            amount=1200,
            reference="alliance-1",
            status=Payment.Status.SUCCESS,
        )
        alliance = create_pending_alliance(
            initiator,
            payment,
            declaration_id=declaration.id,
        )
        self.assertEqual(alliance.status, Alliance.Status.PENDING_PARTNER)
        self.assertFalse(alliance.initiator_badge_public)
        self.assertFalse(alliance.partner_badge_public)

        result = decide_alliance(partner, alliance.id, accept=True)
        self.assertEqual(result.status, Alliance.Status.ACTIVE)

        initiator.is_status_searchable = True
        initiator.save(update_fields=["is_status_searchable"])
        set_status_searchability(
            initiator,
            is_status_searchable=False,
        )
        notification = InAppNotification.objects.get(recipient=partner)
        self.assertEqual(
            notification.type,
            InAppNotification.Type.PARTNER_VISIBILITY_DISABLED,
        )
        self.assertEqual(
            notification.metadata["partner_visibility"],
            "NOT_VISIBLE",
        )

        with patch(
            "core.alliances.services.send_alliance_ended_sms_async"
        ):
            ended = end_alliance(initiator, alliance.id)
        self.assertEqual(ended.status, Alliance.Status.ENDED)
        self.assertIn("a pris fin", ended.message.lower())
        self.assertNotIn("raison", ended.message.lower())
