from django.core.management.base import BaseCommand

from observations.models import RawObservationFastAcquisition1To3GHz


class Command(BaseCommand):
    help = 'Clearing all tables data'

    def handle(self, *args, **options):
        count, _ = RawObservationFastAcquisition1To3GHz.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'DB has been cleared: deleted raw entries: {count}'))