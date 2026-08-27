from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from ninja.errors import HttpError

from geniuspay import (
    GeniusPayAuthError,
    GeniusPayClient,
    GeniusPayError,
    GeniusPayNetworkError,
    GeniusPayNotFoundError,
    GeniusPayValidationError,
)

from core.auth.deps import VERIFICATION_REQUIRED_MESSAGE
from core.models import Payment, PhoneVerificationAccess, User
from core.alliances.services import AllianceServiceError, create_pending_alliance
from core.notifications.email import notify_user_by_email
from core.pricing import SERVICE_PRICES, ServiceType
from core.utils.phone import normalize_phone, to_e164

from .schemas import PaymentWebhookResponseSchema


class PaymentServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def handle_payment_error(exc: PaymentServiceError):
    raise HttpError(exc.status_code, exc.message)


def verify_webhook_secret(request) -> None:
    expected = settings.PAYMENT_WEBHOOK_SECRET
    if not expected:
        if settings.DEBUG:
            return
        raise PaymentServiceError(500, "Webhook de paiement non configuré.")

    received = request.headers.get("X-Webhook-Secret", "")
    if received != expected:
        raise PaymentServiceError(401, "Secret webhook invalide.")


def process_payment_webhook(
    *,
    reference: str,
    status: str,
    service_type: str,
    amount: int,
    user_id: int,
    metadata: dict | None = None,
) -> PaymentWebhookResponseSchema:
    reference = reference.strip()
    metadata = metadata or {}

    if not reference:
        raise PaymentServiceError(400, "La référence de paiement est obligatoire.")

    if Payment.objects.filter(reference=reference).exists():
        raise PaymentServiceError(409, "Cette référence de paiement a déjà été traitée.")

    try:
        service = ServiceType(service_type)
    except ValueError as exc:
        raise PaymentServiceError(400, "Type de service invalide.") from exc

    expected_amount = SERVICE_PRICES[service]
    if amount != expected_amount:
        raise PaymentServiceError(
            400,
            f"Montant incorrect pour {service.value} : attendu {expected_amount} FCFA.",
        )

    if status not in {Payment.Status.SUCCESS, Payment.Status.FAILED}:
        raise PaymentServiceError(400, "Statut de paiement invalide.")

    try:
        user = User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist as exc:
        raise PaymentServiceError(404, "Utilisateur introuvable.") from exc

    if status == Payment.Status.SUCCESS and not user.is_fully_verified:
        raise PaymentServiceError(403, VERIFICATION_REQUIRED_MESSAGE)

    subscription_end_date = None
    message = "Paiement enregistré."

    with transaction.atomic():
        payment = Payment.objects.create(
            user=user,
            service_type=service.value,
            amount=amount,
            reference=reference,
            status=status,
            metadata=metadata,
            consumed=False,
        )

        if status != Payment.Status.SUCCESS:
            message = "Paiement échoué."
        elif service == ServiceType.ALLIANCE_VIP:
            declaration_id = metadata.get("declaration_id")
            if not declaration_id:
                raise PaymentServiceError(
                    400,
                    "La relation certifiée est obligatoire pour créer une Alliance.",
                )
            try:
                alliance = create_pending_alliance(
                    user,
                    payment,
                    declaration_id=int(declaration_id),
                )
            except (AllianceServiceError, TypeError, ValueError) as exc:
                message_text = (
                    exc.message
                    if isinstance(exc, AllianceServiceError)
                    else "Identifiant de relation invalide."
                )
                raise PaymentServiceError(400, message_text) from exc
            payment.consumed = True
            payment.metadata = {**payment.metadata, "alliance_id": alliance.id}
            payment.save(update_fields=["consumed", "metadata"])
            message = (
                "Paiement validé. L'Alliance reste en attente du consentement "
                "du partenaire ; aucun badge n'est encore publié."
            )
        elif service == ServiceType.VERIFICATION:
            phone = metadata.get("phone", "")
            try:
                normalized_phone = normalize_phone(phone)
            except ValueError as exc:
                raise PaymentServiceError(400, str(exc)) from exc
            PhoneVerificationAccess.objects.create(
                user=user,
                phone=normalized_phone,
                payment=payment,
                expires_at=timezone.now()
                + timedelta(hours=settings.VERIFICATION_ACCESS_TTL_HOURS),
            )
            message = "Vérification débloquée pour ce numéro."
        elif service == ServiceType.DECLARATION:
            message = "Paiement déclaration validé. Vous pouvez créer votre déclaration."
        elif service == ServiceType.TRANSPARENCY_REQUEST:
            message = (
                "Paiement Demande de Transparence validé. "
                "Vous pouvez envoyer votre invitation identifiable."
            )

    if status == Payment.Status.SUCCESS:
        notify_user_by_email(
            user.email,
            "Paiement AntiGoumin confirmé",
            message,
        )

    return PaymentWebhookResponseSchema(
        ok=True,
        service_type=service.value,
        subscription_end_date=subscription_end_date,
        message=message,
    )


SERVICE_LABELS = {
    ServiceType.VERIFICATION: "Vérification de statut",
    ServiceType.DECLARATION: "Déclaration de relation",
    ServiceType.TRANSPARENCY_REQUEST: "Demande de Transparence",
    ServiceType.ALLIANCE_VIP: "Alliance Digitale VIP",
}


def _geniuspay_status(raw_status: str) -> str:
    value = (raw_status or "").lower()
    if value in {"completed", "paid", "success"}:
        return Payment.Status.SUCCESS
    if value in {"failed", "cancelled", "canceled", "expired", "refunded"}:
        return Payment.Status.FAILED
    return ""


def extract_geniuspay_event(raw_event: dict | None, transaction=None):
    payload = raw_event if isinstance(raw_event, dict) else {}
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    inner = data.get("transaction") if isinstance(data.get("transaction"), dict) else data
    metadata: dict = {}
    if transaction is not None and getattr(transaction, "metadata", None):
        metadata.update(transaction.metadata)
    if isinstance(inner.get("metadata"), dict):
        metadata.update(inner["metadata"])
    if isinstance(data.get("metadata"), dict):
        metadata.update(data["metadata"])
    reference = (
        getattr(transaction, "reference", None)
        or inner.get("reference")
        or data.get("reference")
        or payload.get("reference")
    )
    amount = inner.get("amount")
    if amount is None:
        amount = data.get("amount")
    if amount is None and transaction is not None:
        amount = getattr(transaction, "amount", 0)
    status = inner.get("status") or data.get("status") or getattr(transaction, "status", "")
    return {
        "reference": str(reference or "").strip(),
        "amount": int(float(amount or 0)),
        "status": str(status or ""),
        "metadata": metadata,
    }


def apply_geniuspay_event(raw_event: dict | None, transaction=None) -> None:
    extracted = extract_geniuspay_event(raw_event, transaction)
    mapped_status = _geniuspay_status(extracted["status"])
    if not mapped_status or not extracted["reference"]:
        return
    metadata = extracted["metadata"] or {}
    try:
        user_id = int(metadata.get("user_id"))
        service = ServiceType(str(metadata.get("service_type", "")))
    except (TypeError, ValueError):
        return
    extra = {
        key: value
        for key, value in metadata.items()
        if key not in {"user_id", "service_type"}
    }
    try:
        process_payment_webhook(
            reference=extracted["reference"],
            status=mapped_status,
            service_type=service.value,
            amount=SERVICE_PRICES[service],
            user_id=user_id,
            metadata=extra,
        )
    except PaymentServiceError:
        return


def create_checkout(
    user: User,
    *,
    service_type: str,
    phone: str = "",
    declaration_id: int | None = None,
):
    try:
        service = ServiceType(service_type)
    except ValueError as exc:
        raise PaymentServiceError(400, "Type de service invalide.") from exc

    amount = SERVICE_PRICES[service]
    if amount < 200:
        raise PaymentServiceError(
            400,
            "GeniusPay refuse les montants inférieurs à 200 FCFA. "
            "Le tarif de ce service doit être ajusté.",
        )

    metadata: dict[str, str | int] = {
        "user_id": user.id,
        "service_type": service.value,
    }
    if service == ServiceType.VERIFICATION:
        if not phone:
            raise PaymentServiceError(
                400,
                "Le numéro à vérifier est obligatoire pour ce paiement.",
            )
        try:
            metadata["phone"] = normalize_phone(phone)
        except ValueError as exc:
            raise PaymentServiceError(400, str(exc)) from exc
    if service == ServiceType.ALLIANCE_VIP:
        if not declaration_id:
            raise PaymentServiceError(
                400,
                "La relation certifiée est obligatoire pour créer une Alliance.",
            )
        metadata["declaration_id"] = int(declaration_id)

    frontend = settings.FRONTEND_BASE_URL.rstrip("/")
    customer = {
        "name": user.full_name or user.email,
        "email": user.email,
        "country": "CI",
    }
    if user.phone_number:
        customer["phone"] = to_e164(user.phone_number)

    try:
        client = GeniusPayClient()
        payment = client.payments.create(
            amount=amount,
            description=f"AntiGoumin — {SERVICE_LABELS[service]}",
            customer=customer,
            success_url=f"{frontend}/paiement/succes",
            error_url=f"{frontend}/paiement/erreur",
            metadata=metadata,
        )
    except GeniusPayValidationError as exc:
        raise PaymentServiceError(400, str(exc)) from exc
    except GeniusPayAuthError as exc:
        raise PaymentServiceError(502, "Clés GeniusPay invalides.") from exc
    except GeniusPayNetworkError as exc:
        raise PaymentServiceError(503, "GeniusPay est temporairement indisponible.") from exc
    except GeniusPayError as exc:
        raise PaymentServiceError(502, str(exc)) from exc

    checkout_url = payment.checkout_url or payment.payment_url
    if not checkout_url:
        raise PaymentServiceError(502, "GeniusPay n'a pas renvoyé d'URL de paiement.")
    return {
        "checkout_url": checkout_url,
        "reference": payment.reference,
        "amount": amount,
        "service_type": service.value,
    }


def get_unused_payment_for_user(user: User, service_type: str):
    try:
        service = ServiceType(service_type)
    except ValueError as exc:
        raise PaymentServiceError(400, "Type de service invalide.") from exc
    payment = (
        Payment.objects.filter(
            user=user,
            service_type=service.value,
            status=Payment.Status.SUCCESS,
            consumed=False,
        )
        .order_by("-created_at")
        .first()
    )
    return {
        "payment_id": payment.id if payment else None,
        "service_type": service.value,
    }


def get_checkout_status(user: User, reference: str):
    def serialize(payment: Payment) -> dict:
        phone = ""
        if payment.service_type == ServiceType.VERIFICATION.value:
            phone = str((payment.metadata or {}).get("phone", ""))
        payment_id = (
            payment.id
            if payment.status == Payment.Status.SUCCESS and not payment.consumed
            else None
        )
        return {
            "reference": payment.reference,
            "status": payment.status,
            "service_type": payment.service_type,
            "credited": payment.status == Payment.Status.SUCCESS,
            "message": (
                "Paiement confirmé."
                if payment.status == Payment.Status.SUCCESS
                else "Paiement non abouti."
            ),
            "phone": phone,
            "payment_id": payment_id,
        }

    local = Payment.objects.filter(reference=reference, user=user).first()
    if local:
        return serialize(local)

    try:
        remote = GeniusPayClient().payments.retrieve(reference)
    except GeniusPayNotFoundError as exc:
        raise PaymentServiceError(404, "Paiement introuvable.") from exc
    except GeniusPayError as exc:
        raise PaymentServiceError(502, str(exc)) from exc

    if remote.is_paid:
        apply_geniuspay_event(
            {
                "data": {
                    "reference": remote.reference,
                    "amount": remote.amount,
                    "status": remote.status,
                    "metadata": remote.metadata or {},
                }
            }
        )
        local = Payment.objects.filter(reference=reference, user=user).first()
        if local:
            return serialize(local)

    return {
        "reference": remote.reference,
        "status": remote.status,
        "service_type": (remote.metadata or {}).get("service_type", ""),
        "credited": False,
        "message": (
            "Paiement encore en attente. S'il a réussi, le webhook le confirmera sous peu."
            if remote.is_pending
            else "Paiement non abouti."
        ),
        "phone": str((remote.metadata or {}).get("phone", "")),
        "payment_id": None,
    }
