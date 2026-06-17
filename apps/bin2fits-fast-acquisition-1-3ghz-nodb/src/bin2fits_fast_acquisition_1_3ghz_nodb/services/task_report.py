from dataclasses import dataclass, field
from typing import List

from ratanpy.ratan.fast_acquisition_1_3ghz.bin2fits.domain import ProcessingResult, ProcessingStatus


@dataclass
class TaskReport:
    total_requested: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    failed_details: List[ProcessingResult] = field(default_factory=list)
    skipped_details: List[ProcessingResult] = field(default_factory=list)
    total_time_sec: float = 0.0
    global_peak_memory_mb: float = 0.0
    formatted_time: str = "0m 0s"

    def update(self, res: ProcessingResult):
        self.global_peak_memory_mb = max(self.global_peak_memory_mb, res.peak_memory_mb)

        if res.status == ProcessingStatus.SKIPPED:
            self.skipped += 1
            self.skipped_details.append(res)
        elif res.status == ProcessingStatus.SUCCESS:
            self.success += 1
        else:
            self.failed += 1
            self.failed_details.append(res)