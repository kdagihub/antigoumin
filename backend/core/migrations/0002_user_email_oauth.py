from django.db import migrations, models


def migrate_phone_users_to_email(apps, schema_editor):
    User = apps.get_model("core", "User")
    for user in User.objects.all():
        if not getattr(user, "email", None):
            user.email = f"{user.phone_number}@legacy.antigoumin.local"
            user.save(update_fields=["email"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="auth_provider",
            field=models.CharField(
                choices=[("email", "Email"), ("google", "Google"), ("apple", "Apple")],
                default="email",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="first_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="user",
            name="google_id",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="user",
            name="last_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.RunPython(migrate_phone_users_to_email, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
