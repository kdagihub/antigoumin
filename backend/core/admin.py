from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Declaration, Payment, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ("email",)
    list_display = (
        "email",
        "auth_provider",
        "is_active",
        "subscription_end_date",
        "created_at",
    )
    list_filter = ("is_active", "auth_provider")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    filter_horizontal = ()

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profil", {"fields": ("first_name", "last_name", "phone_number")}),
        ("OAuth", {"fields": ("auth_provider", "google_id")}),
        ("Abonnement", {"fields": ("subscription_end_date",)}),
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
    list_display = ("author", "partner_phone", "partner_name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("partner_phone", "partner_name", "author__email")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reference", "user__email")
