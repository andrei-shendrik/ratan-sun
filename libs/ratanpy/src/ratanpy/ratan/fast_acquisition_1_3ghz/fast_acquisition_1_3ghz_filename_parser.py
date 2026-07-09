import logging
import re
import zoneinfo
from dataclasses import dataclass
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

@dataclass
class ParsedFilename:
    datetime_utc: datetime
    datetime_local: datetime
    object_of_observation: str
    azimuth: float

class FastAcquisition1To3GHzFilenameParser:
    LOCAL_TZ = zoneinfo.ZoneInfo("Europe/Moscow")

    @classmethod
    def parse(cls, filename: str) -> ParsedFilename:
        pattern = re.compile(r"^(\d{4}-\d{2}-\d{2}_\d{6})_([a-zA-Z]+)([+-]\d+)\.bin.gz")
        match = pattern.search(filename)

        if not match:
            raise ValueError(f"Filename '{filename}' does not match required pattern.")

        dt_str, object_of_observation, az_str = match.groups()

        dt_naive = datetime.strptime(dt_str, "%Y-%m-%d_%H%M%S")
        dt_local = dt_naive.replace(tzinfo=cls.LOCAL_TZ)
        dt_utc = dt_local.astimezone(timezone.utc)

        # dt_local = dt_utc.astimezone(cls.LOCAL_TZ)
        # logger.debug(f"Object: '{object_of_observation}'")

        return ParsedFilename(
            datetime_utc=dt_utc,
            datetime_local=dt_local,
            object_of_observation=object_of_observation.lower(),
            azimuth=float(az_str)
        )