import tomllib
from importlib import metadata
from pathlib import Path


class RatanpyMeta:
    """
    Класс для получения метаданных библиотеки ratanpy.
    """
    _PACKAGE_NAME = "ratanpy"

    @classmethod
    def get_version(cls) -> str:
        # способ 1
        try:
            return metadata.version(cls._PACKAGE_NAME)
        except metadata.PackageNotFoundError:
            pass

        # способ 2 по pyproject.toml
        toml_path = cls._find_lib_pyproject_toml()
        if toml_path:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "unknown")

        return "unknown"

    @classmethod
    def get_name(cls) -> str:
        return cls._PACKAGE_NAME

    @classmethod
    def _find_lib_pyproject_toml(cls) -> Path | None:
        current = Path(__file__).resolve().parent

        for _ in range(5): # максимум на 5 уровней вверх
            candidate = current / "pyproject.toml"
            if candidate.exists():
                with open(candidate, "rb") as f:
                    data = tomllib.load(f)
                    if data.get("project", {}).get("name") == cls._PACKAGE_NAME:
                        return candidate
            current = current.parent

        return None