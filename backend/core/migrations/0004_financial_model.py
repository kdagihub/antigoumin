import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_user_permissions"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="alliance_badge_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="declaration",
            name="relation_type",
            field=models.CharField(
                choices=[
                    ("AMOUR", "Amour"),
                    ("FLIRT", "Flirt"),
                    ("FIANCE", "Fiançailles"),
                    ("MARIAGE", "Mariage"),
                ],
                default="AMOUR",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="payment",
            name="consumed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="payment",
            name="metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="payment",
            name="service_type",
            field=models.CharField(
                choices=[
                    ("VERIFICATION", "Vérification"),
                    ("DECLARATION", "Déclaration"),
                    ("FIDELITY_TEST", "Test de fidélité"),
                    ("ALLIANCE_VIP", "Alliance VIP"),
                ],
                default="ALLIANCE_VIP",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="declaration",
            name="payment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="declarations",
                to="core.payment",
            ),
        ),
        migrations.CreateModel(
            name="PhoneVerificationAccess",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone", models.CharField(max_length=15)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "payment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="verification_accesses",
                        to="core.payment",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="verification_accesses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["user", "phone", "expires_at"],
                        name="core_phonev_user_id_6f0b0d_idx",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="FidelityTest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target_phone", models.CharField(max_length=15)),
                ("token", models.CharField(max_length=64, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("PASSED", "Passed"),
                            ("FAILED", "Failed"),
                            ("EXPIRED", "Expired"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("submitted_partner_name", models.CharField(blank=True, max_length=100)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "initiator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fidelity_tests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "payment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fidelity_tests",
                        to="core.payment",
                    ),
                ),
            ],
        ),
    ]
