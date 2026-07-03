import logging

from django.core.management import BaseCommand

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_raw_to_db import \
    FastAcquisition1To3GHzRawToDB

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'test launch without celery'

    def handle(self, *args, **options):
        logger.info("=========================================")

        settings = FastAcquisition1To3GHzSettings.load()
        raw_to_db = FastAcquisition1To3GHzRawToDB(settings)
        added_count = raw_to_db.execute()

        logger.info(f"Scanning success. Added files: {added_count}")
        logger.info("=========================================")