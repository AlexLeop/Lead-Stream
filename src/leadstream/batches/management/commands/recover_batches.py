from django.core.management.base import BaseCommand

from leadstream.batches.services import recover_stalled_work


class Command(BaseCommand):
    help = "Recupera ingestões e chunks abandonados sem repetir efeitos confirmados."

    def handle(self, *args: object, **options: object) -> None:
        del args, options
        result = recover_stalled_work()
        self.stdout.write(
            self.style.SUCCESS(
                "Recuperação concluída: "
                f"{result['ingestions_requeued']} ingestões, "
                f"{result['chunks_recovered']} leases expirados e "
                f"{result['chunks_requeued']} chunks reenfileirados."
            )
        )
