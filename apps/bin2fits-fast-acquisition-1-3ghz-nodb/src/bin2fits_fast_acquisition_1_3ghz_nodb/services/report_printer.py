import logging

from bin2fits_fast_acquisition_1_3ghz_nodb.services.task_report import TaskReport


logger = logging.getLogger(__name__)

class ReportPrinter:
    @staticmethod
    def print(report: TaskReport):
        logger.info("Processing task finished")
        logger.info("=== Summary report ===")
        logger.info(f"Total files requested : {report.total_requested}")
        logger.info(f"SUCCESS               : {report.success}")
        logger.info(f"FAILED                : {report.failed}")
        logger.info(f"SKIPPED               : {report.skipped}")

        if report.failed > 0:
            logger.info("--- FAILED FILES LIST ---")
            for res in report.failed_details:
                logger.info(f"[{res.bin_file.name}] status: FAILED")
            logger.info("-------------------------")

        if report.skipped > 0 and logger.isEnabledFor(logging.DEBUG):
            logger.debug("--- SKIPPED FILES LIST ---")
            for res in report.skipped_details:
                logger.debug(f"[{res.bin_file.name}] status: SKIPPED (File already exists)")
            logger.debug("-------------------------")

        logger.info(f"Total Task Time         : {report.formatted_time}")
        logger.info(f"Peak RAM used by Worker : {report.global_peak_memory_mb:.1f} MB")
        logger.info("=== End report ===")