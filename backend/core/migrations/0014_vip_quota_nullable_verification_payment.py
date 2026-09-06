from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_subscription_notification_types"),
    ]

    operations = [
        migrations.AlterField(
            model_name="phoneverificationaccess",
            name="payment",
            field=models.ForeignKey(
                blank=True,
                help_text="Null lorsque la consultation est incluse dans le forfait Alliance VIP.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="verification_accesses",
                to="core.payment",
            ),
        ),
    ]
