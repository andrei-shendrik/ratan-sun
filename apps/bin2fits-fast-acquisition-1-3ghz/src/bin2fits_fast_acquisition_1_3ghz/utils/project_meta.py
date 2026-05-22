import os
from importlib import metadata


class ProjectInfo:

    _APP_PACKAGE_NAME = "bin2fits_fast_acquisition_1_3ghz"

    @classmethod
    def get_project_version(cls) -> str:
        """
        Возвращает версию проекта. В продакшн она берется из переменной окружения PROJECT_VERSION.
        При локальной разработке возвращает 'dev-local'.
        """
        return os.getenv("PROJECT_VERSION", "dev-local")

    @classmethod
    def get_project_name(cls) -> str:
        return "ratan-sun"

    @classmethod
    def get_app_version(cls) -> str:
        try:
            return metadata.version(cls._APP_PACKAGE_NAME)
        except metadata.PackageNotFoundError:
            return "unknown"