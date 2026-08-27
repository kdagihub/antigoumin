from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from ninja.errors import HttpError

from core.models import Declaration, Payment, User
from core.notifications.email import notify_phone_or_user_email, notify_user_by_email
from core.notifications.sms import send_verification_sms_async
from core.pricing import ServiceType
from core.utils.phone import normalize_phone
from core.utils.subscription import get_unused_payment

from .schemas import (
    DeclarationSchema,
    PartnerPreviewSchema,
    VerifyPreviewSchema,
    VerifyResultSchema,
)
from .tokens import delete_verification_token, get_declaration_id_from_token, store_verification_token


class DeclarationServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def handle_declaration_error(exc: DeclarationServiceError):
    raise HttpError(exc.status_code, exc.message)


def declaration_to_schema(request, declaration: Declaration) -> DeclarationSchema:
    from core.utils.media import build_media_url

    return DeclarationSchema(
        id=declaration.id,
        partner_phone=declaration.partner_phone,
        partner_name=declaration.partner_name,
        partner_photo=build_media_url(request, declaration.partner_photo),
        relation_type=declaration.relation_type,
        visibility=declaration.visibility,
        status=declaration.status,
        created_at=declaration.created_at,
    )


def preview_partner(phone: str) -> PartnerPreviewSchema:
    try:
        normalized_phone = normalize_phone(phone)
    except ValueError as exc:
        raise DeclarationServiceError(400, str(exc)) from exc

    return PartnerPreviewSchema(
        partner_phone=normalized_phone,
        price_fcfa=settings.SERVICE_PRICES[ServiceType.DECLARATION],
        consent_notice=(
            "La personne invitée choisira librement d'accepter ou de refuser. "
            "Aucune autre relation ni information privée ne vous sera révélée."
        ),
    )


def list_declarations(request, user: User) -> list[DeclarationSchema]:
    declarations = Declaration.objects.filter(author=user).order_by("-created_at")
    return [declaration_to_schema(request, item) for item in declarations]


def create_declaration(
    request,
    user: User,
    *,
    partner_phone: str,
    partner_name: str,
    partner_photo,
    relation_type: str = Declaration.RelationType.AMOUR,
    visibility: str = Declaration.Visibility.PUBLIC_CERTIFIED,
    payment_id: int | None = None,
) -> DeclarationSchema:
    payment = get_unused_payment(user, ServiceType.DECLARATION, payment_id=payment_id)
    if payment is None and not settings.DEBUG:
        raise DeclarationServiceError(
            402,
            "Paiement de déclaration requis (300 FCFA).",
        )

    try:
        normalized_phone = normalize_phone(partner_phone)
    except ValueError as exc:
        raise DeclarationServiceError(400, str(exc)) from exc

    partner_name = partner_name.strip()
    if not partner_name:
        raise DeclarationServiceError(400, "Le nom du partenaire est obligatoire.")

    if relation_type not in Declaration.RelationType.values:
        raise DeclarationServiceError(400, "Type de relation invalide.")
    if visibility not in Declaration.Visibility.values:
        raise DeclarationServiceError(400, "Mode de visibilité invalide.")

    content_type = getattr(partner_photo, "content_type", "")
    if content_type not in settings.ALLOWED_IMAGE_CONTENT_TYPES:
        raise DeclarationServiceError(400, "Format d'image non supporté (JPEG ou PNG).")

    if partner_photo.size > settings.MAX_UPLOAD_IMAGE_SIZE:
        raise DeclarationServiceError(400, "L'image dépasse la taille maximale autorisée.")

    with transaction.atomic():
        declaration = Declaration.objects.create(
            author=user,
            partner_phone=normalized_phone,
            partner_name=partner_name,
            partner_photo=partner_photo,
            relation_type=relation_type,
            visibility=visibility,
            status=Declaration.Status.PENDING,
            payment=payment,
        )
        if payment:
            payment.consumed = True
            payment.metadata = {**payment.metadata, "declaration_id": declaration.id}
            payment.save(update_fields=["consumed", "metadata"])
        token = store_verification_token(declaration.id)

    send_verification_sms_async(normalized_phone, token)
    verify_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/v/{token}"
    notify_user_by_email(
        user.email,
        "Votre déclaration AntiGoumin a été envoyée",
        (
            f"Votre déclaration de relation avec {partner_name} a été transmise. "
            "Votre partenaire doit l'accepter via le lien qui lui a été envoyé."
        ),
    )
    notify_phone_or_user_email(
        normalized_phone,
        "Une déclaration de relation AntiGoumin vous attend",
        (
            f"{user.full_name or user.email} vous invite à certifier une relation. "
            f"Acceptez ou refusez ici : {verify_url}"
        ),
    )
    return declaration_to_schema(request, declaration)


def preview_verification(token: str) -> VerifyPreviewSchema:
    declaration = _get_declaration_by_token(token)
    return VerifyPreviewSchema(
        partner_name=declaration.partner_name,
        author_name=declaration.author.full_name or declaration.author.email,
        relation_type=declaration.relation_type,
        visibility=declaration.visibility,
        consent_notice=(
            "En acceptant, vous certifiez cette relation. "
            + (
                "Tant qu'elle reste active, les utilisateurs pourront vérifier que votre "
                "numéro possède le statut « En couple », sans voir votre identité, le nombre "
                "de relations ni leur historique. Vous pourrez retirer cette consultabilité "
                "à tout moment."
                if declaration.visibility == Declaration.Visibility.PUBLIC_CERTIFIED
                else "Cette relation restera privée et ne produira aucun statut public."
            )
        ),
        status=declaration.status,
        expires_in_minutes=int(settings.VERIFICATION_TOKEN_TTL.total_seconds() // 60),
    )


def process_verification(token: str, *, accept: bool) -> VerifyResultSchema:
    declaration = _get_declaration_by_token(token)

    if declaration.status != Declaration.Status.PENDING:
        raise DeclarationServiceError(
            400,
            f"Cette déclaration est déjà {declaration.status.lower()}.",
        )

    declaration.status = Declaration.Status.VERIFIED if accept else Declaration.Status.REJECTED
    update_fields = ["status"]
    if accept:
        declaration.verified_at = timezone.now()
        update_fields.append("verified_at")
        partner = User.objects.filter(
            phone_number=declaration.partner_phone,
            is_active=True,
        ).first()
        if partner:
            declaration.accepted_by = partner
            update_fields.append("accepted_by")
            if declaration.visibility == Declaration.Visibility.PUBLIC_CERTIFIED:
                partner.is_status_searchable = True
                partner.save(update_fields=["is_status_searchable"])
        if declaration.visibility == Declaration.Visibility.PUBLIC_CERTIFIED:
            declaration.author.is_status_searchable = True
            declaration.author.save(update_fields=["is_status_searchable"])
    declaration.save(update_fields=update_fields)
    delete_verification_token(token)

    message = (
        (
            "Relation acceptée et statut certifié public activé."
            if declaration.visibility == Declaration.Visibility.PUBLIC_CERTIFIED
            else "Relation privée acceptée."
        )
        if accept
        else "Déclaration refusée."
    )
    return VerifyResultSchema(
        declaration_id=declaration.id,
        status=declaration.status,
        message=message,
    )


def end_declaration(user: User, declaration_id: int) -> VerifyResultSchema:
    try:
        declaration = Declaration.objects.select_related(
            "author",
            "accepted_by",
        ).get(id=declaration_id)
    except Declaration.DoesNotExist as exc:
        raise DeclarationServiceError(404, "Relation introuvable.") from exc

    normalized_user_phone = ""
    if user.phone_number:
        try:
            normalized_user_phone = normalize_phone(user.phone_number)
        except ValueError:
            normalized_user_phone = ""
    is_party = (
        declaration.author_id == user.id
        or declaration.accepted_by_id == user.id
        or (
            normalized_user_phone
            and normalized_user_phone == declaration.partner_phone
        )
    )
    if not is_party:
        raise DeclarationServiceError(
            403,
            "Seules les parties peuvent mettre fin à cette relation.",
        )
    if declaration.status != Declaration.Status.VERIFIED:
        raise DeclarationServiceError(400, "Cette relation n'est pas active.")

    declaration.status = Declaration.Status.ENDED
    declaration.ended_at = timezone.now()
    declaration.save(update_fields=["status", "ended_at"])

    parties = [declaration.author]
    if declaration.accepted_by:
        parties.append(declaration.accepted_by)
    for party in parties:
        still_public = Declaration.objects.filter(
            (
                models.Q(author=party)
                | models.Q(accepted_by=party)
            ),
            status=Declaration.Status.VERIFIED,
            visibility=Declaration.Visibility.PUBLIC_CERTIFIED,
            ended_at__isnull=True,
        ).exists()
        if still_public and not party.is_status_searchable:
            party.is_status_searchable = True
            party.save(update_fields=["is_status_searchable"])

    return VerifyResultSchema(
        declaration_id=declaration.id,
        status=declaration.status,
        message=(
            "La relation certifiée a pris fin. L'autre partie peut être informée "
            "de cette fin, sans motif ni détail sur un autre statut."
        ),
    )


def _get_declaration_by_token(token: str) -> Declaration:
    declaration_id = get_declaration_id_from_token(token)
    if declaration_id is None:
        raise DeclarationServiceError(404, "Lien de vérification invalide ou expiré.")

    try:
        return Declaration.objects.select_related("author").get(id=declaration_id)
    except Declaration.DoesNotExist as exc:
        raise DeclarationServiceError(404, "Déclaration introuvable.") from exc
