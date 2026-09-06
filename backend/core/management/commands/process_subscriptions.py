from django.core.management.base import BaseCommand

from core.subscriptions.services import process_subscriptions_daily


class Command(BaseCommand):
    help = (
        "Envoie les rappels d'expiration Premium (J-7, J-3, J-1) "
        "et désactive les avantages expirés."
    )

    def handle(self, *args, **options):
        result = process_subscriptions_daily()
        self.stdout.write(
            self.style.SUCCESS(
                f"Rappels envoyés : {result['reminders_sent']} — "
                f"Alliances expirées traitées : {result['alliances_expired']}"
            )
        )
