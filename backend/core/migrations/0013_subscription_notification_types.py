from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_partner_declared_notification_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inappnotification",
            name="type",
            field=models.CharField(
                choices=[
                    (
                        "PARTNER_VISIBILITY_DISABLED",
                        "Visibilité du partenaire désactivée",
                    ),
                    (
                        "PARTNER_DECLARED_BY_OTHER",
                        "Partenaire déclaré par un tiers",
                    ),
                    (
                        "SUBSCRIPTION_EXPIRING",
                        "Abonnement Premium bientôt expiré",
                    ),
                    (
                        "SUBSCRIPTION_EXPIRED",
                        "Abonnement Premium expiré",
                    ),
                    (
                        "SUBSCRIPTION_RENEWED",
                        "Abonnement Premium renouvelé",
                    ),
                ],
                max_length=40,
            ),
        ),
    ]
