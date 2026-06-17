import argparse
import logging
import sys
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class CliParser:
    """
        Console parsing
        bin2fits_fast_1_3 --help
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="bin2fits_fast_1_3",
            description="Observation Conversion Utility from .bin to .fits for Fast Acquisition 1-3GHz"
        )
        self._setup_arguments()

    def _setup_arguments(self):
        p = self.parser
        p.add_argument("--file", type=str, help="Convert chosen .bin file")

        p.add_argument("--overwrite", action="store_true", help="Overwrite .fits file")

        p.add_argument("--bin-dir", type=str, help="directory for .bin files. Default: project settings")
        p.add_argument("--fits-dir", type=str, help="directory for .fits files. Default: project settings")

        p.add_argument("--start-date", type=str, help="Starting date, format: YYYYMMDD or YYYYMMDD_HHMMSS")
        p.add_argument("--end-date", type=str, help="Ending date, format: YYYYMMDD or YYYYMMDD_HHMMSS")
        p.add_argument("--day", type=str, help="Convert for specific day, format: YYYYMMDD")
        p.add_argument("--month", type=str, help="Convert for specific month, format: YYYYMM")
        p.add_argument("--year", type=str, help="Convert for specific year, format: YYYY")

        p.add_argument("--workers", type=int, default=1, help="Number of parallel processes. Default: 1 (sequential). Use >1 for multi-processing")

    def parse(self) -> argparse.Namespace:
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(0)
        return self.parser.parse_args()

    @staticmethod
    def parse_cli_date(date_str: Optional[str]) -> Optional[datetime]:
        """ Конвертирует строку из консоли в объект datetime """
        if not date_str:
            return None
        try:
            if len(date_str) == 8:
                return datetime.strptime(date_str, "%Y%m%d")
            elif len(date_str) == 15:
                return datetime.strptime(date_str, "%Y%m%d_%H%M%S")
            else:
                raise ValueError
        except ValueError:
            logger.critical(f"Format error: '{date_str}'. Expected YYYYMMDD or YYYYMMDD_HHMMSS")
            sys.exit(1)