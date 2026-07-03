import os
import sys
import tomllib
from functools import cache
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel, ValidationError, Field

CURRENT_DIR = Path(__file__).resolve().parent
ENV_FILE = CURRENT_DIR.parent.parent.parent.parent.parent / '.env'
TOML_FILE = CURRENT_DIR / 'fast_acquisition_1_3ghz.toml'


class ResourceSettings(BaseModel):
    worker_max_ram_gb: float
    min_free_ram_gb: float

class FileFilterSettings(BaseModel):
    allowed_patterns: list[str]
    forbidden_patterns: list[str]

# только для валидации
class EnvConfig(BaseModel):
    log_dir: Path = Field(alias='BACKEND_LOG_DIR')
    log_level: str = Field(alias='BACKEND_LOG_LEVEL')
    bin_archive: Path = Field(alias='FAST_ACQ_1_3GHZ_BIN_ARCHIVE')
    fits_archive: Path = Field(alias='FAST_ACQ_1_3GHZ_FITS_ARCHIVE')
    json_archive: Path = Field(alias='FAST_ACQ_1_3GHZ_JSON_DATA')

    worker_max_ram_gb: float = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_WORKER_MAX_RAM_GB')
    min_free_ram_gb: float = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_MIN_FREE_RAM_GB')
    monitoring_days: int = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_NUM_LAST_DAYS_MONITORING')


class FastAcquisition1To3GHzSettings(BaseModel):
    log_dir: Path
    log_level: str
    bin_archive: Path
    fits_archive: Path
    json_archive: Path
    worker_max_ram_gb: float
    min_free_ram_gb: float
    monitoring_days: int

    resources: ResourceSettings
    file_filters: FileFilterSettings

    @classmethod
    @cache
    def load(cls) -> FastAcquisition1To3GHzSettings | None:
        if not TOML_FILE.is_file():
            sys.stderr.write(f"CRITICAL INIT ERROR: Config TOML not found at '{TOML_FILE}'\n")
            sys.exit(1)

        # если файла .env нет (например, в docker), вернется пустой словарь
        file_env_dict = dotenv_values(ENV_FILE) if ENV_FILE.is_file() else {}

        merged_env = {**file_env_dict, **os.environ}

        try:
            # валидация
            env = EnvConfig(**merged_env)

            with open(TOML_FILE, "rb") as f:
                toml_data = tomllib.load(f)

            filters = FileFilterSettings(**toml_data.get('file_filters', {}))

            return cls(
                log_dir=env.log_dir,
                log_level=env.log_level,
                bin_archive=env.bin_archive,
                fits_archive=env.fits_archive,
                json_archive=env.json_archive,
                worker_max_ram_gb=env.worker_max_ram_gb,
                min_free_ram_gb=env.min_free_ram_gb,
                monitoring_days=env.monitoring_days,
                resources=ResourceSettings(
                    worker_max_ram_gb=env.worker_max_ram_gb,
                    min_free_ram_gb=env.min_free_ram_gb
                ),
                file_filters=filters
            )
        except ValidationError as e:
            sys.stderr.write("\nCRITICAL SETTINGS ERROR: Missing or invalid configuration\n")
            # if not ENV_FILE.is_file():
            #     sys.stderr.write(f"WARNING: .env file not found at '{ENV_FILE}'. Relying entirely on OS variables.\n")
            sys.stderr.write("Details:\n")
            for err in e.errors():
                sys.stderr.write(f" - Field: {err['loc'][0]} | Error: {err['msg']}\n")
            # sys.exit(1)
        except Exception as e:
            sys.stderr.write(f"\nCRITICAL INIT ERROR: {e}\n")
            # sys.exit(1)