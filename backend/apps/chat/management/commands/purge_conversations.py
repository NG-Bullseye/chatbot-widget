"""Loescht abgelaufene Chat-Verlaeufe (DSGVO-Speicherbegrenzung, Art. 5 Abs. 1
lit. e). Taeglich per Cron ausfuehren, z.B. auf Railway:

    python manage.py purge_conversations

Frist kommt aus CONVERSATION_RETENTION_DAYS (Env, Default 90 Tage). Massgeblich
ist `updated_at` -- eine Conversation, in der noch geschrieben wird, bleibt
erhalten. Messages werden per FK-CASCADE mitgeloescht.
"""
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.chat.models import Conversation


class Command(BaseCommand):
    help = "Loescht Chat-Verlaeufe aelter als CONVERSATION_RETENTION_DAYS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Aufbewahrungsfrist in Tagen (ueberschreibt CONVERSATION_RETENTION_DAYS).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Nur zaehlen, was geloescht wuerde, nichts loeschen.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        if days is None:
            days = settings.CONVERSATION_RETENTION_DAYS
        cutoff = timezone.now() - timedelta(days=days)

        expired = Conversation.objects.filter(updated_at__lt=cutoff)
        count = expired.count()

        if options["dry_run"]:
            self.stdout.write(
                f"[dry-run] {count} Conversation(s) aelter als {days} Tage "
                f"(vor {cutoff.date()}) wuerden geloescht."
            )
            return

        expired.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"{count} Conversation(s) aelter als {days} Tage geloescht "
                f"(Stichtag {cutoff.date()})."
            )
        )
