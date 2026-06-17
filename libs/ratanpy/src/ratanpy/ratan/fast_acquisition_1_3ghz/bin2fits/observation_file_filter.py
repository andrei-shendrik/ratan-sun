import logging
import re
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class ObservationFileFilter:
    """
    Фильтр имен файлов, которые подлежат обработке bin2fits
    """
    def __init__(self, allowed_patterns: List[str], forbidden_patterns: List[str]):
        self._allowed_patterns = [re.compile(p) for p in allowed_patterns]
        self._forbidden_patterns = [re.compile(p) for p in forbidden_patterns]

    def is_valid(self, file_path: Path) -> bool:
        filename = file_path.name

        if not (filename.endswith('.bin') or filename.endswith('.bin.gz')):
            return False

        for pattern in self._forbidden_patterns:
            if pattern.search(filename):
                logger.debug(f"[{filename}] Filtered out: matches forbidden pattern '{pattern.pattern}'")
                return False

        for pattern in self._allowed_patterns:
            if pattern.match(filename):
                return True

        logger.debug(f"[{filename}] Filtered out: does not match any allowed pattern.")
        return False