import logging
from pathlib import Path

import sys

from dotenv import load_dotenv

from bin2fits_fast_acquisition_1_3ghz.bin2fits_fast_acquisition_1_3ghz_app import Bin2FitsFastAcquisitionApp
from bin2fits_fast_acquisition_1_3ghz.cli.cli_parser import CliParser
from bin2fits_fast_acquisition_1_3ghz.infrastructure.database import init_db
from bin2fits_fast_acquisition_1_3ghz.settings.bin2fits_fast_acquisition_1_3ghz_settings import \
    Bin2FitsFastAcquisition1To3GHzSettings
from ratanpy.logging_conf.logger_configurator import LoggerConfigurator

CURRENT_DIR = Path(__file__).resolve().parent
APP_ROOT = CURRENT_DIR.parent.parent
APP_CONF_TOML = APP_ROOT / "config" / "bin2fits_fast_1_3_app.toml"

logger = logging.getLogger(__name__)

def init_environment():
    """
    Инициализирует переменные окружения.
    Для docker это не делает ничего (переменные уже в памяти).
    Для локального запуска (PyCharm) находит .env и загружает его.
    """
    load_dotenv(dotenv_path=APP_ROOT.parents[1] / ".env")

#@time_counter
def main():
    # init settings
    try:
        init_environment()

        if not APP_CONF_TOML.is_file():
            logger.critical(f"App config TOML not found at {APP_CONF_TOML}")
            sys.exit(1)

    except Exception as e:
        logger.critical(f"Error:\n{e}")
        sys.exit(1)

    app_settings = Bin2FitsFastAcquisition1To3GHzSettings.load(
        toml_path=APP_CONF_TOML
    )

    # logging_conf
    configurator = LoggerConfigurator(app_settings.logging_settings)
    configurator.configure()

    # database initialization
    init_db(app_settings.database_settings.db_url)

    # test DB
    log_level = app_settings.logging_settings.log_level
    if log_level == "DEBUG":
        # check_db(app_settings)
        from bin2fits_fast_acquisition_1_3ghz.scripts.check_db import check_database, show_processing_files, \
            show_failed_files

        check_database(app_settings)  # Покажет сколько всего записей
        show_processing_files(app_settings)  # Покажет, есть ли сейчас активные/зависшие процессы
        show_failed_files(app_settings)  # Покажет, на чем падали последние конвертации

    # console parser
    cli_parser = CliParser()
    args = cli_parser.parse()

    # start app
    app = Bin2FitsFastAcquisitionApp(app_settings)
    try:
        if args.daemon:
            app.run_daemon()
        else:
            app.run_cli_batch(args)
    except KeyboardInterrupt:
        logger.info("Ctrl+C: Canceled by user")

def print_settings_info(app_settings: Bin2FitsFastAcquisition1To3GHzSettings):
    logger.debug("debug message")
    logger.debug(f"Logger level: {app_settings.logging_settings.log_level}")
    logger.debug(f"Log dir: {app_settings.logging_settings.base_dir}")
    logger.debug(f"Fits archive: {app_settings.fits_archive}")

if __name__ == "__main__":
    main()