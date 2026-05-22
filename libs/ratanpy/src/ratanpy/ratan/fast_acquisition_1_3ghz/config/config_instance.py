from importlib.resources import files

from ratanpy.ratan.fast_acquisition_1_3ghz.config.fast_acquisition_1_3ghz_configuration import \
    FastAcquisition1To3GHzConfiguration


def _load_default_config() -> FastAcquisition1To3GHzConfiguration:
    config_path = (
        files('ratanpy.ratan.fast_acquisition_1_3ghz.config')
        / 'fast_acquisition_1_3ghz_config.toml'
    )
    return FastAcquisition1To3GHzConfiguration.load(config_path)

config = _load_default_config()