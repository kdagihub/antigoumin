from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_phone_verification_result_status"),
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
                ],
                max_length=40,
            ),
        ),
    ]
