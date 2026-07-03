import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Generator

from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.observation_file_filter import ObservationFileFilter

logger = logging.getLogger(__name__)


class FastAcquisition1To3GHzFileScanner:

    def __init__(self, file_filter: ObservationFileFilter):
        self._file_filter = file_filter

    def _extract_datetime_from_filename(self, filename: str) -> Optional[datetime]:
        """
        Парсит дату и время из имени файла (например: 2025-09-01_121336_sun+00.bin.gz)
        """
        match = re.search(r"(\d{4}-\d{2}-\d{2}_\d{6})", filename)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d_%H%M%S")
            except ValueError:
                return None
        return None

    def scan(self,
             base_dir: Path,
             start_dt: Optional[datetime] = None,
             end_dt: Optional[datetime] = None,
             target_year: Optional[int] = None,
             target_month: Optional[int] = None,
             target_day: Optional[int] = None) -> Generator[Path, None, None]:

        logger.debug(f"Base dir: {base_dir} (Exists: {base_dir.exists()})")
        logger.debug(f"Args: start={start_dt}, end={end_dt}, Y={target_year}, M={target_month}, D={target_day}")

        # формирование директорий для поиска
        date_folders = []

        if target_year and not target_month:
            date_folders.append(str(target_year))
        elif target_year and target_month:
            date_folders.append(f"{target_year}/{target_month:02d}")
        elif start_dt and end_dt:
            curr_y, curr_m = start_dt.year, start_dt.month
            end_y, end_m = end_dt.year, end_dt.month

            while (curr_y < end_y) or (curr_y == end_y and curr_m <= end_m):
                date_folders.append(f"{curr_y}/{curr_m:02d}")
                curr_m += 1
                if curr_m > 12:
                    curr_m, curr_y = 1, curr_y + 1

        logger.debug(f"Generated date folders: {date_folders}")

        target_dirs = []

        if not date_folders:
            target_dirs.append(base_dir)
        else:
            for suffix in date_folders:
                pattern = f"**/{suffix}" # ** на любой глубине
                logger.debug(f"Searching with glob pattern: {pattern}")
                for matched_dir in base_dir.glob(pattern):
                    if matched_dir.is_dir():
                        target_dirs.append(matched_dir)
                        logger.debug(f"Found matching directory: {matched_dir}")

        if not target_dirs:
            logger.debug("No directories matched the pattern")
            return

        # сканирование
        _year = int(target_year) if target_year is not None else None
        _month = int(target_month) if target_month is not None else None
        _day = int(target_day) if target_day is not None else None

        _start = start_dt.replace(tzinfo=None) if start_dt and start_dt.tzinfo else start_dt
        _end = end_dt.replace(tzinfo=None) if end_dt and end_dt.tzinfo else end_dt

        for target_dir in target_dirs:
            for file_path in target_dir.rglob("*"):

                if not file_path.is_file():
                    continue

                if not self._file_filter.is_valid(file_path):
                    continue

                file_dateobs = self._extract_datetime_from_filename(file_path.name)
                if not file_dateobs:
                    logger.error(f"[{file_path.name}] Cannot extract datetime, skipping")
                    continue

                # фильтрация по параметрам времени
                if _year and file_dateobs.year != _year: continue
                if _month and file_dateobs.month != _month: continue
                if _day and file_dateobs.day != _day: continue

                if _start or _end:
                    compare_dt = file_dateobs.replace(tzinfo=None) if file_dateobs.tzinfo else file_dateobs

                    if _start and compare_dt < _start: continue
                    if _end and compare_dt > _end: continue

                yield file_path