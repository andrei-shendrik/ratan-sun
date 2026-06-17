from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ProcessingStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ProcessingResult:
    bin_file: Path
    fits_file: Optional[Path]
    status: ProcessingStatus
    time_taken_sec: float
    peak_memory_mb: float
    error_message: Optional[str] = None
    log_records: list = field(default_factory=list)