from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Alliance,
    Declaration,
    InAppNotification,
    Payment,
    PhoneVerificationAccess,
    TransparencyRequest,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ("email",)
    list_display = (
        "email",
        "auth_provider",
        "is_active",
        "subscription_end_date",
        "alliance_badge_enabled",
        "is_status_searchable",
        "email_verified_at",
        "phone_verified_at",
        "created_at",
    )
    list_filter = (
        "is_active",
        "auth_provider",
        "alliance_badge_enabled",
        "is_status_searchable",
    )
    search_fields = ("email", "first_name", "last_name", "phone_number")
    filter_horizontal = ()

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Profil",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "email_verified_at",
                    "phone_verified_at",
                    "is_status_searchable",
                )
            },
        ),
        ("OAuth", {"fields": ("auth_provider", "google_id")}),
        ("Abonnement", {"fields": ("subscription_end_date", "alliance_badge_enabled")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "partner_phone",
        "partner_name",
        "relation_type",
        "visibility",
        "status",
        "created_at",
    )
    list_filter = ("status", "relation_type", "visibility")
    search_fields = ("partner_phone", "partner_name", "author__email")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "user",
        "service_type",
        "amount",
        "status",
        "consumed",
        "created_at",
    )
    list_filter = ("status", "service_type", "consumed")
    search_fields = ("reference", "user__email")


@admin.register(PhoneVerificationAccess)
class PhoneVerificationAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "expires_at", "created_at")
    search_fields = ("phone", "user__email")


@admin.register(TransparencyRequest)
class TransparencyRequestAdmin(admin.ModelAdmin):
    list_display = ("requester", "target_phone", "status", "expires_at", "created_at")
    list_filter = ("status",)
    search_fields = ("target_phone", "requester__email", "token")


@admin.register(Alliance)
class AllianceAdmin(admin.ModelAdmin):
    list_display = (
        "initiator",
        "partner",
        "status",
        "subscription_end_date",
        "created_at",
    )
    list_filter = ("status", "initiator_badge_public", "partner_badge_public")
    search_fields = ("initiator__email", "partner__email")


@admin.register(InAppNotification)
class InAppNotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "type", "read_at", "created_at")
    list_filter = ("type", "read_at")
    search_fields = ("recipient__email", "title", "message")
