import sys
import tomllib
from functools import cache
from pathlib import Path
from pydantic import Field, BaseModel, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

CURRENT_DIR = Path(__file__).resolve().parent
ENV_FILE = CURRENT_DIR.parent.parent.parent.parent / '.env'
TOML_FILE = CURRENT_DIR / 'fast_acquisition_1_3ghz.toml'


class ResourceSettings(BaseModel):
    worker_max_ram_gb: float
    min_free_ram_gb: float

class FileFilterSettings(BaseModel):
    allowed_patterns: list[str]
    forbidden_patterns: list[str]

class FastAcquisition1To3GHzSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        extra='ignore'
    )

    log_dir: Path = Field(alias='DJANGO_API_LOG_DIR')

    bin_archive: Path = Field(alias='FAST_ACQ_1_3GHZ_BIN_ARCHIVE')
    fits_archive: Path = Field(alias='FAST_ACQ_1_3GHZ_FITS_ARCHIVE')
    fast_acq_1_3ghz_json_data: Path = Field(alias='FAST_ACQ_1_3GHZ_JSON_DATA')

    worker_max_ram_gb: float = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_WORKER_MAX_RAM_GB')
    min_free_ram_gb: float = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_MIN_FREE_RAM_GB')
    monitoring_days: int = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_NUM_LAST_DAYS_MONITORING')

    resources: ResourceSettings = None
    file_filters: FileFilterSettings = None

    @classmethod
    @cache  # кэширование
    def load(cls) -> 'FastAcquisition1To3GHzSettings':
        toml_file = TOML_FILE

        if not toml_file.is_file():
            sys.stderr.write(f"CRITICAL INIT ERROR: Config TOML '{toml_file}' not found")
            sys.exit(1)

        try:
            dynamic_kwargs: dict = {}
            settings = cls(**dynamic_kwargs)
            with open(toml_file, "rb") as f:
                toml_data = tomllib.load(f)

            settings.resources = ResourceSettings(
                worker_max_ram_gb=settings.worker_max_ram_gb,
                min_free_ram_gb=settings.min_free_ram_gb
            )
            settings.file_filters = FileFilterSettings(**toml_data['file_filters'])

            return settings

        except ValidationError as e:
            sys.stderr.write("CRITICAL SETTINGS ERROR: Missing or invalid environment variables")
            for err in e.errors():
                sys.stderr.write(f" - Field: {err['loc'][0]} | Error: {err['msg']}")
            sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"CRITICAL INIT ERROR: {e}")
            sys.exit(1)