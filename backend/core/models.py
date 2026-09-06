from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class AuthProvider(models.TextChoices):
        EMAIL = "email", "Email"
        GOOGLE = "google", "Google"
        APPLE = "apple", "Apple"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    is_status_searchable = models.BooleanField(
        default=False,
        help_text="Autorise la consultation publique du statut certifié.",
    )
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
    )
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    alliance_badge_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["phone_number"],
                condition=~models.Q(phone_number=""),
                name="unique_nonempty_phone_number",
            ),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def phone_verified(self) -> bool:
        return self.phone_verified_at is not None

    @property
    def is_fully_verified(self) -> bool:
        return self.email_verified or self.phone_verified


class Declaration(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"
        ENDED = "ENDED", "Ended"

    class RelationType(models.TextChoices):
        AMOUR = "AMOUR", "Amoureuse"
        FLIRT = "FLIRT", "Flirt"
        FIANCE = "FIANCE", "Fiançailles"
        MARIAGE = "MARIAGE", "Mariage"

    class Visibility(models.TextChoices):
        PRIVATE = "PRIVATE", "Relation privée"
        PUBLIC_CERTIFIED = "PUBLIC_CERTIFIED", "Statut certifié public"

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="declarations_made",
    )
    partner_phone = models.CharField(max_length=15)
    partner_name = models.CharField(max_length=100)
    partner_photo = models.ImageField(upload_to="declarations/")
    relation_type = models.CharField(
        max_length=20,
        choices=RelationType.choices,
        default=RelationType.AMOUR,
    )
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
    )
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="declarations_accepted",
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment = models.ForeignKey(
        "Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="declarations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.email} -> {self.partner_phone} ({self.status})"


class Payment(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    class ServiceType(models.TextChoices):
        VERIFICATION = "VERIFICATION", "Vérification"
        DECLARATION = "DECLARATION", "Déclaration"
        TRANSPARENCY_REQUEST = "TRANSPARENCY_REQUEST", "Demande de Transparence"
        FIDELITY_TEST = "FIDELITY_TEST", "Test de fidélité (historique)"
        ALLIANCE_VIP = "ALLIANCE_VIP", "Alliance VIP"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)
    amount = models.IntegerField(default=200)
    reference = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices)
    consumed = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.service_type} - {self.status}"


class PhoneVerificationAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verification_accesses")
    phone = models.CharField(max_length=15)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="verification_accesses")
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Horodatage de la consultation facturée (usage unique par paiement).",
    )
    result_status = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "phone", "expires_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} → {self.phone}"


class TransparencyRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REFUSED = "REFUSED", "Refused"
        EXPIRED = "EXPIRED", "Expired"
        BLOCKED = "BLOCKED", "Blocked"
        REPORTED = "REPORTED", "Reported"

    class DeclaredStatus(models.TextChoices):
        ENGAGED = "ENGAGED", "En couple"
        AVAILABLE = "AVAILABLE", "Disponible"
        PREFER_NOT_TO_ANSWER = "PREFER_NOT_TO_ANSWER", "Préfère ne pas répondre"

    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transparency_requests",
    )
    target_phone = models.CharField(max_length=15)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transparency_requests",
    )
    token = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    declared_status = models.CharField(
        max_length=30,
        choices=DeclaredStatus.choices,
        blank=True,
    )
    declared_partner_name = models.CharField(max_length=100, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["requester", "target_phone", "status"]),
            models.Index(fields=["target_phone", "created_at"]),
        ]

    def __str__(self):
        return f"Demande {self.requester_id} → {self.target_phone} ({self.status})"


class Alliance(models.Model):
    class Status(models.TextChoices):
        PENDING_PARTNER = "PENDING_PARTNER", "En attente du partenaire"
        ACTIVE = "ACTIVE", "Active"
        REFUSED = "REFUSED", "Refusée"
        ENDED = "ENDED", "Terminée"

    declaration = models.OneToOneField(
        Declaration,
        on_delete=models.CASCADE,
        related_name="alliance",
    )
    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="alliances_started",
    )
    partner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="alliances_received",
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="alliance",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PARTNER,
    )
    initiator_consented_at = models.DateTimeField()
    partner_consented_at = models.DateTimeField(null=True, blank=True)
    initiator_badge_public = models.BooleanField(default=False)
    partner_badge_public = models.BooleanField(default=False)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["initiator", "status"]),
            models.Index(fields=["partner", "status"]),
        ]

    def __str__(self):
        return f"Alliance {self.initiator_id} ↔ {self.partner_id} ({self.status})"


class InAppNotification(models.Model):
    class Type(models.TextChoices):
        PARTNER_VISIBILITY_DISABLED = (
            "PARTNER_VISIBILITY_DISABLED",
            "Visibilité du partenaire désactivée",
        )
        PARTNER_DECLARED_BY_OTHER = (
            "PARTNER_DECLARED_BY_OTHER",
            "Partenaire déclaré par un tiers",
        )
        SUBSCRIPTION_EXPIRING = (
            "SUBSCRIPTION_EXPIRING",
            "Abonnement Premium bientôt expiré",
        )
        SUBSCRIPTION_EXPIRED = (
            "SUBSCRIPTION_EXPIRED",
            "Abonnement Premium expiré",
        )
        SUBSCRIPTION_RENEWED = (
            "SUBSCRIPTION_RENEWED",
            "Abonnement Premium renouvelé",
        )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="in_app_notifications",
    )
    type = models.CharField(max_length=40, choices=Type.choices)
    title = models.CharField(max_length=120)
    message = models.CharField(max_length=500)
    metadata = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "read_at", "created_at"]),
        ]

    def __str__(self):
        return f"Notification {self.type} → {self.recipient_id}"
