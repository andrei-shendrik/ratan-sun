import os
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.models import RawObservationFastAcquisition1To3GHzDB
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.observation_file_filter import ObservationFileFilter
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_file_scanner import FastAcquisition1To3GHzFileScanner


class FastAcquisition1To3GHzRawFilesMonitor:
    @staticmethod
    def scan_recent_months():
        """
        Сканирует папки текущего и прошлого месяца архива сырых данных
        """
        base_dir = Path(os.environ['FAST_ACQ_1_3GHZ_BIN_ARCHIVE'])

        today = datetime.today()
        previous_month_date = today - relativedelta(months=1)

        target_dirs = [
            base_dir / str(today.year) / f"{today.month:02d}",
            base_dir / str(previous_month_date.year) / f"{previous_month_date.month:02d}"
        ]

        settings = FastAcquisition1To3GHzSettings.load()
        file_filter = ObservationFileFilter(settings.file_filters.allowed_patterns,
                                            settings.file_filters.forbidden_patterns)
        scanner = FastAcquisition1To3GHzFileScanner(file_filter)

        found_files = []
        for d in target_dirs:
            if d.exists():
                found_files.extend(list(scanner.scan(d)))

        existing_filenames = set(RawObservationFastAcquisition1To3GHzDB.objects.filter(
            filename__in=[f.name for f in found_files]
        ).values_list('filename', flat=True))

        new_files = [f for f in found_files if f.name not in existing_filenames]

        for file_path in new_files:
            parsed = FilenameParser.parse_safe(file_path.name)

            RawObservationFastAcquisition1To3GHzDB.objects.create(
                path_filename=str(file_path),
                filename=file_path.name,
                file_extension=file_path.suffix,
                datetime_obs_utc=parsed.utc if parsed else None,
                datetime_obs_local=parsed.local if parsed else None,
                object_of_observation=parsed.target if parsed else None,
                azimuth=parsed.azimuth if parsed else None
            )