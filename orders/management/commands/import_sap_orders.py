from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser

from orders.services import sync_sap_orders


class Command(BaseCommand):
    help = "Importă comenzi din SAP (mock sau fișier JSON)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--file", dest="file_path", help="Cale către fișier JSON local", default=None)
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validează fără a salva în baza de date",
            default=False,
        )

    def handle(self, *args, **options):  # type: ignore[no-untyped-def]
        file_path = options.get("file_path")
        dry_run = options.get("dry_run", False)
        self.stdout.write(self.style.NOTICE("Pornesc importul de comenzi SAP..."))
        result = sync_sap_orders(file_path=file_path, dry_run=dry_run)
        self.stdout.write(self.style.SUCCESS(f"Comenzi procesate cu succes: {result['success']}"))
        if result["errors"]:
            self.stdout.write(self.style.ERROR("Erori întâlnite:"))
            for err in result["errors"]:
                self.stdout.write(f" - {err}")


