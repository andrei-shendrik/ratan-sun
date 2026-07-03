import logging
from pathlib import Path

from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.domain import ProcessingStatus, ProcessingResult
from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.processing_director import ProcessingDirector
from ratanpy.utils.process_profiler import ProcessProfiler

logger = logging.getLogger(__name__)

class FastAcquisition1To3GHzProcessingWrapper:

    def __init__(self, director: ProcessingDirector):
        self._director = director

    def process(self, bin_file: Path, fits_base_dir: Path, overwrite: bool) -> ProcessingResult:

        output_fits_file = FastAcquisition1To3GHzProcessingWrapper._get_output_fits_pathfilename(bin_file, fits_base_dir)

        if output_fits_file.exists() and not overwrite:
            logger.debug(f"[{bin_file.name}] processing not needed: FITS file already exists (use --overwrite)")
            status = ProcessingStatus.SKIPPED
            return ProcessingResult(bin_file, output_fits_file, ProcessingStatus.SKIPPED, 0.0, 0.0)

        output_fits_file.parent.mkdir(parents=True, exist_ok=True)
        error_msg = None
        status = ProcessingStatus.FAILED

        # вызов обработки с замерами ресурсов
        try:
            with ProcessProfiler() as profiler:
                self._director.execute(bin_file, output_fits_file, overwrite)
            status = ProcessingStatus.SUCCESS

        except MemoryError as me:
            error_msg = f"Memory Limit Exceeded: {me}"
            logger.error(f"[{bin_file.name}] {error_msg}")
            if output_fits_file.exists(): output_fits_file.unlink()

        except Exception as e:
            error_msg = str(e)[:500]
            logger.error(f"[{bin_file.name}] Fatal Pipeline Error: {error_msg}", exc_info=True)
            if output_fits_file.exists(): output_fits_file.unlink()

        return ProcessingResult(
            bin_file=bin_file,
            fits_file=output_fits_file if status == ProcessingStatus.SUCCESS else None,
            status=status,
            time_taken_sec=profiler.elapsed_seconds if 'profiler' in locals() else 0.0,
            peak_memory_mb=profiler.peak_memory_mb if 'profiler' in locals() else 0.0,
            error_message=error_msg
        )

    @staticmethod
    def _get_output_fits_pathfilename(bin_file: Path, fits_base_dir: Path) -> Path:

        year, month = bin_file.name[:4], bin_file.name[5:7]
        fits_filename = bin_file.name.replace('.bin.gz', '.fits').replace('.bin', '.fits').lower()
        # todo remove hardcode
        output_fits_file = fits_base_dir / "sun" / year / month / fits_filename

        # if filename.endswith('.bin.gz'):
        #     fits_filename = filename.replace('.bin.gz', '.fits').lower()
        # else:
        #     fits_filename = bin_file.with_suffix('.fits').name.lower()

        # if bin_file.is_relative_to(bin_archive):
        #     year_month = bin_file.parent.relative_to(bin_archive)
        #     output_fits_dir = fits_base_dir / year_month
        # else:
        #     output_fits_dir = fits_base_dir

        # output_fits_dir.mkdir(parents=True, exist_ok=True)
        return output_fits_file