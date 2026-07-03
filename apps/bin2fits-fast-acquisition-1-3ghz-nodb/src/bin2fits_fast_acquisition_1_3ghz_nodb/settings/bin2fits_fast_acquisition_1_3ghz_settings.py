import os
import sys
import tomllib
from pathlib import Path

from dotenv import dotenv_values
from pydantic import BaseModel, Field, ValidationError

from ratanpy.logging_conf.logging_settings import LoggingSettings

class ResourceSettings(BaseModel):
    worker_max_ram_gb: float
    min_free_ram_gb: float

class FileFilterSettings(BaseModel):
    allowed_patterns: list[str]
    forbidden_patterns: list[str]

class EnvModels(BaseModel):
    log_dir: Path = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_NODB_LOG_DIR')
    log_level: str = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_NODB_LOG_LEVEL')
    console_output: bool = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_NODB_CONSOLE_OUTPUT')

    worker_max_ram_gb: float = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_NODB_WORKER_MAX_RAM_GB')
    min_free_ram_gb: float = Field(alias='BIN2FITS_FAST_ACQ_1_3GHZ_NODB_MIN_FREE_RAM_GB')

    bin_archive: Path = Field(alias='FAST_ACQ_1_3GHZ_BIN_ARCHIVE')
    fits_archive: Path = Field(alias='FAST_ACQ_1_3GHZ_FITS_ARCHIVE')

class Bin2FitsFastAcquisition1To3GHzSettings(BaseModel):
    bin_archive: Path
    fits_archive: Path
    resources: ResourceSettings
    file_filters: FileFilterSettings
    logging: LoggingSettings

    @classmethod
    def load(cls, env_path: Path, toml_path: Path) -> 'Bin2FitsFastAcquisition1To3GHzSettings':
        if not toml_path.is_file():
            raise FileNotFoundError(f"CRITICAL: TOML config '{toml_path}' not found")

        # env_dict = dotenv_values(env_path)
        # env = EnvModels(**env_dict)
        file_env_dict = dotenv_values(env_path) if env_path and env_path.is_file() else {}
        merged_env = {**file_env_dict, **os.environ}

        try:
            env = EnvModels(**merged_env)

            with toml_path.open("rb") as f:
                toml_data = tomllib.load(f)

            return cls(
                bin_archive=env.bin_archive,
                fits_archive=env.fits_archive,
                resources=ResourceSettings(
                    worker_max_ram_gb=env.worker_max_ram_gb,
                    min_free_ram_gb=env.min_free_ram_gb
                ),
                file_filters=FileFilterSettings(**toml_data['file_filters']),
                logging=LoggingSettings(
                    base_dir=env.log_dir,
                    log_level=env.log_level,
                    console_output=env.console_output,
                    **toml_data['logging']
                )
            )
        except ValidationError as e:
            print("Critical settings error: missing or invalid environment variables")
            if not env_path.is_file() and not os.environ.get("BIN2FITS_FAST_ACQ_1_3GHZ_NODB_LOG_DIR"):
                print(f".env file was not found at '{env_path}' and OS environment variables are missing.")
            print("Details:")
            for err in e.errors():
                print(f" - Field: {err['loc'][0]} | Error: {err['msg']}")
            print("=" * 50 + "\n")
            sys.exit(1)