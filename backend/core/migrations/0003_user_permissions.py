from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0002_user_email_oauth"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_superuser",
            field=models.BooleanField(
                default=False,
                help_text="Indique que l'utilisateur possède toutes les permissions sans les assigner explicitement.",
                verbose_name="statut superutilisateur",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(
                default=False,
                help_text="Indique si l'utilisateur peut se connecter à ce site d'administration.",
                verbose_name="statut équipe",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="Les groupes auxquels appartient cet utilisateur.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groupes",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Permissions spécifiques pour cet utilisateur.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="permissions utilisateur",
            ),
        ),
    ]
