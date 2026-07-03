import sys
from pathlib import Path
from django.core.management.base import BaseCommand

from observations.config.fast_acquisition_1_3ghz_settings import FastAcquisition1To3GHzSettings
from observations.models import RawObservationFastAcquisition1To3GHz
from observations.services.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_filename_parser import \
    FastAcquisition1To3GHzFilenameParser
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.observation_file_filter import ObservationFileFilter
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_file_scanner import FastAcquisition1To3GHzFileScanner


class Command(BaseCommand):
    help = 'Add raw fast acquisition 1-3 GHz observations to database'

    def add_arguments(self, parser):
        parser.add_argument('--dir', type=str, help='raw observations directory. Will be scanned recursively.')

    def handle(self, *args, **options):
        if not options['dir']:
            self.print_help('manage.py', 'raw_to_db_fast_1_3')
            sys.exit(1)

        scan_dir = Path(options['dir']).resolve()
        if not scan_dir.exists() or not scan_dir.is_dir():
            self.stderr.write(self.style.ERROR(f"Directory not found: {scan_dir}"))
            sys.exit(1)

        settings = FastAcquisition1To3GHzSettings.load()
        raw_base_path = settings.bin_archive.resolve()
        file_filter = ObservationFileFilter(
            settings.file_filters.allowed_patterns,
            settings.file_filters.forbidden_patterns
        )
        scanner = FastAcquisition1To3GHzFileScanner(file_filter)

        self.stdout.write(self.style.WARNING(f"Scanning directory: {scan_dir} ..."))

        found_files = list(scanner.scan(scan_dir))

        if not found_files:
            self.stdout.write(self.style.SUCCESS("No matching .bin files found."))
            return

        added_count = 0
        error_count = 0
        self.stdout.write(f"Found {len(found_files)} files. Inserting into Database...")

        for file_path in found_files:
            try:
                resolved_file_path = file_path.resolve()
                parent_dir = resolved_file_path.parent  # Директория без имени файла

                if not parent_dir.is_relative_to(raw_base_path):
                    self.stderr.write(self.style.ERROR(
                        f"Skip {resolved_file_path.name}: Outside base archive ({raw_base_path})"
                    ))
                    error_count += 1
                    continue

                relative_dir_str = parent_dir.relative_to(raw_base_path).as_posix()
                if relative_dir_str == ".":
                    relative_dir_str = ""

                parsed = FastAcquisition1To3GHzFilenameParser.parse(resolved_file_path.name)
                _, created = RawObservationFastAcquisition1To3GHz.objects.get_or_create(
                            bin_filename=file_path.name,
                            defaults={
                                'relative_path': relative_dir_str,
                                'datetime_obs_utc': parsed.datetime_utc,
                                'object_of_observation': parsed.object_of_observation,
                                'azimuth': parsed.azimuth
                            }
                        )
                if created: added_count += 1
            except Exception as e:
                error_count += 1
                self.stderr.write(self.style.ERROR(f"Error saving {file_path.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Done! Added to DB: {added_count}. Errors: {error_count}."))