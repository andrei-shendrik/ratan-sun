import logging
import sys
from datetime import datetime
from pathlib import Path

from bin2fits_fast_acquisition_1_3ghz_nodb.cli.cli_parser import CliParser
from bin2fits_fast_acquisition_1_3ghz_nodb.services.batch_processor import BatchProcessor
from bin2fits_fast_acquisition_1_3ghz_nodb.services.report_printer import ReportPrinter
from bin2fits_fast_acquisition_1_3ghz_nodb.services.task_report import TaskReport
from bin2fits_fast_acquisition_1_3ghz_nodb.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    Bin2FitsFastAcquisition1To3GHzSettings
from ratanpy.logging_conf.logger_configurator import LoggerConfigurator
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.domain import ProcessingResult, ProcessingStatus
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.observation_file_filter import ObservationFileFilter
from ratanpy.ratan.fast_acquisition_1_3ghz.fast_acquisition_1_3ghz_file_scanner import FastAcquisition1To3GHzFileScanner

logger = logging.getLogger(__name__)

class Bin2FitsFastAcquisition1To3GHzApp:

    def __init__(self, env_path: Path, toml_path: Path):
        try:
            self._settings = Bin2FitsFastAcquisition1To3GHzSettings.load(env_path=env_path, toml_path=toml_path)
        except Exception as e:
            print(f"CRITICAL INIT ERROR: {e}")
            sys.exit(1)

        # конфигурация логгера из настроек
        configurator = LoggerConfigurator(self._settings.logging)
        configurator.configure(is_worker=False)

    def get_output_fits_pathfilename(self, bin_file: Path, fits_base_dir: Path) -> Path:
        bin_archive = self._settings.bin_archive.resolve()
        filename = bin_file.name

        if filename.endswith('.bin.gz'):
            fits_filename = filename.replace('.bin.gz', '.fits').lower()
        else:
            fits_filename = bin_file.with_suffix('.fits').name.lower()

        if bin_file.is_relative_to(bin_archive):
            year_month = bin_file.parent.relative_to(bin_archive)
            output_fits_dir = fits_base_dir / year_month
        else:
            output_fits_dir = fits_base_dir

        output_fits_dir.mkdir(parents=True, exist_ok=True)
        return output_fits_dir / fits_filename

    def run(self):
        cli_parser = CliParser()
        args = cli_parser.parse()

        bin_dir = Path(args.bin_dir) if args.bin_dir else self._settings.bin_archive
        fits_dir = Path(args.fits_dir) if args.fits_dir else self._settings.fits_archive

        # формирование списка файлов
        all_found_files = []
        if args.file:
            # если указан конкретный файл
            all_found_files.append(Path(args.file))
        else:
            file_filter = ObservationFileFilter(
                allowed_patterns=self._settings.file_filters.allowed_patterns,
                forbidden_patterns=self._settings.file_filters.forbidden_patterns
            )

            # перевод флагов
            start_dt = CliParser.parse_cli_date(args.start_date)
            end_dt = CliParser.parse_cli_date(args.end_date)
            if start_dt and not end_dt:
                end_dt = datetime.now()

            t_year = args.year
            t_month = int(args.month[4:]) if args.month else None
            if args.month and not t_year:
                t_year = int(args.month[:4])

            t_day = int(args.day[6:]) if args.day else None
            if args.day and not t_year:
                t_year = int(args.day[:4])
                t_month = int(args.day[4:6])

            # сканирование
            scanner = FastAcquisition1To3GHzFileScanner(file_filter)
            all_found_files = list(scanner.scan(
                base_dir=bin_dir,
                start_dt=start_dt,
                end_dt=end_dt,
                target_year=t_year,
                target_month=t_month,
                target_day=t_day
            ))

            if not all_found_files:
                logger.info("No files matching the criteria were found")
                return

            report = TaskReport(total_requested=len(all_found_files))
            files_to_process = []

            for bin_file in all_found_files:
                out_fits = self.get_output_fits_pathfilename(bin_file, fits_dir)
                if out_fits.exists() and not args.overwrite:
                    logger.debug(f"[{bin_file.name}] processing not needed: FITS file already exists")
                    skipped_res = ProcessingResult(bin_file, out_fits, ProcessingStatus.SKIPPED, 0.0, 0.0)
                    report.update(skipped_res)
                else:
                    files_to_process.append(bin_file)

            num_files_to_process = len(files_to_process)

            if num_files_to_process == 0:
                logger.info("No files require processing")
                ReportPrinter.print(report)
                return

            # подсчет воркеров
            workers_count = args.workers if args.workers is not None else 1
            active_workers = min(workers_count, num_files_to_process)
            is_multi_processing = active_workers > 1

            mode = f"parallel ({active_workers} workers)" if is_multi_processing else "single-processing (1 worker)"
            logger.info(f"Starting processing of {num_files_to_process} files in {mode} mode...")

            # запуск пакетной обработки
            processor = BatchProcessor(self._settings)
            report = processor.run(files_to_process, fits_dir, active_workers, args.overwrite, report)

            # отчет
            ReportPrinter.print(report)
