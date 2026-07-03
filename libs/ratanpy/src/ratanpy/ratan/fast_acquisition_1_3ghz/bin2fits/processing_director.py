from abc import ABC, abstractmethod
from pathlib import Path


class ProcessingDirector(ABC):
    """
    Интерфейс
    """
    @abstractmethod
    def execute(self, bin_file: Path, output_fits_file: Path, overwrite: bool) -> None:
        pass