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

        # формирование директорий для поиска
        target_dirs = []
        if target_year and not target_month:
            target_dirs.append(base_dir / str(target_year))
        elif target_year and target_month:
            target_dirs.append(base_dir / str(target_year) / f"{target_month:02d}")
        elif target_year and target_month and target_day:
            target_dirs.append(base_dir / str(target_year) / f"{target_month:02d}")
        elif start_dt and end_dt:
            curr_y, curr_m = start_dt.year, start_dt.month
            end_y, end_m = end_dt.year, end_dt.month

            while (curr_y < end_y) or (curr_y == end_y and curr_m <= end_m):
                target_dirs.append(base_dir / str(curr_y) / f"{curr_m:02d}")
                curr_m += 1
                if curr_m > 12:
                    curr_m, curr_y = 1, curr_y + 1
        else:
            target_dirs.append(base_dir)

        # сканирование
        for target_dir in target_dirs:
            if not target_dir.exists():
                logger.debug(f"Directory not found, skipping: {target_dir}")
                continue

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
                if target_year and file_dateobs.year != target_year: continue
                if target_month and file_dateobs.month != target_month: continue
                if target_day and file_dateobs.day != target_day: continue

                if start_dt and file_dateobs < start_dt: continue
                if end_dt and file_dateobs > end_dt: continue

                yield file_path