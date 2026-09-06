from datetime import timedelta
from io import BytesIO
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from core.declarations.services import DeclarationServiceError, create_declaration
from core.fidelity_tests.services import (
    TransparencyRequestServiceError,
    create_transparency_request,
)
from core.models import (
    Alliance,
    Declaration,
    Payment,
    PhoneVerificationAccess,
    TransparencyRequest,
    User,
)
from core.pricing import ServiceType
from core.search.services import search_by_phone
from core.subscriptions.quotas import (
    can_use_vip_quota,
    count_vip_quota_usage,
    vip_quota_remaining,
)
from core.utils.phone import normalize_phone


class VipQuotaTestMixin:
    def setUp(self):
        self.initiator = User.objects.create_user(
            email="vip-initiator@example.com",
            password="strong-password",
            phone_number="2250700000101",
            email_verified_at=timezone.now(),
        )
        self.partner = User.objects.create_user(
            email="vip-partner@example.com",
            password="strong-password",
            phone_number="2250700000102",
            email_verified_at=timezone.now(),
        )
        self.declaration = Declaration.objects.create(
            author=self.initiator,
            accepted_by=self.partner,
            partner_phone=self.partner.phone_number,
            partner_name="Partenaire",
            partner_photo="declarations/vip-quota.jpg",
            status=Declaration.Status.VERIFIED,
            visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
            verified_at=timezone.now(),
        )
        payment = Payment.objects.create(
            user=self.initiator,
            service_type=Payment.ServiceType.ALLIANCE_VIP,
            amount=1200,
            reference="vip-quota-alliance",
            status=Payment.Status.SUCCESS,
            consumed=True,
        )
        self.alliance = Alliance.objects.create(
            initiator=self.initiator,
            partner=self.partner,
            declaration=self.declaration,
            payment=payment,
            status=Alliance.Status.ACTIVE,
            initiator_consented_at=timezone.now(),
            partner_consented_at=timezone.now(),
            subscription_end_date=timezone.now() + timedelta(days=30),
        )
        self.initiator.subscription_end_date = self.alliance.subscription_end_date
        self.partner.subscription_end_date = self.alliance.subscription_end_date
        self.initiator.save(update_fields=["subscription_end_date"])
        self.partner.save(update_fields=["subscription_end_date"])


class VipQuotaStatusTests(VipQuotaTestMixin, TestCase):
    def test_vip_user_has_full_quotas(self):
        self.assertEqual(vip_quota_remaining(self.initiator, ServiceType.VERIFICATION), 5)
        self.assertEqual(vip_quota_remaining(self.initiator, ServiceType.DECLARATION), 1)
        self.assertEqual(
            vip_quota_remaining(self.initiator, ServiceType.TRANSPARENCY_REQUEST),
            1,
        )
        self.assertTrue(can_use_vip_quota(self.initiator, ServiceType.VERIFICATION))

    def test_non_vip_user_has_no_quota(self):
        outsider = User.objects.create_user(
            email="outsider@example.com",
            password="strong-password",
        )
        self.assertEqual(vip_quota_remaining(outsider, ServiceType.VERIFICATION), 0)
        self.assertFalse(can_use_vip_quota(outsider, ServiceType.VERIFICATION))


class VipVerificationQuotaTests(VipQuotaTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.target = User.objects.create_user(
            email="target@example.com",
            password="strong-password",
            phone_number="2250700000200",
            is_status_searchable=True,
        )

    def test_vip_search_uses_included_quota_without_payment(self):
        result = search_by_phone(None, self.initiator, self.target.phone_number)
        self.assertNotEqual(result.certified_status, "PAYMENT_REQUIRED")
        self.assertTrue(result.included_in_vip)
        self.assertEqual(result.vip_quota_remaining, 4)
        self.assertEqual(count_vip_quota_usage(self.initiator, ServiceType.VERIFICATION), 1)

    def test_vip_search_exhausted_requires_payment(self):
        for index in range(5):
            phone = f"22507000003{index:02d}"
            User.objects.create_user(
                email=f"target{index}@example.com",
                password="strong-password",
                phone_number=phone,
                is_status_searchable=True,
            )
            search_by_phone(None, self.initiator, phone)

        result = search_by_phone(None, self.initiator, self.target.phone_number)
        self.assertEqual(result.certified_status, "PAYMENT_REQUIRED")
        self.assertEqual(result.vip_quota_remaining, 0)

    def test_paid_verification_does_not_consume_vip_quota(self):
        phone = normalize_phone(self.target.phone_number)
        payment = Payment.objects.create(
            user=self.initiator,
            service_type=Payment.ServiceType.VERIFICATION,
            amount=200,
            reference="paid-verify-vip",
            status=Payment.Status.SUCCESS,
        )
        PhoneVerificationAccess.objects.create(
            user=self.initiator,
            phone=phone,
            payment=payment,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        search_by_phone(None, self.initiator, phone)
        self.assertEqual(count_vip_quota_usage(self.initiator, ServiceType.VERIFICATION), 0)


class VipDeclarationQuotaTests(VipQuotaTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.request = MagicMock()
        self.request.build_absolute_uri.side_effect = lambda path: f"https://test.local{path}"

    @patch("core.declarations.services.send_verification_sms_async")
    def test_vip_declaration_without_payment(self, _send_sms):
        photo = SimpleUploadedFile(
            "partner.jpg",
            BytesIO(b"fake-image").read(),
            content_type="image/jpeg",
        )
        result = create_declaration(
            self.request,
            self.initiator,
            partner_phone="2250700000300",
            partner_name="Awa",
            partner_photo=photo,
        )
        self.assertEqual(result.status, "PENDING")
        declaration = Declaration.objects.get(id=result.id)
        self.assertIsNone(declaration.payment_id)
        self.assertEqual(count_vip_quota_usage(self.initiator, ServiceType.DECLARATION), 1)
        self.assertEqual(vip_quota_remaining(self.initiator, ServiceType.DECLARATION), 0)

    @patch("core.declarations.services.send_verification_sms_async")
    def test_second_vip_declaration_requires_payment(self, _send_sms):
        photo = SimpleUploadedFile(
            "partner.jpg",
            BytesIO(b"fake-image").read(),
            content_type="image/jpeg",
        )
        create_declaration(
            self.request,
            self.initiator,
            partner_phone="2250700000301",
            partner_name="Awa",
            partner_photo=photo,
        )
        with self.assertRaises(DeclarationServiceError):
            create_declaration(
                self.request,
                self.initiator,
                partner_phone="2250700000302",
                partner_name="Kofi",
                partner_photo=photo,
            )


class VipTransparencyQuotaTests(VipQuotaTestMixin, TestCase):
    @patch("core.fidelity_tests.services.send_transparency_request_sms_async")
    def test_vip_transparency_without_payment(self, _send_sms):
        result = create_transparency_request(
            None,
            self.initiator,
            target_phone="2250700000400",
        )
        self.assertEqual(result.status, "PENDING")
        request = TransparencyRequest.objects.get(id=result.id)
        self.assertIsNone(request.payment_id)
        self.assertEqual(
            count_vip_quota_usage(self.initiator, ServiceType.TRANSPARENCY_REQUEST),
            1,
        )

    @patch("core.fidelity_tests.services.send_transparency_request_sms_async")
    def test_second_vip_transparency_requires_payment(self, _send_sms):
        create_transparency_request(
            None,
            self.initiator,
            target_phone="2250700000401",
        )
        with self.assertRaises(TransparencyRequestServiceError):
            create_transparency_request(
                None,
                self.initiator,
                target_phone="2250700000402",
            )
